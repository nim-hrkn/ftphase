"""TxDiagramWorkChain: stages 01-07 of the ftphase workflow with provenance.

    prepare_cells (calcfunction)  01 relax + hull, 02A solid cells, 02B liquid cells
        -> QhaCalculation x N_solids  (Slurm, CPU)        03A
        -> CalphyCalculation x N_liq  (Slurm, GPU or CPU) 03B      (all in parallel)
    assemble_diagram (calcfunction)  04A/04B/05/06/07 -> summary, REPORT.md, png, tables

Failed cells are skipped (reported); the assembly needs at least one liquid run.
"""

import numpy as np
from aiida import orm
from aiida.engine import WorkChain
from aiida.plugins import CalculationFactory

from ftphase.aiida.functions import assemble_diagram, prepare_cells, repeat_structure

QhaCalculation = CalculationFactory("ftphase.qha")
CalphyCalculation = CalculationFactory("ftphase.calphy")


class TxDiagramWorkChain(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input("spec", valid_type=orm.Dict, help="system description (see ftphase.aiida.functions.prepare_cells / assemble_diagram)")
        spec.input("potential", valid_type=orm.SinglefileData)
        spec.input_namespace("candidates", valid_type=orm.StructureData, dynamic=True, help="0 K candidate structures keyed by spec['candidates'] names (non-alphanumerics -> '_')")
        spec.input("qha_code", valid_type=orm.AbstractCode)
        spec.input("calphy_code", valid_type=orm.AbstractCode)
        spec.input("qha_options", valid_type=orm.Dict, help="metadata.options of the QHA CalcJobs (resources, max_wallclock_seconds, queue_name, ...)")
        spec.input("calphy_options", valid_type=orm.Dict, help="metadata.options of the calphy CalcJobs (add custom_scheduler_commands '#SBATCH --gres=gpu:1' for GPU runs)")
        spec.input("calphy_extra", valid_type=orm.Dict, required=False, help="extra keys merged into every calphy parameters Dict (gpu, lammps_executable, cores, extra)")
        spec.input("skip_liquids", valid_type=orm.Bool, default=lambda: orm.Bool(False))
        spec.outline(cls.prepare, cls.run_calculations, cls.inspect, cls.assemble)
        spec.output("hull", valid_type=orm.Dict)
        spec.output("solid_params", valid_type=orm.Dict)
        spec.output("liquid_params", valid_type=orm.Dict)
        spec.output("summary", valid_type=orm.Dict)
        spec.output("report", valid_type=orm.SinglefileData)
        spec.output("figure", valid_type=orm.SinglefileData)
        spec.output("free_energies", valid_type=orm.SinglefileData)
        spec.output("regions", valid_type=orm.SinglefileData)
        spec.output("invariants", valid_type=orm.SinglefileData)
        spec.output("sensitivity", valid_type=orm.SinglefileData)
        spec.output("fit_residuals", valid_type=orm.SinglefileData)
        spec.exit_code(401, "ERROR_NO_LIQUID", message="no liquid calculation finished; the assembly needs at least one")
        spec.exit_code(402, "ERROR_NO_SOLID", message="no solid QHA finished")
        spec.exit_code(410, "ERROR_ASSEMBLY", message="assemble_diagram raised (see the calcfunction report)")

    def prepare(self):
        res = prepare_cells(self.inputs.spec, self.inputs.potential, **self.inputs.candidates)
        self.ctx.solids = {k[len("solid_"):]: v for k, v in res.items() if k.startswith("solid_") and k != "solid_params"}
        self.ctx.liquids = {k[len("liquid_"):]: v for k, v in res.items() if k.startswith("liquid_") and k != "liquid_params"}
        self.ctx.solid_params = res["solid_params"]
        self.ctx.liquid_params = res["liquid_params"]
        self.out("hull", res["hull"])
        self.out("solid_params", res["solid_params"])
        self.out("liquid_params", res["liquid_params"])
        self.report(f"prepared {len(self.ctx.solids)} solid cells and {len(self.ctx.liquids)} liquid cells; hull check: {res['hull'].get_dict().get('ground_state_check')}")

    def run_calculations(self):
        sp = self.inputs.spec.get_dict()
        qha = sp.get("qha", {})
        Tq = [float(v) for v in __import__("numpy").arange(0.0, float(qha.get("T_max", 1100.0)) + 1e-6, float(qha.get("T_step", 25.0)))]
        sol_p = self.ctx.solid_params.get_dict()
        for key, structure in self.ctx.solids.items():
            m = sol_p[key]
            params = {"pair_style": sp["pair_style"], "pair_coeff": sp["pair_coeff"], "atom_types": sp["atom_types"], "supercell": m["supercell"], "mesh": m["mesh"],
                      "scales": qha.get("scales", [0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05]), "temperatures": Tq, "eos": qha.get("eos", "vinet"),
                      "imaginary": qha.get("imaginary", "drop"), "relax": qha.get("relax", {"do": True, "fmax": 1e-3, "cell": True, "hydrostatic": True}),
                      "pressure_GPa": float(qha.get("pressure_GPa", 0.0))}
            builder = QhaCalculation.get_builder()
            builder.code = self.inputs.qha_code
            builder.structure = structure
            builder.potential = self.inputs.potential
            builder.parameters = orm.Dict(dict=params)
            builder.metadata.options = self.inputs.qha_options.get_dict()
            builder.metadata.label = f"qha {key} {m['phase']} x={m['x']:.4f}"
            self.to_context(**{f"qha_{key}": self.submit(builder)})
        extra = self.inputs.calphy_extra.get_dict() if "calphy_extra" in self.inputs else {}
        # ---- optional calphy TI of the solid cells (anharmonic level near T_m; spec["solids_ti"])
        sti = sp.get("solids_ti")
        self.ctx.sti_keys = []
        if sti:
            for key, structure in self.ctx.solids.items():
                m = sol_p[key]
                if sti.get("phases") and m["phase"] not in sti["phases"]:
                    continue
                T_sw = list(sti.get("T_sweep_by_phase", {}).get(m["phase"], sti.get("T_sweep", [900.0, 1400.0])))
                if sti.get("T_hi_by_x"):   # cap the sweep end per composition, e.g. [[0, 1360], [1, 1480]] (about 1.1 T_m of the pure ends)
                    pts = sorted(sti["T_hi_by_x"])
                    T_sw[1] = float(np.interp(m["x"], [q[0] for q in pts], [q[1] for q in pts]))
                n_rep = max(1, int(np.ceil((float(sti.get("min_atoms", 200)) / m["n_atoms"]) ** (1.0 / 3.0) - 1e-9)))
                big = repeat_structure(structure, orm.Int(n_rep)) if n_rep > 1 else structure
                params = {"name": f"sol_{key}", "folder_prefix": f"sol_{key}", "mode": sti.get("mode", "ts"), "elements": sp["elements"], "masses": sp["masses"],
                          "pair_style": sp["pair_style"], "pair_coeff": sp["pair_coeff"], "temperature": [float(T_sw[0]), float(T_sw[1])] if sti.get("mode", "ts") == "ts" else float(T_sw[0]),
                          "pressure": float(sti.get("pressure", 0.0)), "reference_phase": "solid", "n_equilibration_steps": int(sti.get("n_equilibration_steps", 10000)),
                          "n_switching_steps": sti.get("n_switching_steps", [10000, 10000]), "n_iterations": int(sti.get("n_iterations", 1))}
                params.update(extra)
                builder = CalphyCalculation.get_builder()
                builder.code = self.inputs.calphy_code
                builder.structure = big
                builder.potential = self.inputs.potential
                builder.parameters = orm.Dict(dict=params)
                builder.metadata.options = self.inputs.calphy_options.get_dict()
                builder.metadata.label = f"calphy solid {key} {m['phase']} x={m['x']:.4f} ({len(big.sites)} atoms)"
                self.to_context(**{f"sti_{key}": self.submit(builder)})
                self.ctx.sti_keys.append(key)
        if self.inputs.skip_liquids.value:
            self.report(f"submitted {len(self.ctx.solids)} QHA and {len(self.ctx.sti_keys)} solid TI calculations (liquids skipped)")
            return
        lq = sp.get("liquids", {})
        liq_p = self.ctx.liquid_params.get_dict()
        for key, structure in self.ctx.liquids.items():
            m = liq_p[key]
            params = {"name": m["tag"], "folder_prefix": m["tag"], "mode": m["mode"], "elements": sp["elements"], "masses": sp["masses"], "pair_style": sp["pair_style"],
                      "pair_coeff": sp["pair_coeff"], "temperature": m["temperature"], "pressure": float(lq.get("pressure", 0.0)), "reference_phase": "liquid",
                      "n_equilibration_steps": int(lq.get("n_equilibration_steps", 10000)), "n_switching_steps": lq.get("n_switching_steps", [10000, 10000]),
                      "n_iterations": int(lq.get("n_iterations", 3))}
            params.update(extra)
            builder = CalphyCalculation.get_builder()
            builder.code = self.inputs.calphy_code
            builder.structure = structure
            builder.potential = self.inputs.potential
            builder.parameters = orm.Dict(dict=params)
            builder.metadata.options = self.inputs.calphy_options.get_dict()
            builder.metadata.label = f"calphy {m['tag']} x={m['x_actual']:.4f}"
            self.to_context(**{f"liq_{key}": self.submit(builder)})
        self.report(f"submitted {len(self.ctx.solids)} QHA, {len(self.ctx.sti_keys)} solid TI and {len(self.ctx.liquids)} liquid calphy calculations")

    def inspect(self):
        self.ctx.ok_qha, self.ctx.ok_liq, self.ctx.ok_sti, failed = {}, {}, {}, []
        for key in self.ctx.get("sti_keys", []):
            node = self.ctx[f"sti_{key}"]
            if node.is_finished_ok and "sweep" in node.outputs:
                self.ctx.ok_sti[key] = node.outputs.sweep
            else:
                failed.append(f"sti_{key}<{node.pk}>:{node.exit_status}")
        for key in self.ctx.solids:
            node = self.ctx[f"qha_{key}"]
            if node.is_finished_ok:
                self.ctx.ok_qha[key] = node.outputs.arrays
            else:
                failed.append(f"qha_{key}<{node.pk}>:{node.exit_status}")
        if not self.inputs.skip_liquids.value:
            for key in self.ctx.liquids:
                node = self.ctx[f"liq_{key}"]
                if node.is_finished_ok and "sweep" in node.outputs:
                    self.ctx.ok_liq[key] = node.outputs.sweep
                else:
                    failed.append(f"liq_{key}<{node.pk}>:{node.exit_status}")
        if failed:
            self.report("failed calculations (skipped): " + ", ".join(failed))
        if not self.ctx.ok_qha and not self.ctx.ok_sti:
            return self.exit_codes.ERROR_NO_SOLID
        if not self.ctx.ok_liq:
            return self.exit_codes.ERROR_NO_LIQUID

    def assemble(self):
        nodes = {f"qha_{k}": v for k, v in self.ctx.ok_qha.items()}
        nodes.update({f"liq_{k}": v for k, v in self.ctx.ok_liq.items()})
        nodes.update({f"sti_{k}": v for k, v in self.ctx.ok_sti.items()})
        try:
            res = assemble_diagram(self.inputs.spec, self.ctx.solid_params, self.ctx.liquid_params, **nodes)
        except Exception as exc:  # the calcfunction is recorded as excepted; keep the WorkChain readable
            self.report(f"assembly failed: {exc!r}")
            return self.exit_codes.ERROR_ASSEMBLY
        for label in ("summary", "report", "figure", "free_energies", "regions", "invariants", "sensitivity", "fit_residuals"):
            self.out(label, res[label])
        s = res["summary"].get_dict()
        self.report(f"done: T grid {s.get('T_grid')}, lowest T with liquid {s.get('lowest_T_with_liquid_K')}, invariants {len(s.get('invariants', []))}")
