"""Example 5: a T-x diagram of ACE Al-Li (Al-rich half, x_Li <= 0.5) that starts at
stage 01 and runs through 07, executed as Slurm jobs (see run_pipeline.sh).

Stages and where they run
  prepare  (login node, seconds)   01/02A/02B: relax the 0 K candidates, 0 K hull and
                                   ground-state check, fcc composition series (32-atom
                                   cells, 2 random configurations per x), B32 anti-site
                                   cells, liquid cells (256 atoms), calphy GPU input.
  solids   (CPU Slurm job)         03A: phonopy volume scan + QHA for every solid cell
                                   (quantum); phonon frequencies saved for 04B.
  calphy   (GPU Slurm jobs)        03B: liquid reversible scaling 1100 -> 700 K at
                                   x = 0 .. 0.5, UFM reference, 3 iterations,
                                   LAMMPS KOKKOS/CUDA (env/lammps-gpu/bin/lmp_gpu).
  assemble (CPU Slurm job, after all of the above)
                                   04B: QHA solids lowered to the classical level with
                                   F_q - F_cl from their own frequencies;
                                   04A: ideal mixing for fcc, two-sublattice anti-site
                                   model for B32, nothing for the Al3Li point phase;
                                   05: one FreeEnergyTable (absolute ACE energies, 0 GPa);
                                   06/07: lower convex hull per T, invariants, Monte Carlo
                                   error bands, T-x plot, records.

Everything is written under out/ and calphy_liquid/.  Each step is idempotent
and re-reads the previous step's files, so the chain survives the session that
launched it: Slurm runs the jobs, nothing waits on this process.

Potential: AlLi-6gen-18May.yace (pyiron potentials-workshop-2022; Menon et al.
2024).  Known limitation of this cheap setting: 5000-10000 switching steps and
32-atom solid cells; the error bands in out/ use the measured run-to-run spread
(1.4 meV/atom, examples/alli_ace_gpu_compare.py) and 2 meV/atom for QHA.
"""

import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POT = os.path.join(ROOT, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace")
LMP_GPU = os.path.join(ROOT, "env/lammps-gpu/bin/lmp_gpu")
ENV = os.path.join(ROOT, "env/ftphase")
OUT = os.path.join(HERE, "out")
CAL = os.path.join(HERE, "calphy_liquid")
MODEL = "AlLi-6gen-18May.yace (ACE)"

FCC_X = [0.0625, 0.125, 0.1875, 0.25]      # 2, 4, 6, 8 Li in 32 atoms
N_CONFIG = 2
LIQ_X = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
T_QHA = np.arange(0.0, 1101.0, 25.0)
T_DIAG = np.arange(700.0, 1100.1, 10.0)
T_LIQ = [1100.0, 700.0]                      # calphy sweeps downwards from the stable liquid


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def ace():
    from ase.calculators.lammpslib import LAMMPSlib
    return LAMMPSlib(lmpcmds=["pair_style pace", f"pair_coeff * * {POT} Al Li"], atom_types={"Al": 1, "Li": 2}, keep_alive=True, log_file=None)


def b32_alli(a=6.37):
    from ase.spacegroup import crystal
    return crystal(["Al", "Li"], [(0, 0, 0), (0.5, 0.5, 0.5)], spacegroup=227, cellpar=[a, a, a, 90, 90, 90])


def l12_al3li(a=4.0):
    from ase import Atoms
    return Atoms("LiAl3", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)], cell=[a, a, a], pbc=True)


