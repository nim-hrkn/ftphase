"""Stage 4 of example 7 (post-processing only): re-assemble the Ni-Al diagram with the thermal-defect
(Wagner-Schottky) model for B2 and L1_2 instead of the constitutional single-defect sublattice model.

Input : out_mygardenx1/05_free_energies.tsv (stage 3 table; B2/L12 rows carry the analytic
        constitutional -T s_conf, which is removed here to recover the raw cell free energies).
Output: out_mygardenx1/ws/ (07_two_phase_regions.tsv, 07_invariants.tsv, 07_phase_diagram.png,
        defect_energies.tsv, REPORT_ws.md, summary.json).
Run:    env/ftphase/bin/python reassemble_ws.py   (about 2-4 min; no new MD/phonon calculations)
"""

import json
import os
import time
from functools import partial

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
import argparse as _ap
_args = _ap.ArgumentParser(); _args.add_argument("--in", dest="indir", default=None); _args = _args.parse_args()
IN = os.path.abspath(_args.indir) if _args.indir else (os.path.join(HERE, "out_mygardenx1") if os.path.isdir(os.path.join(HERE, "out_mygardenx1")) else os.path.join(HERE, "out"))
OUT = os.path.join(IN, "ws")
T_DIAG = np.arange(950.0, 2000.1, 10.0)


