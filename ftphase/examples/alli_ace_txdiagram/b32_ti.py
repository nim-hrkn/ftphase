"""Example 6, B32 AlLi near its melting point by calphy solid TI with >= 2000-atom cells (instead of QHA).

The QHA route puts B32 20-45 meV/atom too high near T_m in the Ni-Al test; here the three B32 cells of
example 6 (x_Li = 7/16, 1/2, 9/16; 16 atoms) are replicated 5x5x5 (2000 atoms) and run as calphy
reversible scaling 700 -> 880 K (ACE, GPU, Einstein-crystal reference).  The assembly takes the 05 table
of example 6, replaces the B32 rows at T >= 700 K by the TI rows plus the analytic sublattice term
(b32_antisite_site_fractions, the same term the pipeline added), and re-runs stages 06-07.

    python b32_ti.py prepare    -> calphy_b32ti/input.yaml and submission with calphy -i (Slurm, GPU)
    python b32_ti.py assemble   -> out_full/b32ti/ (07_two_phase_regions.tsv, 07_phase_diagram.png, REPORT.md)
"""

import glob
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POT = os.path.join(ROOT, "pyiron-examples/workshop2022-phase-diagram/resources/lammps/potentials/ace/AlLi-6gen-18May.yace")
LMP_GPU = os.path.join(ROOT, "env/lammps-gpu/bin/lmp_gpu")
ENV = os.path.join(ROOT, "env/ftphase")
CAL = os.path.join(HERE, "calphy_b32ti")
OUT = os.path.join(HERE, "out_full")
T_SWEEP = [700.0, 880.0]
REP = (5, 5, 5)


def prepare():
    from ase.io import read

    from ftphase.calphy_io import calculation_block, slurm_queue, write_series_input
    from ftphase.structures import write_lammps_data

    os.makedirs(CAL, exist_ok=True)
    man = [m for m in json.load(open(os.path.join(OUT, "02A_solids.json"))) if m["phase"] == "B32"]
    q = slurm_queue(ENV, cores=1, memory="8GB")
    blocks, rec = [], []
    for m in man:
        at = read(m["file"]).repeat(REP)
        tag = f"b32_x{m['x']:.4f}".replace(".", "p")
        data = write_lammps_data(at, os.path.join(CAL, f"{tag}.data"), ["Al", "Li"])
        blocks.append(calculation_block(tag, "ts", ["Al", "Li"], [26.9815, 6.94], data, "pace", f"* * {POT} Al Li", T_SWEEP, pressure=0, reference_phase="solid",
                                        n_equilibration_steps=10000, n_switching_steps=[10000, 10000], n_iterations=2, queue=q, folder_prefix=tag, gpu=True, lammps_executable=LMP_GPU))
        rec.append({"id": m["id"], "tag": tag, "x": m["x"], "n_atoms": len(at), "T_sweep": T_SWEEP})
    write_series_input(os.path.join(CAL, "input.yaml"), blocks)
    with open(os.path.join(CAL, "cells.json"), "w") as f:
        json.dump(rec, f, indent=1)
    env = dict(os.environ); env["PATH"] = os.path.join(ENV, "bin") + os.pathsep + env["PATH"]
    r = subprocess.run(["calphy", "-i", "input.yaml"], cwd=CAL, env=env, capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-600:]); print(f"{len(blocks)} B32 solid TI runs ({len(at)} atoms) submitted")


