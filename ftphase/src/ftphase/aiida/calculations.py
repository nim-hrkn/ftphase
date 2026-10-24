"""CalcJobs: stage 03A (phonopy QHA of one cell) and stage 03B (one calphy calculation)."""

import json
import os

from aiida import orm
from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob

from ftphase.structures import write_lammps_data


def _atoms_from(structure: orm.StructureData):
    return structure.get_ase()


class QhaCalculation(CalcJob):
    """Run ``ftphase-qha-run`` (relax + phonopy volume scan + QHA) for one StructureData.

    ``parameters`` keys: ``pair_style``, ``pair_coeff`` (with ``{potential}`` placeholder),
    ``atom_types`` ({element: LAMMPS type}), ``supercell`` (3 ints or 3x3), ``mesh`` (phonopy
    mesh list or a length in Å), ``scales``, ``temperatures`` (list, K), ``eos``, ``imaginary``,
    ``relax`` ({do, fmax, cell, hydrostatic}), ``pressure_GPa``.
    """

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input("structure", valid_type=orm.StructureData, help="relaxed-or-not solid cell (the runner relaxes it when parameters.relax.do)")
        spec.input("potential", valid_type=orm.SinglefileData, help="MLIP / EAM potential file; copied next to the input")
        spec.input("parameters", valid_type=orm.Dict)
        spec.inputs["metadata"]["options"]["resources"].default = {"num_machines": 1, "num_mpiprocs_per_machine": 1, "num_cores_per_mpiproc": 4}
        spec.inputs["metadata"]["options"]["withmpi"].default = False
        spec.inputs["metadata"]["options"]["parser_name"].default = "ftphase.qha"
        spec.output("results", valid_type=orm.Dict, help="scalars and metadata of the QHA run")
        spec.output("arrays", valid_type=orm.ArrayData, help="T, G (eV/atom), V (A^3/atom), hw_eV, weights (0 K volume), volumes, e0, f_vib")
        spec.exit_code(300, "ERROR_MISSING_OUTPUT", message="qha_results.json or qha_arrays.npz was not produced (see stderr)")
        spec.exit_code(310, "ERROR_RUNNER_FAILED", message="the runner reported an exception")

    def prepare_for_submission(self, folder):
        from ase.io import write

        atoms = _atoms_from(self.inputs.structure)
        with folder.open("structure.extxyz", "w") as f:
            write(f, atoms, format="extxyz")
        p = dict(self.inputs.parameters.get_dict())
        pot_name = self.inputs.potential.filename
        inp = {"structure": "structure.extxyz", "potential": pot_name, "pair_style": p.pop("pair_style"), "pair_coeff": p.pop("pair_coeff"),
               "atom_types": p.pop("atom_types"), "parameters": p}
        for k in ("cmdargs", "calculator", "device", "dtype", "modal"):   # optional: Kokkos arguments / torch-based ASE calculators (runners.make_calculator)
            if k in p:
                inp[k] = p.pop(k)
        with folder.open("input.json", "w") as f:
            json.dump(inp, f, indent=1)
        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.cmdline_params = ["input.json"]
        codeinfo.stdout_name = "qha.out"
        codeinfo.stderr_name = "qha.err"
        codeinfo.withmpi = False
        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [(self.inputs.potential.uuid, pot_name, pot_name)]
        calcinfo.retrieve_list = ["qha_results.json", "qha_arrays.npz", "qha.out", "qha.err"]
        return calcinfo


