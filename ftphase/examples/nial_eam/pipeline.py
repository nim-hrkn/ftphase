"""Example 7: Ni-Al T-x diagram (0 <= x_Ni <= 1, 900-2000 K) with the Purja Pun & Mishin
2009 EAM potential, as a Slurm chain on the CPU host mygardenx1 (run_pipeline.sh,
run_resume.sh).  Structure follows examples/alli_ace_txdiagram/pipeline_full.py.

Why Ni-Al: B2 NiAl has a wide homogeneity range (about 45-60 at.% Ni) with the
triple-defect constitution (Ni anti-sites on the Ni-rich side, Ni vacancies on
the Al-rich side), L1_2 Ni3Al a narrow one by anti-sites.  This is the test of
workflow stages 02A/04A for ordered phases with composition width
(anti-site AND vacancy sublattice models, eq. (E10)-(E12)).

Phases and cells (x = Ni fraction of all atoms)
  fcc(Al)   64-atom SQS, x = 0, 1/64, 2/64                       ideal mixing
  fcc(Ni)   64-atom SQS, x = 1, 0.9375, 0.875, 0.8125, 0.75      ideal mixing
  B2 NiAl   54-atom 3x3x3: stoichiometric; 1, 2 Ni anti-sites (x = 28/54, 29/54);
            1, 2 Ni vacancies (x = 26/53, 25/52)                  triple-defect sublattice model
  L1_2 Ni3Al 108-atom 3x3x3: stoichiometric; 1 anti-site each way (x = 80/108, 82/108)
                                                                  two-sublattice anti-site model
  Ni2Al3 (P-3m1), NiAl3 (Pnma, cementite-type guess)             point phases (this EAM puts them
                                                                  60-120 meV/atom above the hull: reported)
  liquid    256-atom cells, x = 0 .. 1 step 0.1, calphy ts 2000 K -> T_stop(x), UFM, 3 iterations,
            N_REPEAT extra runs with new seeds for the run-to-run error
Solids: phonopy QHA, 2x2x2 supercells, volume scan 0.97-1.09 (fcc Ni expands ~4 % to 2000 K),
quantum QHA lowered to the classical level with F_q - F_cl (04B).

Experiment for comparison (Massalski): eutectic L -> (Al) + NiAl3 at 913 K (x ~ 0.03); NiAl3
peritectic 1127 K; Ni2Al3 peritectic 1406 K; NiAl congruent 1911 K, B2 range ~0.45-0.60;
Ni3Al peritectic 1668 K; eutectic L -> Ni3Al + (Ni) 1658 K at x ~ 0.76; (Ni) dissolves up to
~0.21 Al; Al melts 933.5 K, Ni 1728 K.
"""

import glob
import json
import os
import sys
import time
from functools import partial

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POT = os.path.join(ROOT, "potentials/nial/Mishin-Ni-Al-2009.eam.alloy")
ENV = os.path.join(ROOT, "env/ftphase")
OUT = os.environ.get("NIAL_OUT", os.path.join(HERE, "out"))
CAL = os.environ.get("NIAL_CAL", os.path.join(HERE, "calphy_liquid"))
CAL_SOLID = os.environ.get("NIAL_CAL_SOLID", os.path.join(HERE, "calphy_solid"))
MODEL = "Mishin-Ni-Al-2009.eam.alloy (EAM, Purja Pun & Mishin 2009)"
ELEMENTS = ["Al", "Ni"]; MASSES = [26.9815, 58.6934]
CORES = int(os.environ.get("NIAL_CORES", "16"))              # MPI ranks per calphy job (64-core host: 4 jobs at once)
FCC_AL_X = [1 / 64, 2 / 64]
FCC_NI_X = [0.9375, 0.875, 0.8125, 0.75]
LIQ_X = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
T_START = 2000.0
#: sweep end per composition: well below the expected liquidus but above where a 256-atom
#: liquid is likely to freeze within the sweep (the phase check aborts such a run; resume with t_override.json)
T_STOP = {0.0: 850.0, 0.1: 850.0, 0.2: 950.0, 0.3: 1100.0, 0.4: 1300.0, 0.5: 1500.0, 0.6: 1450.0, 0.7: 1350.0, 0.8: 1400.0, 0.9: 1450.0, 1.0: 1500.0}
N_REPEAT = 2
N_EQ, N_SW, N_IT = 10000, [10000, 10000], 3
T_QHA = np.arange(0.0, 2001.0, 25.0)
T_MAX_QHA = {"fccAl": 1300.0, "NiAl3": 1400.0, "Ni2Al3": 1600.0}      # others: 2000 K
T_DIAG = np.arange(800.0, 2000.1, 10.0)
SCALES = (0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09)
#: phonopy mesh as a length (q-point density): with primitive_matrix='auto' a fixed 4x4x4 mesh means only 64 q-points for a
#: pure fcc cell but 4096-equivalent for a P1 SQS cell; 60 A gives ~20^3 for fcc and ~5^3 for the 64-atom cells (F converged to <1 meV)
MESH_LENGTH = 60.0
#: solids are also evaluated by calphy (Einstein-crystal TI, classical) on replicated cells of >= MIN_TI_ATOMS atoms:
#: at 0.8-0.9 T_m the quasi-harmonic free energy of this EAM is 20-40 meV/atom too high (anharmonicity), see REPORT.md
MIN_TI_ATOMS = 200
T_TI = {"fccAl": [700.0, 950.0], "fccNi": [900.0, 1750.0], "B2": [900.0, 1900.0], "L12": [900.0, 1700.0], "Ni2Al3": [900.0, 1500.0], "NiAl3": [700.0, 1300.0]}


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def eam():
    from ase.calculators.lammpslib import LAMMPSlib
    return LAMMPSlib(lmpcmds=["pair_style eam/alloy", f"pair_coeff * * {POT} Al Ni"], atom_types={"Al": 1, "Ni": 2}, keep_alive=True, log_file=None)