def assemble():
    import matplotlib

    matplotlib.use("Agg")
    import pandas as pd

    from ftphase.assemble import builder_from_table, interpolate_T
    from ftphase.configurational import b32_antisite_site_fractions, sublattice_entropy
    from ftphase.diagram import invariants, plot_tx, scan, write_records
    from ftphase.records import FreeEnergyTable

    out = os.path.join(OUT, "b32ti"); os.makedirs(out, exist_ok=True)
    tab = FreeEnergyTable.from_tsv(os.path.join(OUT, "05_free_energies.tsv"))
    df = tab.df.copy()
    rec = json.load(open(os.path.join(CAL, "cells.json")))
    rows = []
    for m in rec:
        d = sorted(glob.glob(os.path.join(CAL, f"{m['tag']}-ts-*/")))
        d = [x for x in d if os.path.exists(os.path.join(x, "temperature_sweep.dat"))]
        if not d:
            print("no sweep for", m["tag"]); continue
        a = np.loadtxt(os.path.join(d[0], "temperature_sweep.dat"), ndmin=2)
        s_conf = sublattice_entropy(*b32_antisite_site_fractions(m["x"]), basis="atom")
        for T, G, err in a:
            rows.append({"phase": "B32", "kind": "limited", "x": m["x"], "T": float(np.round(T, 3)), "P_GPa": 0.0, "G": float(G) - T * s_conf, "G_err": float(err), "V": np.nan,
                         "model": df["model"].iloc[0], "reference_state": "absolute ACE energy", "method": f"calphy ts solid (Einstein crystal), {m['n_atoms']}-atom cell; + analytic B32 anti-site sublattice term",
                         "config_entropy": "sublattice", "quantum": "classical", "n_atoms": m["n_atoms"], "source": f"b32_ti {m['tag']}"})
    if not rows:
        raise SystemExit("no B32 TI sweeps yet")
    T_lo = min(r["T"] for r in rows)
    keep = ~((df.phase == "B32") & (df["T"] >= T_lo - 1e-6))
    df2 = pd.concat([df[keep], pd.DataFrame(rows)], ignore_index=True)
    tab2 = FreeEnergyTable.from_dataframe(df2, dict(tab.meta, stage="B32 solid TI (>= 2000 atoms) above %.0f K" % T_lo))
    T_grid = np.arange(650.0, 1100.1, 10.0)
    ti = interpolate_T(tab2, T_grid)
    cover = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["min", "max", "size"])
    ok_T = cover[(cover["min"] <= 1e-6) & (cover["max"] >= 1 - 1e-6) & (cover["size"] >= 6)].index
    ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(ok_T)], ti.meta)
    Ts = np.array(sorted(ti.df["T"].unique()))
    FITS = {"fcc": "poly", "bcc": "poly", "liquid": "rk", "B32": "spline"}
    HULL = {"min_width": 0.005, "gap_tol": 2.5}
    builder = builder_from_table(ti, fit="spline", fits=FITS, poly_order=3, poly_orders={"liquid": 4})
    reg = scan(builder, Ts, **HULL)
    inv = invariants(reg)
    write_records(os.path.join(out, "07_two_phase_regions.tsv"), reg, {"example": "alli_ace_txdiagram full, B32 by solid TI (2000 atoms)", "fits": str(FITS), "hull": str(HULL), "T_step": 10.0})
    inv.to_csv(os.path.join(out, "07_invariants.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Li", dT=10.0)
    ax.set_title("ACE Al-Li, 0 GPa: QHA solids (64-atom SQS), B32 by calphy TI (2000 atoms) above 700 K, calphy liquid", fontsize=8)
    ax.figure.savefig(os.path.join(out, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")
    # QHA - TI for B32 at a few T
    qha = df[(df.phase == "B32") & (df.config_entropy == "sublattice")]
    cmp = []
    for m in rec:
        for T in (700.0, 800.0, 850.0):
            q = qha[(np.abs(qha.x - m["x"]) < 1e-6)]
            r = [x for x in rows if abs(x["x"] - m["x"]) < 1e-6]
            if len(q) and r:
                gq = float(np.interp(T, q.sort_values("T")["T"], q.sort_values("T")["G"])); gt = float(np.interp(T, [x["T"] for x in r], [x["G"] for x in r]))
                cmp.append(f"* B32 x = {m['x']:.4f} at {T:.0f} K: QHA - TI = {(gq - gt) * 1000:+.1f} meV/atom")
    b32liq = reg[((reg.phase_a == "B32") & (reg.phase_b == "liquid")) | ((reg.phase_a == "liquid") & (reg.phase_b == "B32"))]
    L = ["# Example 6 with B32 by calphy solid TI (2000-atom cells, 700-880 K)", "", f"Grid {Ts.min():.0f}-{Ts.max():.0f} K", "", "## QHA (classical level) minus TI, B32", ""] + cmp
    L += ["", "## Invariant reactions", ""] + [f"* {r['T_low']:.0f}-{r['T_high']:.0f} K: {r['pairs_below']} -> {r['pairs_above']}" for r in inv.to_dict("records")]
    L += ["", f"* B32 + liquid present up to {b32liq['T'].max():.0f} K" if len(b32liq) else "* no B32 + liquid segments"]
    for T in (700, 760, 770, 800, 850):
        rr = reg[np.isclose(reg["T"], T)]
        L.append(f"* two-phase regions at {T} K: " + "; ".join(f"{c.phase_a}({c.x_a:.3f})-{c.phase_b}({c.x_b:.3f})" for c in rr.itertuples()))
    with open(os.path.join(out, "REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    {"prepare": prepare, "assemble": assemble}[sys.argv[1]]()