# ----------------------------------------------------------------------------- prepare
def prepare():
    from ase.build import bulk
    from ase.io import write
    from ftphase.validate import relax, hull_0K, compare_ground_states
    from ftphase.structures import composition_series, write_lammps_data
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input, gpu_capability

    os.makedirs(OUT, exist_ok=True); os.makedirs(CAL, exist_ok=True)
    calc = ace()
    info = {"potential": POT, "started": time.strftime("%F %T")}

    # ---- 01: candidates, relax, hull
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
    log("[01] hull:\n" + hull.round(5).to_string(index=False))

    # ---- 02A: solid cells for QHA (phase, kind, x, config, atoms, supercell, mesh)
    solids = []
    fcc = relaxed["fcc-Al"].atoms.copy(); fcc.calc = None
    base = fcc.repeat((2, 2, 2))                            # 32 atoms
    solids.append(("fcc", "solution", 0.0, 0, base.copy(), [2, 2, 2], [6, 6, 6]))
    for m in composition_series(base, "Li", FCC_X, seed=0, n_configs=N_CONFIG):
        cfg = m.seed
        solids.append(("fcc", "solution", m.x_actual, cfg, m.atoms.copy(), [2, 2, 2], [6, 6, 6]))
    al3li = relaxed["L12-Al3Li"].atoms.copy(); al3li.calc = None
    solids.append(("Al3Li", "point", 0.25, 0, al3li, [3, 3, 3], [12, 12, 12]))
    b32 = relaxed["B32-AlLi"].atoms.copy(); b32.calc = None   # 16 atoms, 8 Al + 8 Li
    solids.append(("B32", "limited", 0.5, 0, b32.copy(), [2, 2, 2], [8, 8, 8]))
    syms = b32.get_chemical_symbols()
    i_li = [i for i, s in enumerate(syms) if s == "Li"][0]; i_al = [i for i, s in enumerate(syms) if s == "Al"][0]
    b32_alrich = b32.copy(); b32_alrich[i_li].symbol = "Al"      # x = 7/16: Al anti-site on the Li sublattice
    b32_lirich = b32.copy(); b32_lirich[i_al].symbol = "Li"      # x = 9/16: Li anti-site on the Al sublattice
    solids.append(("B32", "limited", 7 / 16, 0, b32_alrich, [2, 2, 2], [8, 8, 8]))
    solids.append(("B32", "limited", 9 / 16, 0, b32_lirich, [2, 2, 2], [8, 8, 8]))
    manifest = []
    for k, (ph, kind, x, cfg, at, sc, mesh) in enumerate(solids):
        fn = os.path.join(OUT, f"02A_solid_{k:02d}_{ph}_x{x:.4f}_c{cfg}.extxyz")
        write(fn, at, format="extxyz")
        manifest.append({"id": k, "phase": ph, "kind": kind, "x": float(x), "config": int(cfg), "file": fn, "supercell": sc, "mesh": mesh, "n_atoms": len(at),
                         "counts": {e: at.get_chemical_symbols().count(e) for e in sorted(set(at.get_chemical_symbols()))}})
    with open(os.path.join(OUT, "02A_solids.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    log(f"[02A] {len(manifest)} solid cells written")

    # ---- 02B + calphy input (03B) on the GPU
    cap = gpu_capability(LMP_GPU)
    info["lmp_gpu"] = cap
    if not cap["all_modes"]:
        raise SystemExit(f"{LMP_GPU} cannot run calphy liquids on the GPU: {cap}")
    liq_base = fcc.repeat((4, 4, 4))                         # 256 atoms
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks, liq_manifest = [], []
    for m in composition_series(liq_base, "Li", LIQ_X, seed=100, n_configs=1):
        tag = f"lqd_x{m.x_target:.2f}"
        data = write_lammps_data(m.atoms, os.path.join(CAL, f"{tag}_256.data"), ["Al", "Li"])
        blocks.append(calculation_block(tag, "ts", ["Al", "Li"], [26.9815, 6.94], data, "pace", f"* * {POT} Al Li", T_LIQ, pressure=0,
                                        reference_phase="liquid", n_equilibration_steps=10000, n_switching_steps=[10000, 10000], n_iterations=3,
                                        queue=q, folder_prefix=tag, gpu=True, lammps_executable=LMP_GPU))
        liq_manifest.append({"tag": tag, "x_target": m.x_target, "x_actual": m.x_actual, "counts": m.counts, "seed": m.seed, "data": data})
    write_series_input(os.path.join(CAL, "input_liquid_gpu.yaml"), blocks)
    with open(os.path.join(OUT, "02B_liquids.json"), "w") as f:
        json.dump(liq_manifest, f, indent=1)
    info["finished"] = time.strftime("%F %T")
    with open(os.path.join(OUT, "prepare.json"), "w") as f:
        json.dump(info, f, indent=1, default=str)
    log(f"[02B] {len(blocks)} liquid calphy blocks -> {CAL}/input_liquid_gpu.yaml")




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
    """Re-create calphy input for the liquid compositions without a finished sweep.

    A finished run has <folder>/temperature_sweep.dat.  Unfinished folders (killed
    jobs, SolidifiedError, ...) are moved to calphy_liquid/failed/<time>/ because
    calphy refuses to reuse a folder.  calphy_liquid/t_override.json may map a tag
    to a different sweep end temperature, e.g. {"lqd_x0.10": 800.0} when the liquid
    solidified at the original 700 K; the override is recorded in 02B_liquids.json.
    """
    import shutil
    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input

    liq_manifest = json.load(open(os.path.join(OUT, "02B_liquids.json")))
    override = {}
    if os.path.exists(os.path.join(CAL, "t_override.json")):
        override = json.load(open(os.path.join(CAL, "t_override.json")))
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks, todo = [], []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    queued = _queued_tags()
    for m in liq_manifest:
        tag = m["tag"]
        done = [d for d in glob.glob(os.path.join(CAL, f"{tag}-ts-*/")) if os.path.exists(os.path.join(d, "temperature_sweep.dat"))]
        if done:
            continue
        failed_dir = os.path.join(CAL, "failed", stamp)
        for path in glob.glob(os.path.join(CAL, f"{tag}-ts-*")):
            os.makedirs(failed_dir, exist_ok=True)
            shutil.move(path, os.path.join(failed_dir, os.path.basename(path)))
        T = [T_LIQ[0], float(override.get(tag, T_LIQ[1]))]
        m["T_sweep"] = T
        blocks.append(calculation_block(tag, "ts", ["Al", "Li"], [26.9815, 6.94], m["data"], "pace", f"* * {POT} Al Li", T, pressure=0,
                                        reference_phase="liquid", n_equilibration_steps=10000, n_switching_steps=[10000, 10000], n_iterations=3,
                                        queue=q, folder_prefix=tag, gpu=True, lammps_executable=LMP_GPU))
        todo.append(tag)
    with open(os.path.join(OUT, "02B_liquids.json"), "w") as f:
        json.dump(liq_manifest, f, indent=1)
    if blocks:
        write_series_input(os.path.join(CAL, "input_liquid_gpu_resume.yaml"), blocks)
    log(f"[resume] unfinished liquids: {todo} (overrides {override})")
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
    rows, status = [], []
    t0 = time.time()
    for m in manifest:
        at = read(m["file"])
        t1 = time.time()
        try:
            r = relax(at, calc, fmax=1e-3, cell=True, hydrostatic=True)
            a0 = r.atoms.copy(); a0.calc = None
            res, data = phonopy_volume_scan(a0, calc, np.diag(m["supercell"]), T_QHA, scales=(0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05),
                                            mesh=tuple(m["mesh"]), imaginary="drop", eos="vinet")
            G, V = res.per_atom()
            hw, w = data["frequencies"][3]
            np.savez(os.path.join(OUT, f"03A_freq_{m['id']:02d}.npz"), hw_eV=hw, weights=w, n_atoms=len(a0), volumes=data["volumes"], e0=data["e0"], f_vib=data["f_vib"], T=T_QHA)
            for T, g, v in zip(T_QHA, G, V):
                rows.append({"phase": m["phase"], "kind": m["kind"], "x": m["x"], "T": float(T), "P_GPa": 0.0, "G": float(g), "G_err": 0.0, "V": float(v), "model": MODEL,
                             "reference_state": "absolute ACE energy", "method": f"QHA vinet 9 volumes, phonopy sc={m['supercell']} mesh={m['mesh']}, quantum; config {m['config']}",
                             "config_entropy": "none", "quantum": "quantum", "n_atoms": len(a0), "source": f"alli_ace_txdiagram solid {m['id']}"})
            st = {"id": m["id"], "phase": m["phase"], "x": m["x"], "config": m["config"], "ok": True, "E0_eV_per_atom": r.energy_per_atom, "V0": r.volume_per_atom,
                  "sg": f"{r.spacegroup_before}->{r.spacegroup_after}", "transformed": r.transformed, "G300": float(np.interp(300, T_QHA, G)), "V1000": float(V[-1]),
                  "n_imag_dropped": int(np.sum(hw < 0)), "seconds": time.time() - t1}
            log(f"[03A] {m['id']:02d} {m['phase']} x={m['x']:.4f} c{m['config']}: G(300)={st['G300']:.5f} V(1000)={st['V1000']:.3f} {st['sg']} {st['seconds']:.0f}s")
        except Exception as e:
            st = {"id": m["id"], "phase": m["phase"], "x": m["x"], "config": m["config"], "ok": False, "error": repr(e), "seconds": time.time() - t1}
            log(f"[03A] {m['id']:02d} FAILED: {e!r}")
        status.append(st)
        with open(os.path.join(OUT, "03A_status.json"), "w") as f:
            json.dump(status, f, indent=1, default=str)
    FreeEnergyTable.from_rows(rows, {"potential": POT, "stage": "03A quantum QHA, fixed configurations"}).to_tsv(os.path.join(OUT, "03A_qha_solids.tsv"))
    log(f"[03A] done: {sum(1 for s in status if s['ok'])}/{len(status)} cells in {time.time()-t0:.0f} s")


# ----------------------------------------------------------------------------- assemble
def assemble():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ftphase.records import FreeEnergyTable
    from ftphase.quantum import quantum_minus_classical
    from ftphase.configurational import b32_antisite_site_fractions
    from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table, fit_residuals
    from ftphase.diagram import scan, invariants, sensitivity, plot_tx, write_records
    from ftphase.calphy_io import read_calphy_results

    summary = {"started": time.strftime("%F %T")}
    # ---- 03A solids (quantum) -> 04B classical level
    sol = FreeEnergyTable.from_tsv(os.path.join(OUT, "03A_qha_solids.tsv")).df
    status = json.load(open(os.path.join(OUT, "03A_status.json")))
    ok_ids = {s["id"] for s in status if s["ok"]}
    sol = sol[sol.source.str.extract(r"solid (\d+)")[0].astype(int).isin(ok_ids)].copy()
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
    sol = pd.concat(parts)
    # average the random configurations of the fcc solution at each x (mean, half-range as error)
    agg = []
    for (ph, x, T), g in sol.groupby(["phase", "x", "T"]):
        r = g.iloc[0].to_dict()
        r["G"] = float(g["G"].mean()); r["G_err"] = float((g["G"].max() - g["G"].min()) / 2) if len(g) > 1 else 0.0
        r["V"] = float(g["V"].mean()); r["source"] = f"alli_ace_txdiagram {ph} x={x:.4f} ({len(g)} configs)"
        r["method"] = r["method"].split("; config")[0] + f"; mean of {len(g)} configurations; lowered by F_q-F_cl (harmonic)"
        agg.append(r)
    sol = pd.DataFrame(agg).drop(columns=["sid"], errors="ignore")
    summary["config_spread_meV_max"] = float(sol["G_err"].max() * 1000)

    # ---- 03B liquids (classical, calphy, GPU)
    liq = None
    try:
        cal_dir = os.environ.get("TX_CAL_DIR", CAL)   # smoke test: point at another calphy folder
        liq = read_calphy_results(cal_dir, reference_element="Li", model=MODEL, source_prefix=os.path.basename(cal_dir) + "/").df
        liq = liq[liq["config_entropy"] == "liquid-ti"].copy()   # liquid runs only (UFM reference)
        liq["phase"] = "liquid"
        liq["reference_state"] = "absolute ACE energy"   # same zero as the QHA rows (calphy reports the ACE potential energy)
        summary["liquid_x_available"] = sorted(float(v) for v in liq["x"].unique())
    except Exception as e:
        summary["liquid_error"] = repr(e)
    if liq is None or liq.empty:
        raise SystemExit("no finished liquid calphy runs yet: " + str(summary))
    T_rows = liq.groupby("x")["T"].agg(["min", "max"])
    summary["liquid_T_range"] = {f"{x:.4f}": [float(a), float(b)] for x, (a, b) in T_rows.iterrows()}

    # ---- 05 one table, 04A configurational terms
    allrows = pd.concat([sol, liq], ignore_index=True)
    # a solution/limited phase that ended up with a single composition (failed cells) degrades to a point phase
    for ph, g in allrows.groupby("phase"):
        if g["kind"].iloc[0] != "point" and g["x"].nunique() < 2:
            allrows.loc[allrows.phase == ph, "kind"] = "point"
            summary.setdefault("degraded_to_point", []).append(ph)
    tab = FreeEnergyTable.from_rows(allrows.to_dict("records"), {"potential": POT, "pressure_GPa": 0.0, "level": "classical"})
    tab = add_configurational_term(tab, "fcc", "ideal")
    tab = add_configurational_term(tab, "B32", "sublattice", site_model=b32_antisite_site_fractions)
    warnings = tab.check()
    summary["table_check"] = [str(w) for w in warnings] if warnings else []
    tab.to_tsv(os.path.join(OUT, "05_free_energies.tsv"))
    ti = interpolate_T(tab, T_DIAG)
    Ts = np.array(sorted(ti.df["T"].unique()))
    # ---- 06/07
    # fcc and liquid: cubic polynomial for the excess over the analytic ideal-mixing term (ideal_T=T inside
    # builder_from_table); B32 (3 points, sublattice term): natural spline.  Gaps narrower than 0.005 in x
    # (4 sampling steps) are treated as fit noise, not as two-phase regions.
    FITS = {"fcc": "poly", "liquid": "poly", "B32": "spline"}
    HULL = {"min_width": 0.005, "gap_tol": 2.5}
    builder = builder_from_table(ti, fit="spline", fits=FITS, poly_order=3)
    resid = fit_residuals(builder, 900.0)
    resid.to_csv(os.path.join(OUT, "06_fit_residuals_900K.tsv"), sep="\t", index=False)
    reg = scan(builder, Ts, **HULL)
    # the liquid is sampled only up to x = 0.5: a segment that starts at or beyond the last liquid
    # composition is an edge of the sampled range, not a phase boundary
    x_liq_max = float(liq["x"].max())
    edge = reg["x_a"] >= x_liq_max - 1e-6
    summary["edge_segments_dropped"] = int(edge.sum())
    reg = reg[~edge].reset_index(drop=True)
    inv = invariants(reg)
    write_records(os.path.join(OUT, "07_two_phase_regions.tsv"), reg, {"example": "alli_ace_txdiagram", "fit": str(FITS) + " (poly = cubic excess over analytic ideal mixing)", "hull": str(HULL), "T_step": 10.0, "level": "classical (QHA lowered by F_q-F_cl)",
                                                                       "liquid": "calphy ts GPU, UFM, 3 iterations", "solids": "QHA 9 volumes, 32/108/128-atom supercells"})
    inv.to_csv(os.path.join(OUT, "07_invariants.tsv"), sep="\t", index=False)
    sig = {"fcc": 0.002, "B32": 0.002, "Al3Li": 0.002, "liquid": 0.0014}
    sens = sensitivity(builder, Ts[::2], sig, n_samples=30, rng=0, **HULL)
    sens.table.to_csv(os.path.join(OUT, "07_sensitivity.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Li", dT=10.0)
    ax.set_xlim(0.0, x_liq_max + 0.05)
    ax.set_title("ACE Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy GPU liquid", fontsize=9)
    ax.figure.savefig(os.path.join(OUT, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")
    # eutectic / melting summary
    liqreg = reg[(reg.phase_a == "liquid") | (reg.phase_b == "liquid")]
    if not liqreg.empty:
        Tm = float(liqreg["T"].min())
        summary["lowest_T_with_liquid_K"] = Tm
        summary["coexistence_at_that_T"] = liqreg[liqreg["T"] == Tm][["phase_a", "x_a", "phase_b", "x_b"]].to_dict("records")
    summary["invariants"] = inv.to_dict("records")
    summary["regions_at_800K"] = reg[np.isclose(reg["T"], 800.0)][["phase_a", "x_a", "phase_b", "x_b"]].to_dict("records")
    summary["regions_at_1000K"] = reg[np.isclose(reg["T"], 1000.0)][["phase_a", "x_a", "phase_b", "x_b"]].to_dict("records")
    summary["fit_rmse_900K"] = resid.to_dict("records")
    summary["finished"] = time.strftime("%F %T")
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str, ensure_ascii=False)
    log(json.dumps(summary, indent=1, default=str, ensure_ascii=False))


if __name__ == "__main__":
    {"prepare": prepare, "resume": resume, "solids": solids, "assemble": assemble}[sys.argv[1]]()
