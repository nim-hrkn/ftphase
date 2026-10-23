"""Submit the ftphase T-x WorkChain (stages 01-07) to the AiiDA daemon.

    env/ftphase/bin/python run_aiida.py [--name alli_ace] [--smoke] [--computer mygarden5] [--no-gpu]

Case: ACE Al-Li (AlLi-6gen-18May.yace), Al-rich half x_Li <= 0.5, the same physics as example 5
(fcc random cells, B32 anti-sites, L1_2 Al3Li point phase, calphy liquids 1100 -> 700 K on the GPU).
``--smoke`` shrinks everything (1 fcc cell + 1 liquid, 1000 steps, 2 volumes) to check the chain
in a few minutes.  After ``submit`` nothing depends on this process: the daemon (profile
``ftphase``) runs the calcfunctions, Slurm the CalcJobs.  Follow with

    verdi -p ftphase process status <pk>      # tree of the WorkChain
    verdi -p ftphase process report <pk>      # messages
    python fetch_results.py <pk>              # copy REPORT.md, png, tables to out/<name>/
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POT = os.path.join(ROOT, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace")
LMP_GPU = os.path.join(ROOT, "env/lammps-gpu/bin/lmp_gpu")
POT_AGCU = os.path.join(ROOT, "potentials/agcu/CuAg.eam.alloy")   # Williams, Mishin, Hamilton 2006 (NIST), setfl order Cu Ag


def candidates():
    from ase.build import bulk
    from ase import Atoms
    from ase.spacegroup import crystal

    b32 = crystal(["Al", "Li"], [(0, 0, 0), (0.5, 0.5, 0.5)], spacegroup=227, cellpar=[6.37, 6.37, 6.37, 90, 90, 90])
    l12 = Atoms("LiAl3", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)], cell=[4.0, 4.0, 4.0], pbc=True)
    return {"fcc-Al": (bulk("Al", "fcc", a=4.05, cubic=True), 0.0), "bcc-Li": (bulk("Li", "bcc", a=3.49, cubic=True), 1.0), "B32-AlLi": (b32, 0.5), "L12-Al3Li": (l12, 0.25)}


def candidates_agcu():
    from ase.build import bulk

    return {"fcc-Ag": (bulk("Ag", "fcc", a=4.09, cubic=True), 0.0), "fcc-Cu": (bulk("Cu", "fcc", a=3.615, cubic=True), 1.0)}


def make_spec_agcu(smoke: bool, gpu: bool):
    """Ag-Cu: one fcc solution over the whole range (random 32-atom cells, 2 configurations) + liquid.
    The eutectic and the fcc miscibility gap come out of one fitted fcc curve (ideal + Redlich-Kister)
    and the liquid; solids near T_m use calphy TI (spec['solids_ti']) instead of QHA."""
    xs = [0.0, 1 / 32, 2 / 32, 4 / 32, 8 / 32, 12 / 32, 16 / 32, 20 / 32, 24 / 32, 28 / 32, 30 / 32, 31 / 32, 1.0]
    spec = {
        "elements": ["Ag", "Cu"], "masses": [107.8682, 63.546], "x_element": "Cu", "model": "CuAg.eam.alloy (Williams-Mishin-Hamilton 2006 EAM)",
        "pair_style": "eam/alloy", "pair_coeff": "* * {potential} Ag Cu", "atom_types": {"Ag": 1, "Cu": 2},
        "candidates": {"fcc-Ag": 0.0, "fcc-Cu": 1.0}, "known_ground_states": ["fcc-Ag", "fcc-Cu"],
        "relax": {"fmax": 1e-3, "cell": True},
        "solids": [{"phase": "fcc", "kind": "solution", "base": "fcc-Ag", "repeat": [2, 2, 2], "x": xs, "n_configs": 2, "series": "random", "seed": 0,
                    "supercell": [2, 2, 2], "mesh": 60.0}],
        "solids_ti": {"phases": ["fcc"], "T_sweep": [900.0, 1400.0], "T_hi_by_x": [[0.0, 1360.0], [1.0, 1480.0]], "min_atoms": 2000,   # 256-atom Frenkel-Ladd cells are ~7 meV/atom too low (ti_convergence.py); 4x4x4 of 32 = 2048
                      "n_equilibration_steps": 10000, "n_switching_steps": [10000, 10000], "n_iterations": 1, "mode": "ts"},
        "liquids": {"base": "fcc-Ag", "repeat": [4, 4, 4], "x": [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0], "seed": 100, "T_sweep": [1500.0, 950.0],
                    "T_override": {"0.0": 1050.0, "1.0": 1100.0}, "n_repeats": 1, "n_equilibration_steps": 10000, "n_switching_steps": [10000, 10000],
                    "n_iterations": 3, "mode": "ts", "pressure": 0.0},
        "qha": {"T_max": 1400.0, "T_step": 25.0, "scales": [0.96, 0.98, 1.0, 1.02, 1.04, 1.06, 1.08], "eos": "vinet", "imaginary": "drop",
                "relax": {"do": True, "fmax": 1e-3, "cell": True, "hydrostatic": True}},
        "assemble": {"T_min": 900.0, "T_max": 1400.0, "T_step": 10.0, "fits": {"fcc": "rk", "liquid": "rk"}, "poly_orders": {"fcc": 4, "liquid": 4}, "poly_order": 4,
                     "config_terms": {"fcc": "ideal"}, "sigma": {"fcc": 0.002, "liquid": 0.0014}, "hull": {"min_width": 0.005, "gap_tol": 2.5},
                     "drop_edge_beyond_liquid": False, "sensitivity_samples": 30, "liquid_sigma_floor": 0.0014, "T_residuals": 1100.0,
                     "title": "EAM Ag-Cu (Williams-Mishin-Hamilton 2006), 0 GPa: fcc (calphy TI >= 900 K, QHA below) + calphy liquid [AiiDA]", "xlabel": "x_Cu"},
    }
    if smoke:
        spec["solids"][0].update({"x": [0.0, 0.5, 1.0], "n_configs": 1, "repeat": [1, 1, 1], "supercell": [2, 2, 2], "mesh": [4, 4, 4]})
        spec["solids_ti"].update({"T_sweep": [1000.0, 1100.0], "T_hi_by_x": [[0.0, 1100.0], [1.0, 1100.0]], "min_atoms": 100, "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000]})
        spec["liquids"].update({"x": [0.0, 0.5], "repeat": [3, 3, 3], "T_sweep": [1500.0, 1200.0], "T_override": {}, "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000], "n_iterations": 1})
        spec["qha"].update({"T_step": 100.0, "scales": [0.97, 0.985, 1.0, 1.015, 1.03, 1.05]})
        spec["assemble"].update({"T_min": 1000.0, "T_max": 1400.0, "sensitivity_samples": 5, "title": "smoke test Ag-Cu"})
    return spec


SYSTEMS = {"alli": (lambda: POT, lambda: candidates(), lambda sm, g: make_spec(sm, g), "ACE Al-Li T-x diagram, stages 01-07 with provenance"),
           "agcu": (lambda: POT_AGCU, candidates_agcu, make_spec_agcu, "EAM Ag-Cu T-x diagram (eutectic + fcc miscibility gap), stages 01-07 with provenance")}


def make_spec(smoke: bool, gpu: bool):
    spec = {
        "elements": ["Al", "Li"], "masses": [26.9815, 6.94], "x_element": "Li", "model": "AlLi-6gen-18May.yace (ACE)",
        "pair_style": "pace", "pair_coeff": "* * {potential} Al Li", "atom_types": {"Al": 1, "Li": 2},
        "candidates": {"fcc-Al": 0.0, "bcc-Li": 1.0, "B32-AlLi": 0.5, "L12-Al3Li": 0.25},
        "known_ground_states": ["fcc-Al", "bcc-Li", "B32-AlLi"],
        "relax": {"fmax": 1e-3, "cell": True},
        "solids": [
            {"phase": "fcc", "kind": "solution", "base": "fcc-Al", "repeat": [2, 2, 2], "x": [0.0, 0.0625, 0.125, 0.1875, 0.25], "n_configs": 2, "series": "random", "seed": 0,
             "supercell": [2, 2, 2], "mesh": 60.0},
            {"phase": "Al3Li", "kind": "point", "base": "L12-Al3Li", "x": [0.25], "supercell": [3, 3, 3], "mesh": 60.0},
            {"phase": "B32", "kind": "limited", "base": "B32-AlLi", "antisites": True, "supercell": [2, 2, 2], "mesh": 60.0},
        ],
        "liquids": {"base": "fcc-Al", "repeat": [4, 4, 4], "x": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5], "seed": 100, "T_sweep": [1100.0, 700.0], "T_override": {"0.1": 800.0},
                    "n_repeats": 1, "n_equilibration_steps": 10000, "n_switching_steps": [10000, 10000], "n_iterations": 3, "mode": "ts", "pressure": 0.0},
        "qha": {"T_max": 1100.0, "T_step": 25.0, "scales": [0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05], "eos": "vinet", "imaginary": "drop",
                "relax": {"do": True, "fmax": 1e-3, "cell": True, "hydrostatic": True}},
        "assemble": {"T_min": 700.0, "T_max": 1100.0, "T_step": 10.0, "fits": {"fcc": "poly", "liquid": "poly", "B32": "spline"}, "poly_order": 3,
                     "config_terms": {"fcc": "ideal", "B32": "sublattice:b32_antisite"}, "sigma": {"fcc": 0.002, "B32": 0.002, "Al3Li": 0.002, "liquid": 0.0014},
                     "hull": {"min_width": 0.005, "gap_tol": 2.5}, "drop_edge_beyond_liquid": True, "sensitivity_samples": 30, "liquid_sigma_floor": 0.0014,
                     "title": "ACE Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram]", "xlabel": "x_Li"},
    }
    if smoke:
        spec["solids"] = [{"phase": "fcc", "kind": "solution", "base": "fcc-Al", "repeat": [1, 1, 1], "x": [0.0, 0.25], "n_configs": 1, "series": "random", "seed": 0, "supercell": [2, 2, 2], "mesh": [4, 4, 4]},
                          {"phase": "B32", "kind": "limited", "base": "B32-AlLi", "antisites": True, "supercell": [1, 1, 1], "mesh": [4, 4, 4]}]
        spec["liquids"].update({"x": [0.0, 0.2], "repeat": [3, 3, 3], "n_equilibration_steps": 1000, "n_switching_steps": [1000, 1000], "n_iterations": 1, "T_sweep": [1100.0, 900.0]})
        spec["qha"].update({"T_step": 100.0, "scales": [0.97, 0.99, 1.01, 1.03, 1.05, 1.07]})  # 1100 K needs V0 beyond 1.03^3
        spec["assemble"].update({"T_min": 900.0, "sensitivity_samples": 5, "title": "smoke test"})
    if not gpu:
        spec["liquids"]["cpu"] = True
    return spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", choices=sorted(SYSTEMS), default="alli", help="alli = ACE Al-Li (example 8), agcu = EAM Ag-Cu (example 9)")
    ap.add_argument("--name", default=None, help="run name (default: alli_ace or agcu_eam)")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--computer", default="mygarden5")
    ap.add_argument("--profile", default=os.environ.get("AIIDA_PROFILE", "ftphase"))
    ap.add_argument("--no-gpu", action="store_true", help="run calphy on CPU ranks (default: 1 GPU per liquid)")
    ap.add_argument("--cpu-cores", type=int, default=4, help="LAMMPS ranks per calphy job with --no-gpu")
    ap.add_argument("--qha-cores", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="build the inputs, print them, do not submit")
    a = ap.parse_args()

    from aiida import load_profile, orm
    from aiida.engine import submit
    from aiida.plugins import WorkflowFactory

    load_profile(a.profile)
    gpu = not a.no_gpu
    pot_fn, cand_fn, spec_fn, descr = SYSTEMS[a.system]
    spec = spec_fn(a.smoke, gpu)
    name = (a.name or {"alli": "alli_ace", "agcu": "agcu_eam"}[a.system]) + ("_smoke" if a.smoke else "")
    cands = {"".join(c if c.isalnum() else "_" for c in n): orm.StructureData(ase=at) for n, (at, x) in cand_fn().items()}
    for k, s in cands.items():
        s.label = k
    inputs = {
        "spec": orm.Dict(dict=spec),
        "potential": orm.SinglefileData(file=pot_fn()),
        "candidates": cands,
        "qha_code": orm.load_code(f"ftphase-qha@{a.computer}"),
        "calphy_code": orm.load_code(f"calphy@{a.computer}"),
        "qha_options": orm.Dict(dict={"resources": {"num_machines": 1, "num_mpiprocs_per_machine": 1, "num_cores_per_mpiproc": a.qha_cores}, "max_wallclock_seconds": 24 * 3600,
                                      "queue_name": "debug", "withmpi": False, "custom_scheduler_commands": "#SBATCH --hint=nomultithread"}),
        "calphy_options": orm.Dict(dict={"resources": {"num_machines": 1, "num_mpiprocs_per_machine": 1 if gpu else a.cpu_cores}, "max_wallclock_seconds": 48 * 3600,
                                         "queue_name": "debug", "withmpi": False,
                                         "custom_scheduler_commands": "#SBATCH --hint=nomultithread" + ("\n#SBATCH --gres=gpu:1" if gpu else "")}),
        "calphy_extra": orm.Dict(dict={"gpu": True, "lammps_executable": LMP_GPU} if gpu else {"gpu": False, "cores": a.cpu_cores}),
        "metadata": {"label": f"ftphase txdiagram {name}", "description": descr},
    }
    if a.dry_run:
        print(json.dumps(spec, indent=1)); print({k: (v.get_dict() if isinstance(v, orm.Dict) else type(v).__name__) for k, v in inputs.items() if k != "metadata"})
        return
    node = submit(WorkflowFactory("ftphase.txdiagram"), **inputs)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    rec = {"pk": node.pk, "uuid": node.uuid, "name": name, "profile": a.profile, "submitted": time.strftime("%F %T"), "gpu": gpu, "smoke": a.smoke}
    with open(os.path.join(HERE, "out", f"{name}.pk.json"), "w") as f:
        json.dump(rec, f, indent=1)
    with open(os.path.join(HERE, "out", "submissions.log"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"submitted TxDiagramWorkChain pk={node.pk} uuid={node.uuid} ({name}); follow with: verdi -p {a.profile} process status {node.pk}")


if __name__ == "__main__":
    sys.exit(main())
