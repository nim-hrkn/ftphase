"""Example 6: full-range T-x diagram of ACE Al-Li (0 <= x_Li <= 1) with lower
configurational noise, as a Slurm chain (run_pipeline_full.sh / run_resume_full.sh).

Changes with respect to pipeline.py (example 5, Al-rich half, 32-atom random cells):
  * fcc solid solution: one 64-atom icet SQS per composition (x = 0.0625 .. 0.25,
    4x4x4 of the fcc primitive cell, cutoffs 7/5 A, 20000 MC steps) instead of two
    32-atom random cells -> smaller configurational noise; the difference to the
    example-5 free energies is reported in out_full/REPORT.md.
  * Li side: bcc solid solution (64-atom SQS, x_Li = 0.75 .. 1.0, wide volume scan
    0.96-1.14 because Li expands strongly), liquids x = 0.6 .. 1.0 (250-atom bcc
    cells, calphy ts 1100 -> 700 K on the GPU).  The Al-side liquids x = 0 .. 0.5
    of example 5 (same settings) are reused from calphy_liquid/.
  * Not included: the Li-rich intermetallics Al2Li3 and Al4Li9 (no structure files
    offline); the Li side is therefore B32 + bcc + liquid only.  Below 700 K the
    diagram is not computed.

Outputs: out_full/ (01_*, 02A_*, 02B_*, 03A_*, 05_*, 06_*, 07_*, summary.json,
REPORT.md), calphy_liquid_li/.  Every step is idempotent; after a crash run
run_resume_full.sh.
"""

import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pipeline import ace, b32_alli, l12_al3li, log, POT, LMP_GPU, ENV, MODEL, T_QHA, T_DIAG, T_LIQ  # noqa: E402

OUT = os.path.join(HERE, "out_full")
OUT5 = os.path.join(HERE, "out")                     # example 5 (for the noise comparison)
CAL_AL = os.path.join(HERE, "calphy_liquid")         # example 5 liquids x <= 0.5 (reused)
CAL_LI = os.path.join(HERE, "calphy_liquid_li")      # new liquids x >= 0.6
FCC_X = [0.0625, 0.125, 0.1875, 0.25]
BCC_X = [0.75, 0.8125, 0.875, 0.9375]                # x_Li on the bcc Li lattice
LIQ_X_LI = [0.6, 0.7, 0.8, 0.9, 1.0]
SC_FCC = (0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05)
CAL_MORE = os.path.join(HERE, "calphy_liquid_more")   # low-T sweeps (700 -> T_stop) and independent repeats of 1100 -> 700
#: end of the low-temperature liquid sweep per composition.  Al-rich liquids freeze far below the
#: eutectic (x = 0.1 solidified at 700 K already), so they stop at 650 K; from x = 0.4 on the sweep
#: goes to 500 K (Li-rich liquids are stable down to the Li melting point, 453 K).
LOW_T_STOP = {0.0: 650.0, 0.2: 650.0, 0.3: 650.0, 0.4: 500.0, 0.5: 500.0, 0.6: 500.0, 0.7: 500.0, 0.8: 500.0, 0.9: 500.0, 1.0: 500.0}
N_REPEAT = 2                                           # extra independent 1100 -> 700 K runs per composition (new seeds)
T_DIAG_MORE = np.arange(500.0, 1100.1, 10.0)
SC_BCC = (0.96, 0.98, 1.0, 1.02, 1.04, 1.06, 1.08, 1.10, 1.12, 1.14)
#: phonopy mesh as a length (q-point density).  A fixed [4,4,4] mesh with primitive_matrix='auto' means only 64 q-points
#: for the pure fcc/bcc cells (phonopy reduces them to the 1-atom primitive) but 4096-equivalent for the P1 SQS cells;
#: that under-converged the pure-element F by ~1 meV/atom at 1000 K.  60 A -> ~20^3 for fcc, ~5^3 for 64-atom cells.
MESH_LENGTH = 60.0


def _sqs(prim, conc, seed):
    from ftphase.structures import sqs_icet
    sc = prim.repeat((4, 4, 4))
    return sqs_icet(prim, [["Al", "Li"]], cutoffs=[7.0, 5.0], target_concentrations=conc, max_size=64, method="supercells", supercells=[sc], n_steps=20000, seed=seed)