def structures():
    from ase import Atoms
    from ase.build import bulk
    from ase.spacegroup import crystal
    return {
        "fcc-Al": (bulk("Al", "fcc", a=4.05, cubic=True), 0.0),
        "fcc-Ni": (bulk("Ni", "fcc", a=3.52, cubic=True), 1.0),
        "B2-NiAl": (Atoms("NiAl", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0.5)], cell=[2.88] * 3, pbc=True), 0.5),
        "L12-Ni3Al": (Atoms("AlNi3", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)], cell=[3.57] * 3, pbc=True), 0.75),
        "Ni2Al3": (crystal(["Al", "Al", "Ni"], [(0, 0, 0), (1 / 3, 2 / 3, 0.149), (1 / 3, 2 / 3, 0.648)], spacegroup=164, cellpar=[4.03, 4.03, 4.89, 90, 90, 120]), 0.4),
        "NiAl3": (crystal(["Al", "Al", "Ni"], [(0.183, 0.069, 0.334), (0.039, 0.25, 0.842), (0.876, 0.25, 0.443)], spacegroup=62, cellpar=[6.61, 7.37, 4.81, 90, 90, 90]), 0.25),
    }


def _sqs(prim, conc, seed):
    from ftphase.structures import sqs_icet
    return sqs_icet(prim, [["Al", "Ni"]], cutoffs=[7.0, 5.0], target_concentrations=conc, max_size=64, method="supercells", supercells=[prim.repeat((4, 4, 4))], n_steps=20000, seed=seed)


def _x(at):
    syms = at.get_chemical_symbols()
    return syms.count("Ni") / len(syms)