def main():
    import matplotlib

    matplotlib.use("Agg")
    from ftphase.assemble import builder_from_table, interpolate_T
    from ftphase.configurational import b2_triple_defect_site_fractions, b32_antisite_site_fractions, defect_energies_from_cells, sublattice_entropy
    from ftphase.diagram import invariants, plot_tx, scan, write_records
    from ftphase.records import FreeEnergyTable

    os.makedirs(OUT, exist_ok=True)
    tab = FreeEnergyTable.from_tsv(os.path.join(IN, "05_free_energies.tsv"))
    df = tab.df.copy()
    # ---- recover raw cell free energies of the ordered phases (undo the analytic constitutional term)
    models = {"B2": b2_triple_defect_site_fractions, "L12": partial(b32_antisite_site_fractions, stoich_x=0.75)}
    for ph, sm in models.items():
        m = (df.phase == ph) & (df.config_entropy == "sublattice")
        s = np.array([sublattice_entropy(*sm(x), basis="atom") for x in df.loc[m, "x"]])
        df.loc[m, "G"] = df.loc[m, "G"].to_numpy() + df.loc[m, "T"].to_numpy() * s
        df.loc[m, "config_entropy"] = "none"
        df.loc[m, "method"] = df.loc[m, "method"] + "; raw cell (constitutional term removed for the Wagner-Schottky model)"
    # calphy TI rows carry n_atoms = 0: reconstruct the atom count from x and the known number of lattice
    # sites of the defect supercells (B2 3x3x3 = 54 sites, L1_2 3x3x3 = 108 sites): n = N - k vacancies with x n integer
    N_SITES = {"B2": 54, "L12": 108}
    for ph, N in N_SITES.items():
        m = (df.phase == ph) & (df.n_atoms <= 0)
        def _n(x, N=N):
            for k in range(0, 9):
                n = N - k
                if abs(x * n - round(x * n)) < 1e-6:
                    return n
            raise ValueError(f"cannot reconstruct the atom count of x={x} with {N} sites")
        df.loc[m, "n_atoms"] = [_n(x) for x in df.loc[m, "x"]]
    tab = FreeEnergyTable.from_dataframe(df, dict(tab.meta, stage="ws re-assembly"))
    # ---- assemble as in pipeline.py stage 3, but with the thermal-defect model for B2 / L12
    ti = interpolate_T(tab, T_DIAG)
    cover = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["min", "max", "size"])
    ok_T = cover[cover["size"] >= 3].index          # same rule as pipeline.py stage 3 (liquid T_stop depends on x)
    ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(ok_T)], ti.meta)
    Ts = np.array(sorted(ti.df["T"].unique()))
    # ---- effective defect free energies at a few temperatures (for the report)
    rows = []
    for ph, sc in (("B2", (0.5, 0.5)), ("L12", (0.25, 0.75))):
        g = ti.df[ti.df.phase == ph]
        for T in (1000.0, 1400.0, 1800.0):
            gT = g[np.isclose(g["T"], T)]
            if gT.empty:
                continue
            try:
                e, g0, n_sites, cells = defect_energies_from_cells(gT["x"].to_numpy(), gT["G"].to_numpy(), gT["n_atoms"].to_numpy(), sc)
            except ValueError as exc:
                print(f"[{ph} {T} K] {exc}\n", gT[["x", "T", "n_atoms", "config_entropy"]].to_string(index=False)); raise
            for k, v in e.items():
                rows.append({"phase": ph, "T": T, "defect": k, "energy_eV_per_defect": v, "raw_minus_g0": v + g0 if k.startswith("Va") else v, "g0_atom": g0, "n_sites": n_sites,
                             "n_cells": sum(1 for c in cells if c["defect"] == k)})
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "defect_energies.tsv"), sep="\t", index=False)
    FITS = {"fccAl": "poly", "fccNi": "poly", "liquid": "rk", "B2": "poly", "L12": "poly"}
    HULL = {"min_width": 0.005, "gap_tol": 2.5}
    ENT = {"B2": ("wagner_schottky", (0.5, 0.5)), "L12": ("wagner_schottky", (0.25, 0.75))}
    t0 = time.time()
    builder = builder_from_table(ti, fit="spline", fits=FITS, poly_order=3, poly_orders={"liquid": 4, "fccAl": 2}, entropy_models=ENT)
    reg = scan(builder, Ts, **HULL)
    inv = invariants(reg)
    write_records(os.path.join(OUT, "07_two_phase_regions.tsv"), reg, {"example": "nial_eam stage 4 (Wagner-Schottky thermal defects)", "fits": str(FITS), "hull": str(HULL), "T_step": 10.0})
    inv.to_csv(os.path.join(OUT, "07_invariants.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Ni", dT=10.0)
    ax.set_title("EAM Ni-Al (Mishin 2009), 0 GPa: solids calphy TI, B2/L1_2 with thermal defects (Wagner-Schottky)", fontsize=8)
    ax.figure.savefig(os.path.join(OUT, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")
    # ---- key numbers: B2 range vs T, same-phase segments, invariants
    summary = {"seconds": time.time() - t0, "T_grid": [float(Ts.min()), float(Ts.max()), int(Ts.size)], "invariants": inv.to_dict("records")}
    b2 = {}
    for T in (1000, 1200, 1400, 1600, 1800):
        r = reg[np.isclose(reg["T"], T)]
        lo = r[r.phase_b == "B2"]["x_b"].min() if (r.phase_b == "B2").any() else np.nan
        hi = r[r.phase_a == "B2"]["x_a"].max() if (r.phase_a == "B2").any() else np.nan
        b2[str(T)] = [float(lo), float(hi)]
    summary["B2_range_vs_T"] = b2
    same = reg[reg.phase_a == reg.phase_b]
    summary["same_phase_segments"] = [{"phase": r.phase_a, "T": float(r.T), "x_a": float(r.x_a), "x_b": float(r.x_b)} for r in same.itertuples()]
    for T in (1200, 1500, 1800):
        summary[f"regions_at_{T}K"] = reg[np.isclose(reg["T"], T)][["phase_a", "x_a", "phase_b", "x_b"]].round(4).to_dict("records")
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)
    L = ["# Example 7, stage 4: B2 / L1_2 with thermal point defects (Wagner-Schottky), re-assembled from the stage-3 table", "",
         f"Grid {summary['T_grid']}; scan {summary['seconds']:.0f} s.  Effective defect free energies (eV per defect, raw supercell differences) in defect_energies.tsv.", "",
         "## Effective defect free energies", ""]
    for r in rows:
        L.append(f"* {r['phase']} {r['T']:.0f} K {r['defect']}: {r['energy_eV_per_defect']:+.3f} eV" + (f" (formation-like, + g0: {r['raw_minus_g0']:+.3f} eV)" if r['defect'].startswith('Va') else "") + f" from {r['n_cells']} cells")
    L += ["", "## B2 composition range [x_Ni lower, upper]", ""] + [f"* {T} K: {v}" for T, v in b2.items()]
    L += ["", "## Invariant reactions", ""] + [f"* {r['T_low']:.0f}-{r['T_high']:.0f} K: {r['pairs_below']} -> {r['pairs_above']}" for r in summary["invariants"]]
    L += ["", "## Same-phase segments", ""] + ([f"* {s['phase']}+{s['phase']} x = {s['x_a']:.3f}-{s['x_b']:.3f} at {s['T']:.0f} K" for s in summary["same_phase_segments"]] or ["* none"])
    for T in (1200, 1500, 1800):
        L.append(f"* two-phase regions at {T} K: " + "; ".join(f"{c['phase_a']}({c['x_a']:.3f})-{c['phase_b']}({c['x_b']:.3f})" for c in summary[f"regions_at_{T}K"]))
    with open(os.path.join(OUT, "REPORT_ws.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