class CalphyCalculation(CalcJob):
    """Run ``calphy_kernel -i input.yaml -k 0`` for one calphy calculation block.

    ``parameters`` keys (see :func:`ftphase.calphy_io.calculation_block`): ``mode`` (fe/ts/...),
    ``elements``, ``masses``, ``pair_style``, ``pair_coeff`` (with ``{potential}``), ``temperature``
    (number or [T_start, T_stop]), ``pressure`` (bar), ``reference_phase``, ``n_equilibration_steps``,
    ``n_switching_steps``, ``n_iterations``, ``cores`` (LAMMPS ranks calphy starts itself), ``gpu``
    (bool; adds KOKKOS cmdargs and ``pace product``), ``lammps_executable`` (path on the compute
    node, needed for ``gpu``), ``folder_prefix``, ``extra`` (dict merged into the block).
    The LAMMPS data file is written from ``structure`` with ``elements`` as the type order.
    Paths are written as ``__WORKDIR__/...`` and substituted with ``$PWD`` on the node.
    """

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input("structure", valid_type=orm.StructureData)
        spec.input("potential", valid_type=orm.SinglefileData)
        spec.input("parameters", valid_type=orm.Dict)
        spec.inputs["metadata"]["options"]["resources"].default = {"num_machines": 1, "num_mpiprocs_per_machine": 1}
        spec.inputs["metadata"]["options"]["withmpi"].default = False
        spec.inputs["metadata"]["options"]["parser_name"].default = "ftphase.calphy"
        spec.output("results", valid_type=orm.Dict, help="report.yaml of the calculation (+ calculation folder name)")
        spec.output("sweep", valid_type=orm.ArrayData, required=False, help="temperature_sweep.dat: temperature (K), free_energy (eV/atom), error (eV/atom)")
        spec.exit_code(300, "ERROR_NO_REPORT", message="no report.yaml was retrieved: the calculation did not finish")
        spec.exit_code(310, "ERROR_PHASE_CHANGED", message="calphy stopped because the phase melted or solidified")
        spec.exit_code(320, "ERROR_NO_SWEEP", message="ts mode finished without temperature_sweep.dat")

    def prepare_for_submission(self, folder):
        import yaml

        from ftphase.calphy_io import calculation_block

        p = dict(self.inputs.parameters.get_dict())
        elements = list(p["elements"])
        atoms = _atoms_from(self.inputs.structure)
        prefix = p.get("folder_prefix") or p.get("name") or "calc"
        data_name = f"{prefix}.data"
        write_lammps_data(atoms, folder.get_abs_path(data_name), elements)
        pot_name = self.inputs.potential.filename
        gpu = bool(p.get("gpu", False))
        cores = int(p.get("cores", self.inputs.metadata.options.resources.get("num_mpiprocs_per_machine", 1)))
        queue = {"scheduler": "local", "cores": 1 if gpu else cores}
        block = calculation_block(
            p.get("name", prefix), p["mode"], elements, list(p["masses"]), f"__WORKDIR__/{data_name}", p["pair_style"],
            p["pair_coeff"].format(potential=f"__WORKDIR__/{pot_name}"), p["temperature"], pressure=float(p.get("pressure", 0.0)),
            reference_phase=p.get("reference_phase", "solid"), n_equilibration_steps=int(p.get("n_equilibration_steps", 10000)),
            n_switching_steps=p.get("n_switching_steps", 25000), n_iterations=int(p.get("n_iterations", 1)), queue=queue,
            folder_prefix=prefix, extra=p.get("extra"), gpu=gpu, n_gpus=int(p.get("n_gpus", 1)), lammps_executable=p.get("lammps_executable"),
            check_executable=False)
        with folder.open("input.yaml", "w") as f:
            yaml.safe_dump({"calculations": [block]}, f, sort_keys=False)
        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.cmdline_params = ["-i", "input.yaml", "-k", "0"]
        codeinfo.stdout_name = "calphy.out"
        codeinfo.stderr_name = "calphy.err"
        codeinfo.withmpi = False
        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.prepend_text = 'sed -i "s|__WORKDIR__|$PWD|g" input.yaml'
        calcinfo.local_copy_list = [(self.inputs.potential.uuid, pot_name, pot_name)]
        calcinfo.retrieve_list = ["calphy.out", "calphy.err", "input.yaml",
                                  ("*/report.yaml", ".", 2), ("*/temperature_sweep.dat", ".", 2), ("*/calphy.log", ".", 2), ("*/metadata.yaml", ".", 2)]
        return calcinfo