# ----------------------------------------------------------------------------- prepare
def prepare():
    from ase.build import bulk
    from ase.io import write
    from ftphase.validate import relax, hull_0K, compare_ground_states
    from ftphase.structures import composition_series, write_lammps_data
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input

    os.makedirs(OUT, exist_ok=True); os.makedirs(CAL, exist_ok=True)
    calc = eam()
    info = {"potential": POT, "started": time.strftime("%F %T"), "host": os.uname().nodename}
    rows, relaxed = [], {}
    for name, (at, x) in structures().items():
        r = relax(at, calc, fmax=1e-3, cell=True)
        relaxed[name] = r
        rows.append({"name": name, "x": x, "e": r.energy_per_atom, "V": r.volume_per_atom, "sg_before": r.spacegroup_before, "sg_after": r.spacegroup_after, "converged": r.converged, "transformed": r.transformed})
        log(f"[01] {name:10s} E={r.energy_per_atom:.5f} eV/atom V={r.volume_per_atom:.3f}  {r.spacegroup_before} -> {r.spacegroup_after}")
    relax_df = pd.DataFrame(rows)
    hull = hull_0K(relax_df["name"], relax_df["x"], relax_df["e"])
    cmp = compare_ground_states(hull, ["fcc-Al", "fcc-Ni", "B2-NiAl", "L12-Ni3Al", "Ni2Al3", "NiAl3"])
    relax_df.to_csv(os.path.join(OUT, "01_relaxed.tsv"), sep="\t", index=False)
    hull.to_csv(os.path.join(OUT, "01_hull_0K.tsv"), sep="\t", index=False)
    cmp.to_csv(os.path.join(OUT, "01_ground_state_check.tsv"), sep="\t", index=False)
    log("[01] hull:\n" + hull.round(4).to_string(index=False))

    solids = []
    a_al = relaxed["fcc-Al"].atoms.cell.lengths()[0]; a_ni = relaxed["fcc-Ni"].atoms.cell.lengths()[0]
    p_al = bulk("Al", "fcc", a=a_al); p_ni = bulk("Ni", "fcc", a=a_ni)
    solids.append(("fccAl", "solution", 0.0, p_al.repeat((4, 4, 4)), [2, 2, 2], MESH_LENGTH, {}))
    for i, x in enumerate(FCC_AL_X):
        sqs, meta = _sqs(p_al, {"Al": 1 - x, "Ni": x}, seed=10 + i)
        solids.append(("fccAl", "solution", _x(sqs), sqs, [2, 2, 2], MESH_LENGTH, {"sqs_cluster_vector_deviation": meta["cluster_vector_deviation"]}))
    solids.append(("fccNi", "solution", 1.0, p_ni.repeat((4, 4, 4)), [2, 2, 2], MESH_LENGTH, {}))
    for i, x in enumerate(FCC_NI_X):
        sqs, meta = _sqs(p_ni, {"Ni": x, "Al": 1 - x}, seed=20 + i)
        solids.append(("fccNi", "solution", _x(sqs), sqs, [2, 2, 2], MESH_LENGTH, {"sqs_cluster_vector_deviation": meta["cluster_vector_deviation"]}))
    # B2: 3x3x3 of the relaxed 2-atom cell = 54 atoms, triple-defect constitution
    b2 = relaxed["B2-NiAl"].atoms.copy(); b2.calc = None; b2 = b2.repeat((3, 3, 3))
    al_sites = [i for i, s in enumerate(b2.get_chemical_symbols()) if s == "Al"]
    ni_sites = [i for i, s in enumerate(b2.get_chemical_symbols()) if s == "Ni"]
    rng = np.random.default_rng(0)
    solids.append(("B2", "limited", 0.5, b2.copy(), [2, 2, 2], MESH_LENGTH, {"defect": "none"}))
    for n in (1, 2):                                   # Ni-rich: Ni anti-sites on the Al sublattice
        a = b2.copy()
        for i in rng.choice(al_sites, n, replace=False):
            a[int(i)].symbol = "Ni"
        solids.append(("B2", "limited", _x(a), a, [2, 2, 2], MESH_LENGTH, {"defect": f"{n} Ni anti-site(s)"}))
    for n in (1, 2):                                   # Al-rich: Ni vacancies
        a = b2.copy()
        del a[[int(i) for i in rng.choice(ni_sites, n, replace=False)]]
        solids.append(("B2", "limited", _x(a), a, [2, 2, 2], MESH_LENGTH, {"defect": f"{n} Ni vacancy(ies)"}))
    # L1_2: 3x3x3 of the 4-atom cell = 108 atoms, anti-sites both ways
    l12 = relaxed["L12-Ni3Al"].atoms.copy(); l12.calc = None; l12 = l12.repeat((3, 3, 3))
    al_sites = [i for i, s in enumerate(l12.get_chemical_symbols()) if s == "Al"]
    ni_sites = [i for i, s in enumerate(l12.get_chemical_symbols()) if s == "Ni"]
    solids.append(("L12", "limited", 0.75, l12.copy(), [2, 2, 2], MESH_LENGTH, {"defect": "none"}))
    a = l12.copy(); a[int(rng.choice(al_sites))].symbol = "Ni"; solids.append(("L12", "limited", _x(a), a, [2, 2, 2], MESH_LENGTH, {"defect": "1 Ni anti-site"}))
    a = l12.copy(); a[int(rng.choice(ni_sites))].symbol = "Al"; solids.append(("L12", "limited", _x(a), a, [2, 2, 2], MESH_LENGTH, {"defect": "1 Al anti-site"}))
    for name, sc, mesh in (("Ni2Al3", [3, 3, 3], MESH_LENGTH), ("NiAl3", [2, 2, 3], MESH_LENGTH)):
        a = relaxed[name].atoms.copy(); a.calc = None
        solids.append((name, "point", _x(a), a, sc, mesh, {"note": "point phase; see 01_hull_0K.tsv for its distance to the hull"}))
    manifest = []
    for k, (ph, kind, x, at, sc, mesh, extra) in enumerate(solids):
        at.calc = None
        fn = os.path.join(OUT, f"02A_solid_{k:02d}_{ph}_x{x:.4f}.extxyz")
        write(fn, at, format="extxyz")
        m = {"id": k, "phase": ph, "kind": kind, "x": float(x), "file": fn, "supercell": sc, "mesh": mesh, "scales": list(SCALES), "n_atoms": len(at),
             "counts": {e: at.get_chemical_symbols().count(e) for e in sorted(set(at.get_chemical_symbols()))}}
        m.update(extra); manifest.append(m)
    with open(os.path.join(OUT, "02A_solids.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    log(f"[02A] {len(manifest)} solid cells written")

    # ---- 02B liquids: 256-atom fcc cells of the majority element with substitution; calphy ts sweeps + repeats
    q = slurm_queue(ENV, cores=CORES, memory="16GB")
    blocks, liq_manifest = [], []
    for x in LIQ_X:
        base = (p_al if x <= 0.5 else p_ni).repeat((4, 4, 4)).copy()
        base = bulk("Al" if x <= 0.5 else "Ni", "fcc", a=(a_al if x <= 0.5 else a_ni), cubic=True).repeat((4, 4, 4))
        sub_el, target = ("Ni", x) if x <= 0.5 else ("Al", 1 - x)
        m = composition_series(base, sub_el, [target], seed=100 + int(round(x * 10)), n_configs=1)[0]
        x_act = _x(m.atoms)
        data = write_lammps_data(m.atoms, os.path.join(CAL, f"lqd_x{x:.2f}_256.data"), ELEMENTS)
        for r in range(N_REPEAT + 1):
            tag = f"lqd_x{x:.2f}" + ("" if r == 0 else f"_r{r}")
            T = [T_START, T_STOP[x]]
            blocks.append(calculation_block(tag, "ts", ELEMENTS, MASSES, data, "eam/alloy", f"* * {POT} Al Ni", T, pressure=0, reference_phase="liquid",
                                            n_equilibration_steps=N_EQ, n_switching_steps=N_SW, n_iterations=N_IT, queue=q, folder_prefix=tag))
            liq_manifest.append({"tag": tag, "x_target": x, "x_actual": x_act, "counts": m.counts, "seed": m.seed, "data": data, "T_sweep": T, "dir": CAL})
    write_series_input(os.path.join(CAL, "input_liquid.yaml"), blocks)
    with open(os.path.join(OUT, "02B_liquids.json"), "w") as f:
        json.dump(liq_manifest, f, indent=1)
    info["finished"] = time.strftime("%F %T")
    with open(os.path.join(OUT, "prepare.json"), "w") as f:
        json.dump(info, f, indent=1, default=str)
    log(f"[02B] {len(blocks)} liquid calphy blocks ({CORES} ranks each) -> {CAL}/input_liquid.yaml")


# ----------------------------------------------------------------------------- prepare_more_defects
def prepare_more_defects():
    """Widen the sampled composition ranges of B2 (Ni anti-sites 3-6 -> x up to 0.611, Ni vacancies 3-4 -> x down
    to 0.46) and L1_2 (2 and 3 anti-sites each way).  New cells get new ids in 02A_solids.json and new TI blocks in
    calphy_solid/input_solid_more.yaml; `solids` and the TI resume then compute only the new ones."""
    from ase.io import read, write
    from ftphase.structures import write_lammps_data
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    manifest = json.load(open(os.path.join(OUT, "02A_solids.json")))
    ti_path = os.path.join(OUT, "02A_solids_ti.json"); ti_man = json.load(open(ti_path)) if os.path.exists(ti_path) else []
    cal = os.path.join(HERE, "calphy_solid"); os.makedirs(cal, exist_ok=True)
    b2 = read([m for m in manifest if m["phase"] == "B2" and m.get("defect") == "none"][0]["file"])
    l12 = read([m for m in manifest if m["phase"] == "L12" and m.get("defect") == "none"][0]["file"])
    rng = np.random.default_rng(1)
    new = []
    al_b2 = [i for i, sy in enumerate(b2.get_chemical_symbols()) if sy == "Al"]; ni_b2 = [i for i, sy in enumerate(b2.get_chemical_symbols()) if sy == "Ni"]
    for n in (3, 4, 5, 6):
        a = b2.copy()
        for i in rng.choice(al_b2, n, replace=False):
            a[int(i)].symbol = "Ni"
        new.append(("B2", "limited", a, [2, 2, 2], f"{n} Ni anti-site(s)"))
    for n in (3, 4):
        a = b2.copy(); del a[[int(i) for i in rng.choice(ni_b2, n, replace=False)]]
        new.append(("B2", "limited", a, [2, 2, 2], f"{n} Ni vacancy(ies)"))
    al_l = [i for i, sy in enumerate(l12.get_chemical_symbols()) if sy == "Al"]; ni_l = [i for i, sy in enumerate(l12.get_chemical_symbols()) if sy == "Ni"]
    for n in (2, 3):
        a = l12.copy()
        for i in rng.choice(al_l, n, replace=False):
            a[int(i)].symbol = "Ni"
        new.append(("L12", "limited", a, [2, 2, 2], f"{n} Ni anti-sites"))
        a = l12.copy()
        for i in rng.choice(ni_l, n, replace=False):
            a[int(i)].symbol = "Al"
        new.append(("L12", "limited", a, [2, 2, 2], f"{n} Al anti-sites"))
    k0 = max(m["id"] for m in manifest) + 1
    q = slurm_queue(ENV, cores=CORES, memory="16GB")
    blocks = []
    for j, (ph, kind, at, sc, defect) in enumerate(new):
        k = k0 + j; x = _x(at); at.calc = None
        fn = os.path.join(OUT, f"02A_solid_{k:02d}_{ph}_x{x:.4f}.extxyz"); write(fn, at, format="extxyz")
        manifest.append({"id": k, "phase": ph, "kind": kind, "x": float(x), "file": fn, "supercell": sc, "mesh": MESH_LENGTH, "scales": list(SCALES), "n_atoms": len(at),
                         "counts": {e: at.get_chemical_symbols().count(e) for e in sorted(set(at.get_chemical_symbols()))}, "defect": defect})
        f = _rep_factors(at, MIN_TI_ATOMS); big = at.repeat(tuple(f))
        tag = f"sol{k:02d}_{ph}_x{x:.4f}".replace(".", "p")
        data = write_lammps_data(big, os.path.join(cal, f"{tag}.data"), ELEMENTS)
        T = T_TI[ph]
        blocks.append(calculation_block(tag, "ts", ELEMENTS, MASSES, data, "eam/alloy", f"* * {POT} Al Ni", T, pressure=0, reference_phase="solid",
                                        n_equilibration_steps=N_EQ, n_switching_steps=N_SW, n_iterations=2, queue=q, folder_prefix=tag))
        ti_man.append({"id": k, "tag": tag, "phase": ph, "kind": kind, "x": float(x), "n_atoms": len(big), "repeat": f, "data": data, "T_sweep": T, "dir": cal, "defect": defect})
        log(f"[02A+] id {k} {ph} x={x:.4f} {defect} ({len(at)} atoms; TI cell {len(big)})")
    json.dump(manifest, open(os.path.join(OUT, "02A_solids.json"), "w"), indent=1)
    json.dump(ti_man, open(ti_path, "w"), indent=1)
    write_series_input(os.path.join(cal, "input_solid_more.yaml"), blocks)
    log(f"[02A+] {len(new)} extra defect cells; TI input {cal}/input_solid_more.yaml")


# ----------------------------------------------------------------------------- prepare_solids_ti
def _rep_factors(at, nmin):
    L = at.cell.lengths(); n = len(at); f = [1, 1, 1]
    while n * f[0] * f[1] * f[2] < nmin:
        i = int(np.argmin([L[k] * f[k] for k in range(3)])); f[i] += 1
    return f


def prepare_solids_ti():
    """calphy reversible-scaling runs (Einstein-crystal reference) for every solid cell of 02A, replicated
    to >= MIN_TI_ATOMS atoms (the defect concentration is unchanged by replication).  Written to
    calphy_solid/input_solid.yaml and out/02A_solids_ti.json."""
    from ase.io import read
    from ftphase.structures import write_lammps_data
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    cal = os.path.join(HERE, "calphy_solid"); os.makedirs(cal, exist_ok=True)
    manifest = json.load(open(os.path.join(OUT, "02A_solids.json")))
    q = slurm_queue(ENV, cores=CORES, memory="16GB")
    blocks, out_m = [], []
    for m in manifest:
        at = read(m["file"])
        f = _rep_factors(at, MIN_TI_ATOMS)
        big = at.repeat(tuple(f))
        tag = f"sol{m['id']:02d}_{m['phase']}_x{m['x']:.4f}".replace(".", "p")
        data = write_lammps_data(big, os.path.join(cal, f"{tag}.data"), ELEMENTS)
        T = T_TI.get(m["phase"], [900.0, 1800.0])
        blocks.append(calculation_block(tag, "ts", ELEMENTS, MASSES, data, "eam/alloy", f"* * {POT} Al Ni", T, pressure=0, reference_phase="solid",
                                        n_equilibration_steps=N_EQ, n_switching_steps=N_SW, n_iterations=2, queue=q, folder_prefix=tag))
        out_m.append({"id": m["id"], "tag": tag, "phase": m["phase"], "kind": m["kind"], "x": m["x"], "n_atoms": len(big), "repeat": f, "data": data, "T_sweep": T, "dir": cal, "defect": m.get("defect", "")})
    write_series_input(os.path.join(cal, "input_solid.yaml"), blocks)
    with open(os.path.join(OUT, "02A_solids_ti.json"), "w") as fh:
        json.dump(out_m, fh, indent=1)
    log(f"[03B-solid] {len(blocks)} calphy solid blocks -> {cal}/input_solid.yaml")


def resume_solids_ti():
    import shutil
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    cal = os.path.join(HERE, "calphy_solid")
    man = json.load(open(os.path.join(OUT, "02A_solids_ti.json")))
    override = json.load(open(os.path.join(cal, "t_override.json"))) if os.path.exists(os.path.join(cal, "t_override.json")) else {}
    q = slurm_queue(ENV, cores=CORES, memory="16GB")
    blocks, todo = [], []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    queued = _queued_tags()
    for m in man:
        tag = m["tag"]
        if _tag_queued(tag, queued):
            continue                      # still pending/running in Slurm: not unfinished
        if any(os.path.exists(os.path.join(d, "temperature_sweep.dat")) for d in glob.glob(os.path.join(cal, f"{tag}-ts-*/"))):
            continue
        for path in glob.glob(os.path.join(cal, f"{tag}-ts-*")):
            os.makedirs(os.path.join(cal, "failed", stamp), exist_ok=True)
            shutil.move(path, os.path.join(cal, "failed", stamp, os.path.basename(path)))
        T = [m["T_sweep"][0], float(override.get(tag, m["T_sweep"][1]))]
        m["T_sweep"] = T
        blocks.append(calculation_block(tag, "ts", ELEMENTS, MASSES, m["data"], "eam/alloy", f"* * {POT} Al Ni", T, pressure=0, reference_phase="solid",
                                        n_equilibration_steps=N_EQ, n_switching_steps=N_SW, n_iterations=2, queue=q, folder_prefix=tag))
        todo.append(tag)
    with open(os.path.join(OUT, "02A_solids_ti.json"), "w") as fh:
        json.dump(man, fh, indent=1)
    if blocks:
        write_series_input(os.path.join(cal, "input_solid_resume.yaml"), blocks)
    log(f"[resume solids-ti] unfinished: {todo} (overrides {override})")
    print("RESUME_TODO", " ".join(todo))




def _queued_tags():
    """Job names of this user in squeue, sanitised like calphy names its jobs (alnum only, lower case)."""
    import re, subprocess
    try:
        out = subprocess.run(["squeue", "-h", "-u", os.environ.get("USER", ""), "-o", "%j"], capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return set()
    return {re.sub(r"[^a-z0-9]", "", n.lower()) for n in out.split()}


def _tag_queued(tag, queued):
    import re
    t = re.sub(r"[^a-z0-9]", "", tag.lower())
    return any(n.startswith(t) for n in queued)


# ----------------------------------------------------------------------------- resume
def resume():
    import shutil
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    liq_manifest = json.load(open(os.path.join(OUT, "02B_liquids.json")))
    override = json.load(open(os.path.join(CAL, "t_override.json"))) if os.path.exists(os.path.join(CAL, "t_override.json")) else {}
    q = slurm_queue(ENV, cores=CORES, memory="16GB")
    blocks, todo = [], []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    queued = _queued_tags()
    for m in liq_manifest:
        tag = m["tag"]
        if _tag_queued(tag, queued):
            continue                      # still pending/running in Slurm: not unfinished
        if any(os.path.exists(os.path.join(d, "temperature_sweep.dat")) for d in glob.glob(os.path.join(CAL, f"{tag}-ts-*/"))):
            continue
        for path in glob.glob(os.path.join(CAL, f"{tag}-ts-*")):
            os.makedirs(os.path.join(CAL, "failed", stamp), exist_ok=True)
            shutil.move(path, os.path.join(CAL, "failed", stamp, os.path.basename(path)))
        T = [m["T_sweep"][0], float(override.get(tag, m["T_sweep"][1]))]
        m["T_sweep"] = T
        blocks.append(calculation_block(tag, "ts", ELEMENTS, MASSES, m["data"], "eam/alloy", f"* * {POT} Al Ni", T, pressure=0, reference_phase="liquid",
                                        n_equilibration_steps=N_EQ, n_switching_steps=N_SW, n_iterations=N_IT, queue=q, folder_prefix=tag))
        todo.append(tag)
    with open(os.path.join(OUT, "02B_liquids.json"), "w") as f:
        json.dump(liq_manifest, f, indent=1)
    if blocks:
        write_series_input(os.path.join(CAL, "input_liquid_resume.yaml"), blocks)
    log(f"[resume] unfinished liquids: {todo} (overrides {override})")
    print("RESUME_TODO", " ".join(todo))


# ----------------------------------------------------------------------------- solids
def solids():
    from ase.io import read
    from ftphase.validate import relax
    from ftphase.qha import phonopy_volume_scan
    from ftphase.records import FreeEnergyTable

    calc = eam()
    manifest = json.load(open(os.path.join(OUT, "02A_solids.json")))
    if os.environ.get("TX_SOLIDS_SUBSET"):
        keep = {int(v) for v in os.environ["TX_SOLIDS_SUBSET"].split(",")}
        manifest = [m for m in manifest if m["id"] in keep]
    status_path = os.path.join(OUT, "03A_status.json")
    status = json.load(open(status_path)) if os.path.exists(status_path) else []
    done = {s["id"] for s in status if s.get("ok")}
    tsv = os.path.join(OUT, "03A_qha_solids.tsv")
    rows = FreeEnergyTable.from_tsv(tsv).df.to_dict("records") if done and os.path.exists(tsv) else []
    t0 = time.time()
    for m in manifest:
        if m["id"] in done:
            continue
        at = read(m["file"])
        t1 = time.time()
        try:
            r = relax(at, calc, fmax=1e-3, cell=True, hydrostatic=True)
            a0 = r.atoms.copy(); a0.calc = None
            t_max = T_MAX_QHA.get(m["phase"], T_QHA[-1])
            while True:          # QHA has no minimum far above the melting point: shorten the T range instead of failing
                Tq = T_QHA[T_QHA <= t_max + 1e-9]
                try:
                    res, data = phonopy_volume_scan(a0, calc, np.diag(m["supercell"]), Tq, scales=tuple(m["scales"]), mesh=(tuple(m["mesh"]) if isinstance(m["mesh"], list) else float(m["mesh"])), imaginary="drop", eos="vinet")
                    break
                except ValueError as e:
                    if "EOS minimum" in str(e) and t_max > 700.0:
                        t_max -= 200.0
                        log(f"[03A] {m['id']:02d} {m['phase']}: {e}; retrying with T <= {t_max:.0f} K")
                        continue
                    raise
            G, V = res.per_atom()
            i1 = int(np.argmin(np.abs(np.asarray(m["scales"]) - 1.0)))
            hw, w = data["frequencies"][i1]
            np.savez(os.path.join(OUT, f"03A_freq_{m['id']:02d}.npz"), hw_eV=hw, weights=w, n_atoms=len(a0), volumes=data["volumes"], e0=data["e0"], f_vib=data["f_vib"], T=Tq)
            for T, g, v in zip(Tq, G, V):
                rows.append({"phase": m["phase"], "kind": m["kind"], "x": m["x"], "T": float(T), "P_GPa": 0.0, "G": float(g), "G_err": 0.0, "V": float(v), "model": MODEL,
                             "reference_state": "absolute EAM energy", "method": f"QHA vinet {len(m['scales'])} volumes, phonopy sc={m['supercell']} mesh={m['mesh']}, quantum; {m['n_atoms']}-atom cell; {m.get('defect', '')}",
                             "config_entropy": "none", "quantum": "quantum", "n_atoms": len(a0), "source": f"nial_eam solid {m['id']}"})
            st = {"id": m["id"], "phase": m["phase"], "x": m["x"], "ok": True, "E0_eV_per_atom": r.energy_per_atom, "V0": r.volume_per_atom, "sg": f"{r.spacegroup_before}->{r.spacegroup_after}",
                  "G300": float(np.interp(300, Tq, G)), "T_max": float(Tq[-1]), "V_Tmax": float(V[-1]), "n_imag_dropped": int(np.sum(hw < 0)), "seconds": time.time() - t1}
            log(f"[03A] {m['id']:02d} {m['phase']} x={m['x']:.4f}: G(300)={st['G300']:.5f} V({Tq[-1]:.0f})={st['V_Tmax']:.3f} {st['sg']} {st['seconds']:.0f}s")
        except Exception as e:
            st = {"id": m["id"], "phase": m["phase"], "x": m["x"], "ok": False, "error": repr(e), "seconds": time.time() - t1}
            log(f"[03A] {m['id']:02d} FAILED: {e!r}")
        status = [s for s in status if s["id"] != m["id"]] + [st]
        with open(status_path, "w") as f:
            json.dump(status, f, indent=1, default=str)
        if rows:
            FreeEnergyTable.from_rows(rows, {"potential": POT, "stage": "03A quantum QHA, fixed configurations"}).to_tsv(tsv)
    log(f"[03A] done: {sum(1 for s in status if s['ok'])}/{len(manifest)} cells in {time.time()-t0:.0f} s")


# ----------------------------------------------------------------------------- assemble
def assemble():
    import matplotlib
    matplotlib.use("Agg")
    from ftphase.records import FreeEnergyTable
    from ftphase.quantum import quantum_minus_classical
    from ftphase.configurational import b32_antisite_site_fractions, b2_triple_defect_site_fractions
    from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table, fit_residuals
    from ftphase.diagram import scan, invariants, sensitivity, plot_tx, write_records
    from ftphase.calphy_io import read_calphy_results

    summary = {"started": time.strftime("%F %T"), "host": os.uname().nodename}
    sol = FreeEnergyTable.from_tsv(os.path.join(OUT, "03A_qha_solids.tsv")).df
    status = json.load(open(os.path.join(OUT, "03A_status.json")))
    summary["solids_failed"] = [s for s in status if not s["ok"]]
    sol["sid"] = sol.source.str.extract(r"solid (\d+)")[0].astype(int)
    parts = []
    for sid, g in sol.groupby("sid"):
        fr = np.load(os.path.join(OUT, f"03A_freq_{sid:02d}.npz"))
        g = g.sort_values("T").copy()
        Tpos = g["T"].to_numpy() > 0
        dF = np.zeros(len(g))
        dF[Tpos] = quantum_minus_classical(fr["hw_eV"], g["T"].to_numpy()[Tpos], weights=fr["weights"], imaginary="drop") / int(fr["n_atoms"])
        g["G"] = g["G"] - dF
        g["quantum"] = "classical+harmonic-correction"
        g["method"] = g["method"] + "; lowered by F_q-F_cl (harmonic)"
        parts.append(g)
    sol = pd.concat(parts).drop(columns=["sid"])
    qha_sol = sol.copy()
    # ---- solids by calphy TI (classical, anharmonic) replace the QHA rows where a finished run exists
    ti_man_path = os.path.join(OUT, "02A_solids_ti.json")
    solids_source = "QHA (classical level)"
    if os.path.exists(ti_man_path):
        try:
            ti = read_calphy_results(CAL_SOLID, reference_element="Ni", model=MODEL, source_prefix="nial_eam/calphy_solid/").df
            ti = ti[ti["config_entropy"] == "none"].copy()
        except Exception as e:
            ti = pd.DataFrame(); summary["solid_ti_error"] = repr(e)
        if not ti.empty:
            man = {m["tag"]: m for m in json.load(open(ti_man_path))}
            ti["tag"] = ti["source"].str.extract(r"calphy_solid/([^-]+)-ts")[0]
            ti = ti[ti["tag"].isin(man)].copy()
            ti["phase"] = ti["tag"].map(lambda t: man[t]["phase"]); ti["kind"] = ti["tag"].map(lambda t: man[t]["kind"]); ti["x"] = ti["tag"].map(lambda t: man[t]["x"])
            ti["reference_state"] = "absolute EAM energy"; ti["method"] = ti["method"] + "; solid TI (Einstein crystal), " + ti["tag"].map(lambda t: man[t]["defect"] or "")
            ti = ti.drop(columns=["tag"])
            done_ids = {man[t]["id"] for t in set(ti["source"].str.extract(r"calphy_solid/([^-]+)-ts")[0]) if t in man}
            # QHA vs TI at common temperatures, per cell
            comp = []
            for tag, m in man.items():
                a = ti[(ti.phase == m["phase"]) & np.isclose(ti.x, m["x"])]; b = qha_sol[(qha_sol.phase == m["phase"]) & np.isclose(qha_sol.x, m["x"])]
                if a.empty or b.empty:
                    continue
                for T in (1000.0, 1500.0):
                    if a["T"].min() <= T <= a["T"].max() and b["T"].min() <= T <= b["T"].max():
                        comp.append({"phase": m["phase"], "x": m["x"], "T": T, "QHA_minus_TI_meV": float((np.interp(T, b.sort_values("T")["T"], b.sort_values("T")["G"]) - np.interp(T, a.sort_values("T")["T"], a.sort_values("T")["G"])) * 1000)})
            summary["qha_minus_ti_meV"] = comp
            keep_qha = qha_sol[~qha_sol.source.str.extract(r"solid (\d+)")[0].astype(int).isin(done_ids)]
            sol = pd.concat([ti[qha_sol.columns.intersection(ti.columns)], keep_qha], ignore_index=True)
            solids_source = f"calphy TI (Einstein crystal, classical) for {len(done_ids)} cells, QHA for the rest"
            summary["solids_ti_cells"] = sorted(done_ids)
    summary["solids_source"] = solids_source

    liq = pd.DataFrame()
    try:
        liq = read_calphy_results(CAL, reference_element="Ni", model=MODEL, source_prefix="nial_eam/calphy_liquid/").df
        liq = liq[liq["config_entropy"] == "liquid-ti"].copy()
    except Exception as e:
        summary["liquid_error"] = repr(e)
    if liq.empty:
        raise SystemExit("no finished liquid runs: " + str(summary))
    liq["phase"] = "liquid"; liq["reference_state"] = "absolute EAM energy"
    liq["x"] = liq["x"].round(4); liq["T"] = liq["T"].round(1)
    summary["liquid_runs"] = liq.groupby("x")["source"].nunique().to_dict()
    g = liq.groupby(["x", "T"])
    agg = g.agg(G=("G", "mean"), G_std=("G", "std"), G_err0=("G_err", "mean"), n=("G", "size")).reset_index()
    agg["G_std"] = agg["G_std"].fillna(0.0)
    agg["G_err"] = np.sqrt(agg["G_err0"] ** 2 + (agg["G_std"] / np.sqrt(agg["n"].clip(lower=1))) ** 2)
    first = g.first().reset_index()
    liq = first.drop(columns=["G", "G_err"]).merge(agg[["x", "T", "G", "G_err", "n"]], on=["x", "T"])
    liq["method"] = liq["method"] + liq["n"].map(lambda k: f"; mean of {k} runs" if k > 1 else "")
    spread = liq[np.isclose(liq["T"], 1500.0)].groupby("x")["G_err"].mean()
    summary["liquid_G_err_1500K_meV"] = {f"{x:.4f}": float(v * 1000) for x, v in spread.items()}
    liq = liq.drop(columns=["n"])
    summary["liquid_x_available"] = sorted(float(v) for v in liq["x"].unique())
    summary["liquid_T_range"] = {f"{x:.4f}": [float(a), float(b)] for x, (a, b) in liq.groupby("x")["T"].agg(["min", "max"]).iterrows()}

    allrows = pd.concat([sol, liq], ignore_index=True)
    for ph, gg in allrows.groupby("phase"):
        if gg["kind"].iloc[0] != "point" and gg["x"].nunique() < 2:
            allrows.loc[allrows.phase == ph, "kind"] = "point"
            summary.setdefault("degraded_to_point", []).append(ph)
    tab = FreeEnergyTable.from_rows(allrows.to_dict("records"), {"potential": POT, "pressure_GPa": 0.0, "level": "classical"})
    phases = set(tab.df.phase)
    for ph in ("fccAl", "fccNi"):
        if ph in phases:
            tab = add_configurational_term(tab, ph, "ideal")
    if "B2" in phases and tab.df[tab.df.phase == "B2"]["x"].nunique() > 1:
        tab = add_configurational_term(tab, "B2", "sublattice", site_model=b2_triple_defect_site_fractions)
    if "L12" in phases and tab.df[tab.df.phase == "L12"]["x"].nunique() > 1:
        tab = add_configurational_term(tab, "L12", "sublattice", site_model=partial(b32_antisite_site_fractions, stoich_x=0.75))
    summary["table_check"] = [str(w) for w in tab.check()]
    tab.to_tsv(os.path.join(OUT, "05_free_energies.tsv"))
    ti = interpolate_T(tab, T_DIAG)
    # the liquid sweeps end at composition-dependent T_stop: at low T only the Al-rich liquid exists.  Keep every T
    # with at least 3 liquid compositions; the liquid curve then spans only the sampled x range and segments that
    # end at a sampled edge (not at a pure element) are removed below as artefacts of the range, not boundaries.
    cover = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["min", "max", "size"])
    ok_T = cover[cover["size"] >= 3].index
    ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(ok_T)], ti.meta)
    Ts = np.array(sorted(ti.df["T"].unique()))
    summary["T_grid"] = [float(Ts.min()), float(Ts.max()), int(Ts.size)]
    # B2 / L1_2: the analytic sublattice entropy is separated and the defect-energy part is fitted linearly per branch
    # (anti-site side / vacancy side), which averages the configuration noise of the individual defect cells
    FITS = {"fccAl": "poly", "fccNi": "poly", "liquid": "rk", "B2": "poly", "L12": "poly"}
    HULL = {"min_width": 0.005, "gap_tol": 2.5}
    ENT = {"B2": (b2_triple_defect_site_fractions, 0.5), "L12": (partial(b32_antisite_site_fractions, stoich_x=0.75), 0.75)}
    builder = builder_from_table(ti, fit="spline", fits=FITS, poly_order=3, poly_orders={"liquid": 4, "fccAl": 2, "B2": 1, "L12": 1}, entropy_models=ENT)
    resid = fit_residuals(builder, float(Ts[len(Ts) // 2]))
    resid.to_csv(os.path.join(OUT, "06_fit_residuals.tsv"), sep="\t", index=False)
    reg = scan(builder, Ts, **HULL)
    rng_ = ti.df[ti.df.kind != "point"].groupby(["phase", "T"])["x"].agg(["min", "max"])

    def _edge(row):
        a = rng_.loc[(row.phase_a, row["T"])] if (row.phase_a, row["T"]) in rng_.index else None
        b = rng_.loc[(row.phase_b, row["T"])] if (row.phase_b, row["T"]) in rng_.index else None
        left_edge = a is not None and abs(row.x_a - a["max"]) < 1e-6 and a["max"] < 1 - 1e-6 and row.phase_a != row.phase_b
        right_edge = b is not None and abs(row.x_b - b["min"]) < 1e-6 and b["min"] > 1e-6 and row.phase_a != row.phase_b
        return bool(left_edge or right_edge)

    reg["edge"] = reg.apply(_edge, axis=1) if len(reg) else []
    summary["edge_segments"] = int(reg["edge"].sum()) if len(reg) else 0   # boundary sits at a sampled composition limit: lower bound of the true width
    inv = invariants(reg)
    write_records(os.path.join(OUT, "07_two_phase_regions.tsv"), reg, {"example": "nial_eam", "potential": MODEL, "fit": str(FITS), "hull": str(HULL), "T_step": 10.0,
                                                                       "level": "classical (QHA lowered by F_q-F_cl)", "liquid": f"calphy ts {T_START} K -> T_stop(x), UFM, {N_IT} iterations, {N_REPEAT + 1} runs"})
    inv.to_csv(os.path.join(OUT, "07_invariants.tsv"), sep="\t", index=False)
    sig = {ph: 0.002 for ph in set(ti.df.phase) if ph != "liquid"}
    sig["liquid"] = float(max(0.0014, spread.mean())) if len(spread) else 0.0014
    summary["sigma_used_eV"] = sig
    sens = sensitivity(builder, Ts[::4], sig, n_samples=30, rng=0, **HULL)
    sens.table.to_csv(os.path.join(OUT, "07_sensitivity.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Ni", dT=10.0)
    ax.set_xlim(0.0, 1.0)
    ax.set_title(f"Ni-Al, Mishin 2009 EAM, 0 GPa: solids = {solids_source.split(' for ')[0]}, liquid = calphy TI", fontsize=8)
    ax.figure.savefig(os.path.join(OUT, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")

    summary["invariants"] = inv.to_dict("records")
    for T in (900.0, 1200.0, 1500.0, 1800.0):
        summary[f"regions_at_{int(T)}K"] = reg[np.isclose(reg["T"], T)][["phase_a", "x_a", "phase_b", "x_b"]].round(4).to_dict("records")
    b2 = reg[(reg.phase_a == "B2") | (reg.phase_b == "B2")]
    summary["B2_range_vs_T"] = {int(T): [float(gg.loc[gg.phase_a == "B2", "x_a"].min()) if (gg.phase_a == "B2").any() else None,
                                         float(gg.loc[gg.phase_b == "B2", "x_b"].max()) if (gg.phase_b == "B2").any() else None] for T, gg in b2.groupby("T") if int(T) % 100 == 0}
    liqreg = reg[(reg.phase_a == "liquid") | (reg.phase_b == "liquid")]
    summary["lowest_T_with_liquid_K"] = float(liqreg["T"].min()) if not liqreg.empty else None
    summary["B2_liquid_highest_T_K"] = float(b2[(b2.phase_a == "liquid") | (b2.phase_b == "liquid")]["T"].max()) if not b2.empty else None
    summary["fit_rmse"] = resid.to_dict("records")
    summary["finished"] = time.strftime("%F %T")
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str, ensure_ascii=False)
    write_report(summary, reg, sens.table)
    log(json.dumps({k: summary[k] for k in ("lowest_T_with_liquid_K", "B2_liquid_highest_T_K", "liquid_x_available", "solids_failed", "T_grid") if k in summary}, ensure_ascii=False, default=str))


def write_report(summary, reg, sens):
    L = ["# Example 7: Ni-Al T-x diagram, Purja Pun & Mishin 2009 EAM (classical level, 0 GPa)", "",
         f"Assembled {summary['finished']} on {summary.get('host')}.  Files: out/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.", "",
         "## Inputs", "", "* potential: potentials/nial/Mishin-Ni-Al-2009.eam.alloy (NIST, Purja Pun & Mishin, Philos. Mag. 89, 3245 (2009)).",
         "* solids: QHA of 64-atom SQS (fcc(Al) x = 0-0.03, fcc(Ni) x = 0.75-1), B2 54-atom cells with Ni anti-sites (Ni-rich) and Ni vacancies (Al-rich), L1_2 108-atom cells with anti-sites, Ni2Al3 and NiAl3 point phases; quantum QHA lowered to the classical level.",
         f"* liquids: calphy reversible scaling {T_START:.0f} K -> T_stop(x), UFM, {N_IT} iterations, {N_REPEAT + 1} independent runs per composition averaged; compositions " + ", ".join(f"{v:.2f}" for v in summary.get("liquid_x_available", [])) + ".",
         "* configurational terms: ideal mixing (fcc), triple-defect sublattice model (B2: anti-sites + vacancies), two-sublattice anti-site model (L1_2).",
         "* fits: liquid = ideal mixing + 4-term Redlich-Kister; fcc = polynomial excess over ideal mixing; B2, L1_2 = analytic sublattice entropy + linear defect energy per branch (anti-site / vacancy side).", ""]
    if "T_grid" in summary:
        L += [f"Temperature grid {summary['T_grid'][0]:.0f}-{summary['T_grid'][1]:.0f} K ({summary['T_grid'][2]} points); liquid runs per composition {summary.get('liquid_runs')}; sigma in the Monte Carlo (eV/atom) {summary.get('sigma_used_eV')}", ""]
    if summary.get("solids_failed"):
        L += ["**Failed solid cells:** " + "; ".join(f"{s['phase']} x={s['x']}: {s.get('error', '')[:120]}" for s in summary["solids_failed"]), ""]
    L += ["## Key numbers (experiment: NiAl congruent 1911 K, B2 range ~0.45-0.60; Ni3Al peritectic 1668 K; eutectic L -> Ni3Al + (Ni) 1658 K x~0.76; Al-rich eutectic 913 K; Al 933.5 K; Ni 1728 K)", ""]
    L += [f"* B2 + liquid up to {summary.get('B2_liquid_highest_T_K')} K; lowest temperature with liquid on the grid {summary.get('lowest_T_with_liquid_K')} K"]
    L += ["* B2 composition range [x_Ni lower, upper] vs T: " + "; ".join(f"{T} K {v}" for T, v in summary.get("B2_range_vs_T", {}).items())]
    L += [f"* segments whose boundary sits at a sampled composition limit (flag edge=True in 07_two_phase_regions.tsv; the true width may be larger): {summary.get('edge_segments')}"]
    L += ["* invariant reactions (pairs change between T_low and T_high):"]
    for r in summary.get("invariants", []):
        L += [f"  * {r['T_low']:.0f}-{r['T_high']:.0f} K: {r['pairs_below']} -> {r['pairs_above']}"]
    for T in (900, 1200, 1500, 1800):
        rr = summary.get(f"regions_at_{T}K", [])
        L += [f"* two-phase regions at {T} K: " + ("; ".join(f"{c['phase_a']}({c['x_a']:.3f})-{c['phase_b']}({c['x_b']:.3f})" for c in rr) if rr else "none")]
    same = reg[reg.phase_a == reg.phase_b].copy()
    if not same.empty:
        same["w"] = same.x_b - same.x_a
        L += ["", "## Same-phase segments (fit noise unless wide)", ""]
        for (pa, lo_, hi_), gg in same.groupby(["phase_a", same.x_a.round(2), same.x_b.round(2)]):
            L += [f"* {pa}+{pa} x = {lo_:.3f}-{hi_:.3f} (width {gg['w'].mean():.3f}) at T = {gg['T'].min():.0f}-{gg['T'].max():.0f} K ({len(gg)} temperatures)"]
    L += ["", "## Error bands (Monte Carlo, 30 samples)", ""]
    try:
        for T in sorted(sens["T"].unique())[::3]:
            s = sens[np.isclose(sens["T"], T)]
            for _, r in s.iterrows():
                L += [f"* {T:.0f} K {r['pair']}: x_a = {r['x_a_mean']:.3f} +/- {r['x_a_std']:.3f}, x_b = {r['x_b_mean']:.3f} +/- {r['x_b_std']:.3f} ({int(r['n_found'])}/{int(r['n_samples'])})"]
    except Exception as e:  # pragma: no cover
        L += [f"(sensitivity table not readable: {e!r})"]
    if summary.get("qha_minus_ti_meV"):
        L += ["", "## QHA (classical level) minus calphy solid TI, per cell (anharmonic error of the quasi-harmonic route; mesh converged)", ""]
        for c in summary["qha_minus_ti_meV"]:
            L += [f"* {c['phase']} x = {c['x']:.4f} at {c['T']:.0f} K: {c['QHA_minus_TI_meV']:+.1f} meV/atom"]
    L += ["", "## Caveats", "", "* This EAM puts NiAl3 and Ni2Al3 60-120 meV/atom above the 0 K hull (01_hull_0K.tsv), so the Al-rich intermetallics of the experimental diagram are absent; the B2 and L1_2 widths are the point of this example.",
          "* Nothing below the lowest T_stop of the liquids is computed; T_stop(x) is listed in 02B_liquids.json.", "* Table check: " + "; ".join(summary.get("table_check", [])) + " (intended).", ""]
    with open(os.path.join(OUT, "REPORT.md"), "w") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    {"prepare": prepare, "prepare_more_defects": prepare_more_defects, "prepare_solids_ti": prepare_solids_ti, "resume_solids_ti": resume_solids_ti, "resume": resume, "solids": solids, "assemble": assemble}[sys.argv[1]]()