# ----------------------------------------------------------------------------- prepare
def prepare():
    from ase.build import bulk
    from ase.io import write
    from ftphase.validate import relax, hull_0K, compare_ground_states
    from ftphase.structures import composition_series, write_lammps_data
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input, gpu_capability

    os.makedirs(OUT, exist_ok=True); os.makedirs(CAL_LI, exist_ok=True)
    calc = ace()
    info = {"potential": POT, "started": time.strftime("%F %T")}
    cands = {"fcc-Al": (bulk("Al", "fcc", a=4.05, cubic=True), 0.0), "bcc-Li": (bulk("Li", "bcc", a=3.49, cubic=True), 1.0),
             "B32-AlLi": (b32_alli(), 0.5), "L12-Al3Li": (l12_al3li(), 0.25)}
    rows, relaxed = [], {}
    for name, (at, x) in cands.items():
        r = relax(at, calc, fmax=1e-3, cell=True)
        relaxed[name] = r
        rows.append({"name": name, "x": x, "e": r.energy_per_atom, "V": r.volume_per_atom, "sg_before": r.spacegroup_before, "sg_after": r.spacegroup_after, "converged": r.converged, "transformed": r.transformed})
        log(f"[01] {name:10s} E={r.energy_per_atom:.5f} eV/atom V={r.volume_per_atom:.3f}  {r.spacegroup_before} -> {r.spacegroup_after}")
    relax_df = pd.DataFrame(rows)
    hull = hull_0K(relax_df["name"], relax_df["x"], relax_df["e"])
    cmp = compare_ground_states(hull, ["fcc-Al", "bcc-Li", "B32-AlLi"])
    relax_df.to_csv(os.path.join(OUT, "01_relaxed.tsv"), sep="\t", index=False)
    hull.to_csv(os.path.join(OUT, "01_hull_0K.tsv"), sep="\t", index=False)
    cmp.to_csv(os.path.join(OUT, "01_ground_state_check.tsv"), sep="\t", index=False)

    a_fcc = relaxed["fcc-Al"].atoms.cell.lengths()[0]; a_bcc = relaxed["bcc-Li"].atoms.cell.lengths()[0]
    prim_fcc = bulk("Al", "fcc", a=a_fcc); prim_bcc = bulk("Li", "bcc", a=a_bcc)
    solids = []
    solids.append(("fcc", "solution", 0.0, 0, prim_fcc.repeat((4, 4, 4)), [2, 2, 2], MESH_LENGTH, SC_FCC, {}))
    for i, x in enumerate(FCC_X):
        sqs, meta = _sqs(prim_fcc, {"Al": 1 - x, "Li": x}, seed=10 + i)
        solids.append(("fcc", "solution", x, 0, sqs, [2, 2, 2], MESH_LENGTH, SC_FCC, {"sqs_cluster_vector_deviation": meta["cluster_vector_deviation"]}))
        log(f"[02A] fcc SQS x={x}: {sqs.get_chemical_formula()} dev={meta['cluster_vector_deviation']:.3f}")
    solids.append(("bcc", "solution", 1.0, 0, prim_bcc.repeat((4, 4, 4)), [2, 2, 2], MESH_LENGTH, SC_BCC, {}))
    for i, x in enumerate(BCC_X):
        sqs, meta = _sqs(prim_bcc, {"Li": x, "Al": 1 - x}, seed=20 + i)
        solids.append(("bcc", "solution", x, 0, sqs, [2, 2, 2], MESH_LENGTH, SC_BCC, {"sqs_cluster_vector_deviation": meta["cluster_vector_deviation"]}))
        log(f"[02A] bcc SQS x={x}: {sqs.get_chemical_formula()} dev={meta['cluster_vector_deviation']:.3f}")
    al3li = relaxed["L12-Al3Li"].atoms.copy(); al3li.calc = None
    solids.append(("Al3Li", "point", 0.25, 0, al3li, [3, 3, 3], MESH_LENGTH, SC_FCC, {}))
    b32 = relaxed["B32-AlLi"].atoms.copy(); b32.calc = None
    syms = b32.get_chemical_symbols()
    i_li = [i for i, s in enumerate(syms) if s == "Li"][0]; i_al = [i for i, s in enumerate(syms) if s == "Al"][0]
    b_al = b32.copy(); b_al[i_li].symbol = "Al"; b_li = b32.copy(); b_li[i_al].symbol = "Li"
    for x, at in ((0.5, b32.copy()), (7 / 16, b_al), (9 / 16, b_li)):
        solids.append(("B32", "limited", x, 0, at, [2, 2, 2], MESH_LENGTH, SC_FCC, {}))
    manifest = []
    for k, (ph, kind, x, cfg, at, sc, mesh, scales, extra) in enumerate(solids):
        at.calc = None
        fn = os.path.join(OUT, f"02A_solid_{k:02d}_{ph}_x{x:.4f}.extxyz")
        write(fn, at, format="extxyz")
        m = {"id": k, "phase": ph, "kind": kind, "x": float(x), "config": int(cfg), "file": fn, "supercell": sc, "mesh": mesh, "scales": list(scales), "n_atoms": len(at),
             "counts": {e: at.get_chemical_symbols().count(e) for e in sorted(set(at.get_chemical_symbols()))}}
        m.update(extra); manifest.append(m)
    with open(os.path.join(OUT, "02A_solids.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    log(f"[02A] {len(manifest)} solid cells written")

    # Li-side liquids: 250-atom bcc cells with Al substitution
    cap = gpu_capability(LMP_GPU); info["lmp_gpu"] = cap
    if not cap["all_modes"]:
        raise SystemExit(f"{LMP_GPU} cannot run calphy liquids on the GPU: {cap}")
    liq_base = relaxed["bcc-Li"].atoms.copy(); liq_base.calc = None; liq_base = liq_base.repeat((5, 5, 5))     # 250 atoms
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks, liq_manifest = [], []
    for m in composition_series(liq_base, "Al", [1 - x for x in LIQ_X_LI], seed=200, n_configs=1):
        x_li = 1 - m.x_target
        tag = f"lqd_x{x_li:.2f}"
        data = write_lammps_data(m.atoms, os.path.join(CAL_LI, f"{tag}_250.data"), ["Al", "Li"])
        blocks.append(calculation_block(tag, "ts", ["Al", "Li"], [26.9815, 6.94], data, "pace", f"* * {POT} Al Li", T_LIQ, pressure=0,
                                        reference_phase="liquid", n_equilibration_steps=10000, n_switching_steps=[10000, 10000], n_iterations=3,
                                        queue=q, folder_prefix=tag, gpu=True, lammps_executable=LMP_GPU))
        liq_manifest.append({"tag": tag, "x_target": x_li, "x_actual": 1 - m.x_actual, "counts": m.counts, "seed": m.seed, "data": data, "dir": CAL_LI})
    write_series_input(os.path.join(CAL_LI, "input_liquid_li_gpu.yaml"), blocks)
    with open(os.path.join(OUT, "02B_liquids.json"), "w") as f:
        json.dump(liq_manifest, f, indent=1)
    info["finished"] = time.strftime("%F %T")
    with open(os.path.join(OUT, "prepare.json"), "w") as f:
        json.dump(info, f, indent=1, default=str)
    log(f"[02B] {len(blocks)} Li-side liquid blocks -> {CAL_LI}/input_liquid_li_gpu.yaml (Al side reused from {CAL_AL})")


# ----------------------------------------------------------------------------- addsolid
def addsolid():
    """addsolid <file> <phase> <kind> <x_Li> <supercell a,b,c> <mesh a,b,c>

    Relax one extra candidate (e.g. a Materials Project CIF) with the ACE
    potential, add it to the 0 K hull files (01_*) and to the solids manifest
    (02A_solids.json) with a new id; `solids` then computes only the new cells
    and `assemble` picks them up.
    """
    from ase.io import read, write
    from ftphase.validate import relax, hull_0K, compare_ground_states
    f, ph, kind, x = sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
    sc = [int(v) for v in sys.argv[6].split(",")]; mesh = [int(v) for v in sys.argv[7].split(",")] if "," in sys.argv[7] else float(sys.argv[7])
    calc = ace()
    at = read(f)
    r = relax(at, calc, fmax=1e-3, cell=True)
    log(f"[01] {ph:10s} E={r.energy_per_atom:.5f} eV/atom V={r.volume_per_atom:.3f}  {r.spacegroup_before} -> {r.spacegroup_after}  ({len(at)} atoms, {os.path.basename(f)})")
    relax_df = pd.read_csv(os.path.join(OUT, "01_relaxed.tsv"), sep="\t")
    relax_df = relax_df[relax_df.name != ph]
    relax_df = pd.concat([relax_df, pd.DataFrame([{"name": ph, "x": x, "e": r.energy_per_atom, "V": r.volume_per_atom, "sg_before": r.spacegroup_before, "sg_after": r.spacegroup_after,
                                                   "converged": r.converged, "transformed": r.transformed}])], ignore_index=True)
    hull = hull_0K(relax_df["name"], relax_df["x"], relax_df["e"])
    cmp = compare_ground_states(hull, ["fcc-Al", "bcc-Li", "B32-AlLi"])
    relax_df.to_csv(os.path.join(OUT, "01_relaxed.tsv"), sep="\t", index=False)
    hull.to_csv(os.path.join(OUT, "01_hull_0K.tsv"), sep="\t", index=False)
    cmp.to_csv(os.path.join(OUT, "01_ground_state_check.tsv"), sep="\t", index=False)
    log("[01] hull:\n" + hull.round(5).to_string(index=False))
    manifest = json.load(open(os.path.join(OUT, "02A_solids.json")))
    manifest = [m for m in manifest if m["phase"] != ph]
    k = max(m["id"] for m in manifest) + 1
    a0 = r.atoms.copy(); a0.calc = None
    fn = os.path.join(OUT, f"02A_solid_{k:02d}_{ph}_x{x:.4f}.extxyz")
    write(fn, a0, format="extxyz")
    manifest.append({"id": k, "phase": ph, "kind": kind, "x": x, "config": 0, "file": fn, "supercell": sc, "mesh": mesh, "scales": list(SC_FCC), "n_atoms": len(a0),
                     "counts": {e: a0.get_chemical_symbols().count(e) for e in sorted(set(a0.get_chemical_symbols()))}, "source_file": f})
    with open(os.path.join(OUT, "02A_solids.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    log(f"[02A] added solid id {k}: {ph} kind={kind} x={x} sc={sc} mesh={mesh}")


# ----------------------------------------------------------------------------- prepare_more
def prepare_more():
    """Liquid runs below 700 K and independent repeats, reusing the existing liquid cells.

    For every composition of 02B (Al side from example 5, Li side from this run):
      * lqd_x<x>_lo : ts 700 -> LOW_T_STOP[x] K (skipped where the liquid froze at 700 K already),
      * lqd_x<x>_r1, _r2 : ts 1100 -> 700 K (800 K for x = 0.1) with new random seeds.
    Written to calphy_liquid_more/input_liquid_more_gpu.yaml and out_full/02B_liquids_more.json.
    """
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    os.makedirs(CAL_MORE, exist_ok=True)
    al = json.load(open(os.path.join(OUT5, "02B_liquids.json")))
    li = json.load(open(os.path.join(OUT, "02B_liquids.json")))
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks, manifest = [], []
    for m in al + li:
        x = round(m["x_target"], 2)
        hi = [1100.0, 800.0 if abs(x - 0.1) < 1e-6 else 700.0]
        runs = [(f"lqd_x{x:.2f}_r{i}", hi) for i in range(1, N_REPEAT + 1)]
        if x in LOW_T_STOP:
            runs.append((f"lqd_x{x:.2f}_lo", [700.0, LOW_T_STOP[x]]))
        for tag, T in runs:
            blocks.append(calculation_block(tag, "ts", ["Al", "Li"], [26.9815, 6.94], m["data"], "pace", f"* * {POT} Al Li", T, pressure=0,
                                            reference_phase="liquid", n_equilibration_steps=10000, n_switching_steps=[10000, 10000], n_iterations=3,
                                            queue=q, folder_prefix=tag, gpu=True, lammps_executable=LMP_GPU))
            manifest.append({"tag": tag, "x_target": x, "x_actual": m["x_actual"], "data": m["data"], "T_sweep": T, "dir": CAL_MORE})
    write_series_input(os.path.join(CAL_MORE, "input_liquid_more_gpu.yaml"), blocks)
    with open(os.path.join(OUT, "02B_liquids_more.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    log(f"[02B] {len(blocks)} extra liquid runs -> {CAL_MORE}/input_liquid_more_gpu.yaml")


def _resume_manifest(manifest_path, cal_dir, yaml_name):
    import shutil
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    liq_manifest = json.load(open(manifest_path))
    override = {}
    if os.path.exists(os.path.join(cal_dir, "t_override.json")):
        override = json.load(open(os.path.join(cal_dir, "t_override.json")))
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks, todo = [], []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    queued = _queued_tags()
    for m in liq_manifest:
        tag = m["tag"]
        if _tag_queued(tag, queued):
            continue                      # still pending/running in Slurm: not unfinished
        if any(os.path.exists(os.path.join(d, "temperature_sweep.dat")) for d in glob.glob(os.path.join(cal_dir, f"{tag}-ts-*/"))):
            continue
        for path in glob.glob(os.path.join(cal_dir, f"{tag}-ts-*")):
            os.makedirs(os.path.join(cal_dir, "failed", stamp), exist_ok=True)
            shutil.move(path, os.path.join(cal_dir, "failed", stamp, os.path.basename(path)))
        T0 = m.get("T_sweep", T_LIQ)
        T = [T0[0], float(override.get(tag, T0[1]))]
        m["T_sweep"] = T
        blocks.append(calculation_block(tag, "ts", ["Al", "Li"], [26.9815, 6.94], m["data"], "pace", f"* * {POT} Al Li", T, pressure=0,
                                        reference_phase="liquid", n_equilibration_steps=10000, n_switching_steps=[10000, 10000], n_iterations=3,
                                        queue=q, folder_prefix=tag, gpu=True, lammps_executable=LMP_GPU))
        todo.append(tag)
    with open(manifest_path, "w") as f:
        json.dump(liq_manifest, f, indent=1)
    if blocks:
        write_series_input(os.path.join(cal_dir, yaml_name), blocks)
    return todo, override


def resume_more():
    todo, override = _resume_manifest(os.path.join(OUT, "02B_liquids_more.json"), CAL_MORE, "input_liquid_more_gpu_resume.yaml")
    log(f"[resume] unfinished extra liquids: {todo} (overrides {override})")
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
    override = {}
    if os.path.exists(os.path.join(CAL_LI, "t_override.json")):
        override = json.load(open(os.path.join(CAL_LI, "t_override.json")))
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks, todo = [], []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    queued = _queued_tags()
    for m in liq_manifest:
        tag = m["tag"]
        if _tag_queued(tag, queued):
            continue                      # still pending/running in Slurm: not unfinished
        if any(os.path.exists(os.path.join(d, "temperature_sweep.dat")) for d in glob.glob(os.path.join(CAL_LI, f"{tag}-ts-*/"))):
            continue
        for path in glob.glob(os.path.join(CAL_LI, f"{tag}-ts-*")):
            os.makedirs(os.path.join(CAL_LI, "failed", stamp), exist_ok=True)
            shutil.move(path, os.path.join(CAL_LI, "failed", stamp, os.path.basename(path)))
        T = [T_LIQ[0], float(override.get(tag, T_LIQ[1]))]
        m["T_sweep"] = T
        blocks.append(calculation_block(tag, "ts", ["Al", "Li"], [26.9815, 6.94], m["data"], "pace", f"* * {POT} Al Li", T, pressure=0,
                                        reference_phase="liquid", n_equilibration_steps=10000, n_switching_steps=[10000, 10000], n_iterations=3,
                                        queue=q, folder_prefix=tag, gpu=True, lammps_executable=LMP_GPU))
        todo.append(tag)
    with open(os.path.join(OUT, "02B_liquids.json"), "w") as f:
        json.dump(liq_manifest, f, indent=1)
    if blocks:
        write_series_input(os.path.join(CAL_LI, "input_liquid_li_gpu_resume.yaml"), blocks)
    log(f"[resume] unfinished Li-side liquids: {todo} (overrides {override})")
    print("RESUME_TODO", " ".join(todo))


# ----------------------------------------------------------------------------- solids
def solids():
    from ase.io import read
    from ftphase.validate import relax
    from ftphase.qha import phonopy_volume_scan
    from ftphase.records import FreeEnergyTable

    calc = ace()
    manifest = json.load(open(os.path.join(OUT, "02A_solids.json")))
    if os.environ.get("TX_SOLIDS_SUBSET"):           # smoke test: comma-separated ids
        keep = {int(v) for v in os.environ["TX_SOLIDS_SUBSET"].split(",")}
        manifest = [m for m in manifest if m["id"] in keep]
    status_path = os.path.join(OUT, "03A_status.json")
    status = json.load(open(status_path)) if os.path.exists(status_path) else []
    done = {s["id"] for s in status if s.get("ok")}
    rows = []
    old = FreeEnergyTable.from_tsv(os.path.join(OUT, "03A_qha_solids.tsv")).df if done and os.path.exists(os.path.join(OUT, "03A_qha_solids.tsv")) else None
    if old is not None:
        rows = old.to_dict("records")
    t0 = time.time()
    for m in manifest:
        if m["id"] in done:
            continue
        at = read(m["file"])
        t1 = time.time()
        try:
            r = relax(at, calc, fmax=1e-3, cell=True, hydrostatic=True)
            a0 = r.atoms.copy(); a0.calc = None
            res, data = phonopy_volume_scan(a0, calc, np.diag(m["supercell"]), T_QHA, scales=tuple(m["scales"]), mesh=(tuple(m["mesh"]) if isinstance(m["mesh"], list) else float(m["mesh"])), imaginary="drop", eos="vinet")
            G, V = res.per_atom()
            i1 = int(np.argmin(np.abs(np.asarray(m["scales"]) - 1.0)))
            hw, w = data["frequencies"][i1]
            np.savez(os.path.join(OUT, f"03A_freq_{m['id']:02d}.npz"), hw_eV=hw, weights=w, n_atoms=len(a0), volumes=data["volumes"], e0=data["e0"], f_vib=data["f_vib"], T=T_QHA)
            for T, g, v in zip(T_QHA, G, V):
                rows.append({"phase": m["phase"], "kind": m["kind"], "x": m["x"], "T": float(T), "P_GPa": 0.0, "G": float(g), "G_err": 0.0, "V": float(v), "model": MODEL,
                             "reference_state": "absolute ACE energy", "method": f"QHA vinet {len(m['scales'])} volumes, phonopy sc={m['supercell']} mesh={m['mesh']}, quantum; {m['n_atoms']}-atom cell",
                             "config_entropy": "none", "quantum": "quantum", "n_atoms": len(a0), "source": f"alli_ace_txdiagram_full solid {m['id']}"})
            st = {"id": m["id"], "phase": m["phase"], "x": m["x"], "ok": True, "E0_eV_per_atom": r.energy_per_atom, "V0": r.volume_per_atom, "sg": f"{r.spacegroup_before}->{r.spacegroup_after}",
                  "G300": float(np.interp(300, T_QHA, G)), "V1100": float(V[-1]), "n_imag_dropped": int(np.sum(hw < 0)), "seconds": time.time() - t1}
            log(f"[03A] {m['id']:02d} {m['phase']} x={m['x']:.4f}: G(300)={st['G300']:.5f} V(1100)={st['V1100']:.3f} {st['sg']} {st['seconds']:.0f}s")
        except Exception as e:
            st = {"id": m["id"], "phase": m["phase"], "x": m["x"], "ok": False, "error": repr(e), "seconds": time.time() - t1}
            log(f"[03A] {m['id']:02d} FAILED: {e!r}")
        status = [s for s in status if s["id"] != m["id"]] + [st]
        with open(status_path, "w") as f:
            json.dump(status, f, indent=1, default=str)
        FreeEnergyTable.from_rows(rows, {"potential": POT, "stage": "03A quantum QHA, fixed configurations (SQS)"}).to_tsv(os.path.join(OUT, "03A_qha_solids.tsv"))
    log(f"[03A] done: {sum(1 for s in status if s['ok'])}/{len(manifest)} cells in {time.time()-t0:.0f} s")


# ----------------------------------------------------------------------------- assemble
def assemble():
    import matplotlib
    matplotlib.use("Agg")
    from ftphase.records import FreeEnergyTable
    from ftphase.quantum import quantum_minus_classical
    from ftphase.configurational import b32_antisite_site_fractions
    from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table, fit_residuals
    from ftphase.diagram import scan, invariants, sensitivity, plot_tx, write_records
    from ftphase.calphy_io import read_calphy_results

    summary = {"started": time.strftime("%F %T")}
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
        g["method"] = g["method"] + "; lowered by F_q-F_cl (harmonic, frequencies at the 0 K volume)"
        parts.append(g)
    sol = pd.concat(parts).drop(columns=["sid"])

    # liquids: Al side (example 5) + Li side (this run)
    liqs = []
    for d in (CAL_AL, CAL_LI, CAL_MORE):
        if not os.path.isdir(d):
            continue
        try:
            df = read_calphy_results(d, reference_element="Li", model=MODEL, source_prefix=os.path.basename(d) + "/").df
            df = df[df["config_entropy"] == "liquid-ti"].copy()
            liqs.append(df)
        except Exception as e:
            summary.setdefault("liquid_errors", []).append(f"{d}: {e!r}")
    liq = pd.concat(liqs, ignore_index=True) if liqs else pd.DataFrame()
    if liq.empty:
        raise SystemExit("no finished liquid runs: " + str(summary))
    liq["phase"] = "liquid"; liq["reference_state"] = "absolute ACE energy"
    liq["x"] = liq["x"].round(4)
    # independent runs of the same composition (r1, r2, ...) and the low-T sweep overlap on the T grid:
    # average G per (x, T), keep the run-to-run spread as the statistical error (calphy's own error is
    # only the reference-free-energy error and is 0.1-0.4 meV/atom here)
    summary["liquid_runs"] = liq.groupby("x")["source"].nunique().to_dict()
    liq["T"] = liq["T"].round(1)
    g = liq.groupby(["x", "T"])
    agg = g.agg(G=("G", "mean"), G_std=("G", "std"), G_err0=("G_err", "mean"), n=("G", "size")).reset_index()
    agg["G_std"] = agg["G_std"].fillna(0.0)
    agg["G_err"] = np.sqrt(agg["G_err0"] ** 2 + (agg["G_std"] / np.sqrt(agg["n"].clip(lower=1))) ** 2)
    first = g.first().reset_index()
    liq = first.drop(columns=["G", "G_err"]).merge(agg[["x", "T", "G", "G_err", "n"]], on=["x", "T"])
    liq["method"] = liq["method"] + liq["n"].map(lambda k: f"; mean of {k} runs" if k > 1 else "")
    spread = liq[np.isclose(liq["T"], 900.0)].groupby("x")["G_err"].mean()
    summary["liquid_G_err_900K_meV"] = {f"{x:.4f}": float(v * 1000) for x, v in spread.items()}
    liq = liq.drop(columns=["n"])
    summary["liquid_x_available"] = sorted(float(v) for v in liq["x"].unique())
    summary["liquid_T_range"] = {f"{x:.4f}": [float(a), float(b)] for x, (a, b) in liq.groupby("x")["T"].agg(["min", "max"]).iterrows()}

    allrows = pd.concat([sol, liq], ignore_index=True)
    for ph, g in allrows.groupby("phase"):
        if g["kind"].iloc[0] != "point" and g["x"].nunique() < 2:
            allrows.loc[allrows.phase == ph, "kind"] = "point"
            summary.setdefault("degraded_to_point", []).append(ph)
    tab = FreeEnergyTable.from_rows(allrows.to_dict("records"), {"potential": POT, "pressure_GPa": 0.0, "level": "classical"})
    for ph in ("fcc", "bcc"):
        if ph in set(tab.df.phase):
            tab = add_configurational_term(tab, ph, "ideal")
    if "B32" in set(tab.df.phase) and tab.df[tab.df.phase == "B32"]["x"].nunique() > 1:
        tab = add_configurational_term(tab, "B32", "sublattice", site_model=b32_antisite_site_fractions)
    summary["table_check"] = [str(w) for w in tab.check()]
    tab.to_tsv(os.path.join(OUT, "05_free_energies.tsv"))
    ti = interpolate_T(tab, T_DIAG_MORE)
    # keep only temperatures where the liquid covers the whole range 0..1 (else the hull would see a truncated liquid)
    liq_xmin, liq_xmax = liq["x"].min(), liq["x"].max()
    cover = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["min", "max", "size"])
    ok_T = cover[(cover["min"] <= liq_xmin + 1e-6) & (cover["max"] >= liq_xmax - 1e-6) & (cover["size"] >= 6)].index
    ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(ok_T)], ti.meta)
    Ts = np.array(sorted(ti.df["T"].unique()))
    summary["T_grid"] = [float(Ts.min()), float(Ts.max()), int(Ts.size)]
    summary["liquid_T_min_K"] = {f"{x:.3f}": float(g["T"].min()) for x, g in liq.groupby("x")}
    FITS = {"fcc": "poly", "bcc": "poly", "liquid": "rk", "B32": "spline"}
    HULL = {"min_width": 0.005, "gap_tol": 2.5}
    # liquid: 11 compositions over 0-1 with both pure ends -> ideal mixing + 4-term Redlich-Kister (CALPHAD
    # liquid model; a plain cubic left 4 meV/atom rmse and spurious liquid+liquid gaps); fcc/bcc: 5 points -> cubic excess
    builder = builder_from_table(ti, fit="spline", fits=FITS, poly_order=3, poly_orders={"liquid": 4})
    resid = fit_residuals(builder, 900.0)
    resid.to_csv(os.path.join(OUT, "06_fit_residuals_900K.tsv"), sep="\t", index=False)
    reg = scan(builder, Ts, **HULL)
    inv = invariants(reg)
    write_records(os.path.join(OUT, "07_two_phase_regions.tsv"), reg, {"example": "alli_ace_txdiagram_full", "fit": str(FITS) + " (liquid: ideal + 4-term Redlich-Kister; fcc/bcc: cubic excess over ideal mixing)", "hull": str(HULL), "T_step": 10.0,
                                                                       "level": "classical (QHA lowered by F_q-F_cl)", "liquid": "calphy ts GPU, UFM, 3 iterations", "solids": "QHA, 64-atom SQS (fcc, bcc), B32 16-atom, Al3Li 4-atom"})
    inv.to_csv(os.path.join(OUT, "07_invariants.tsv"), sep="\t", index=False)
    sig = {ph: 0.002 for ph in set(ti.df.phase) if ph != "liquid"}
    sig["liquid"] = float(max(0.0014, spread.mean())) if len(spread) else 0.0014   # measured run-to-run spread once repeats exist
    summary["sigma_used_eV"] = sig
    sens = sensitivity(builder, Ts[::2], sig, n_samples=30, rng=0, **HULL)
    sens.table.to_csv(os.path.join(OUT, "07_sensitivity.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Li", dT=10.0)
    ax.set_xlim(0.0, 1.0)
    ax.set_title("ACE Al-Li, 0 GPa: QHA solids (64-atom SQS, classical level) + calphy GPU liquid", fontsize=9)
    ax.figure.savefig(os.path.join(OUT, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")

    # ---- key numbers and the noise comparison with example 5
    summary["invariants"] = inv.to_dict("records")
    for T in (700.0, 800.0, 900.0, 1000.0):
        summary[f"regions_at_{int(T)}K"] = reg[np.isclose(reg["T"], T)][["phase_a", "x_a", "phase_b", "x_b"]].round(4).to_dict("records")
    liqreg = reg[(reg.phase_a == "liquid") | (reg.phase_b == "liquid")]
    if not liqreg.empty:
        summary["lowest_T_with_liquid_K"] = float(liqreg["T"].min())
        summary["coexistence_at_that_T"] = liqreg[liqreg["T"] == liqreg["T"].min()][["phase_a", "x_a", "phase_b", "x_b"]].round(4).to_dict("records")
    fl = reg[(reg.phase_a == "fcc") & (reg.phase_b == "liquid")]
    summary["fcc_liquidus_highest_T_K"] = float(fl["T"].max()) if not fl.empty else None
    summary["fit_rmse_900K"] = resid.to_dict("records")
    noise = []
    p5 = os.path.join(OUT5, "05_free_energies.tsv")
    if os.path.exists(p5):
        t5 = FreeEnergyTable.from_tsv(p5).df
        for x in FCC_X:
            a = tab.df[(tab.df.phase == "fcc") & np.isclose(tab.df.x, x, atol=2e-3) & np.isclose(tab.df["T"], 800.0)]
            b = t5[(t5.phase == "fcc") & np.isclose(t5.x, x, atol=2e-3) & np.isclose(t5["T"], 800.0)]
            if not a.empty and not b.empty:
                noise.append({"x": x, "G_sqs64_800K": float(a["G"].iloc[0]), "G_random32_mean_800K": float(b["G"].iloc[0]), "random32_half_spread_meV": float(b["G_err"].iloc[0] * 1000),
                              "sqs64_minus_random32_meV": float((a["G"].iloc[0] - b["G"].iloc[0]) * 1000)})
    summary["fcc_sqs64_vs_random32_800K"] = noise
    summary["finished"] = time.strftime("%F %T")
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str, ensure_ascii=False)
    write_report(summary, reg, sens.table)
    log(json.dumps({k: summary[k] for k in ("lowest_T_with_liquid_K", "coexistence_at_that_T", "fcc_liquidus_highest_T_K", "liquid_x_available", "solids_failed") if k in summary}, ensure_ascii=False, default=str))


def write_report(summary, reg, sens):
    """REPORT.md: what a reader needs without rerunning anything."""
    L = ["# Example 6: ACE Al-Li full-range T-x diagram (classical level, 0 GPa)", "",
         f"Assembled {summary['finished']}.  Files: out_full/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.", ""]
    L += ["## Inputs", "", "* solids: QHA of 64-atom icet SQS (fcc x = 0-0.25, bcc x = 0.75-1), B32 16-atom with anti-sites (x = 7/16, 1/2, 9/16), L1_2 Al3Li; quantum QHA lowered to the classical level with F_q-F_cl.",
      "* liquids: calphy reversible scaling 1100 -> 700 K plus (calphy_liquid_more/) 700 -> 650/500 K sweeps and 2 independent repeats per composition, averaged per (x, T); UFM, 3 iterations, LAMMPS KOKKOS/CUDA (x <= 0.5 from example 5, x >= 0.6 new, " + ", ".join(f"{v:.3f}" for v in summary.get("liquid_x_available", [])) + ").",
      "* configurational terms: ideal mixing (fcc, bcc), two-sublattice anti-site model (B32), none (Al3Li).", "* fits: cubic polynomial of the excess over the analytic ideal-mixing term (fcc, bcc, liquid), natural spline (B32).", ""]
    if summary.get("solids_failed"):
        L += ["**Failed solid cells:** " + "; ".join(f"{s['phase']} x={s['x']}: {s.get('error','')[:120]}" for s in summary["solids_failed"]), ""]
    if summary.get("liquid_errors"):
        L += ["**Liquid read errors:** " + "; ".join(summary["liquid_errors"]), ""]
    if "T_grid" in summary:
        L += [f"Temperature grid: {summary['T_grid'][0]:.0f}-{summary['T_grid'][1]:.0f} K ({summary['T_grid'][2]} points); liquid runs per composition: {summary.get('liquid_runs')}; sigma used in the Monte Carlo (eV/atom): {summary.get('sigma_used_eV')}", ""]
    L += ["## Key numbers", ""]
    if "lowest_T_with_liquid_K" in summary:
        L += [f"* lowest temperature with liquid on the grid: {summary['lowest_T_with_liquid_K']:.0f} K; coexistences there: " + "; ".join(f"{c['phase_a']}({c['x_a']:.3f}) + {c['phase_b']}({c['x_b']:.3f})" for c in summary["coexistence_at_that_T"])]
    if summary.get("fcc_liquidus_highest_T_K"):
        L += [f"* highest temperature with fcc + liquid (Al melting bracket on a 10 K grid): {summary['fcc_liquidus_highest_T_K']:.0f} K"]
    L += ["* invariant reactions (pairs change between T_low and T_high):"]
    for r in summary.get("invariants", []):
        L += [f"  * {r['T_low']:.0f}-{r['T_high']:.0f} K: {r['pairs_below']} -> {r['pairs_above']}"]
    for T in (700, 800, 900, 1000):
        rr = summary.get(f"regions_at_{T}K", [])
        L += [f"* two-phase regions at {T} K: " + ("; ".join(f"{c['phase_a']}({c['x_a']:.3f})-{c['phase_b']}({c['x_b']:.3f})" for c in rr) if rr else "none (single phase everywhere)")]
    same = reg[reg.phase_a == reg.phase_b].copy()
    if not same.empty:
        same["w"] = same.x_b - same.x_a
        L += ["", "## Same-phase segments (fit noise, not phase boundaries)", "",
              "The lower hull of one fitted curve shows a 'gap' where the curve is slightly concave.  Segments that keep the same x in every Monte Carlo sample (std 0 below) come from the curvature of the fit through the sampled points, i.e. from the 1-2 meV/atom statistical noise of the free energies, not from the physics.  Treat them as noise unless they are wide (> 0.1 in x) and survive a denser composition grid.", ""]
        for (pa, lo_, hi_), g in same.groupby(["phase_a", same.x_a.round(2), same.x_b.round(2)]):
            L += [f"* {pa}+{pa} x = {lo_:.3f}-{hi_:.3f} (width {g['w'].mean():.3f}) at T = {g['T'].min():.0f}-{g['T'].max():.0f} K ({len(g)} temperatures)"]
    L += ["", "## Error bands (Monte Carlo, sigma = 2 meV/atom solids, 1.4 meV/atom liquid, 30 samples)", ""]
    try:
        avail = np.unique(np.asarray(sens["T"], dtype=float))
        for T in sorted({avail[np.argmin(np.abs(avail - t))] for t in (700.0, 770.0, 850.0)}):  # nearest sampled T (sensitivity uses every 2nd grid point)
            s = sens[np.isclose(sens["T"], T)]
            for _, r in s.iterrows():
                L += [f"* {T:.0f} K {r['pair']}: x_a = {r['x_a_mean']:.3f} +/- {r['x_a_std']:.3f}, x_b = {r['x_b_mean']:.3f} +/- {r['x_b_std']:.3f} (found in {int(r['n_found'])}/{int(r['n_samples'])} samples)"]
    except Exception as e:  # pragma: no cover
        L += [f"(sensitivity table not readable: {e!r})"]
    L += ["", "## Configurational noise: 64-atom SQS (this run) vs mean of two 32-atom random cells (example 5), fcc at 800 K", ""]
    for n in summary.get("fcc_sqs64_vs_random32_800K", []):
        L += [f"* x = {n['x']:.4f}: G_SQS64 - G_random32 = {n['sqs64_minus_random32_meV']:+.2f} meV/atom (random-cell half spread {n['random32_half_spread_meV']:.2f} meV/atom)"]
    phases = sorted(set(reg.phase_a) | set(reg.phase_b))
    inter = [ph for ph in ("Al2Li3", "Al4Li9") if ph in set(pd.read_csv(os.path.join(OUT, "05_free_energies.tsv"), sep="\t").phase)]
    L += ["", "## Caveats", "", ("* Li-rich intermetallics included as point phases: " + ", ".join(inter) + " (Materials Project CIFs, structures/README.md); phases appearing in the diagram: " + ", ".join(phases)) if inter else "* Li-rich intermetallics Al2Li3 and Al4Li9 are not included; the Li side is B32 + bcc + liquid only.",
          (f"* Nothing below {summary['T_grid'][0]:.0f} K is shown: the grid keeps only temperatures where the liquid has both pure ends and at least 6 compositions (QHA solids exist down to 0 K). Lowest liquid temperature per x: " + ", ".join(f"{x} K={T:.0f}" for x, T in summary.get("liquid_T_min_K", {}).items()) + "." if "T_grid" in summary else "* Nothing below 700 K is computed (QHA solids exist down to 0 K, liquids only 700-1100 K)."), "* Example 5 found ACE temperatures about 100 K below experiment with the right composition features; compare the eutectic here with 873 K / x = 0.30.",
          "* Table check warnings: " + "; ".join(summary.get("table_check", [])) + " (the quantum/classical mix is intended: every phase is on the classical level after the correction).", ""]
    with open(os.path.join(OUT, "REPORT.md"), "w") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    {"prepare": prepare, "prepare_more": prepare_more, "resume": resume, "resume_more": resume_more, "solids": solids, "assemble": assemble, "addsolid": addsolid}[sys.argv[1]]()
