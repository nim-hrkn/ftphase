"""Post-processing of the Ag-Cu AiiDA run (example 9, pk 428): re-assemble from out/agcu_eam/05_free_energies.tsv
with the two fcc terminal solutions treated as separate phases (fccAg: x_Cu <= 0.3, fccCu: x_Cu >= 0.7) so that
the gap is a fccAg + fccCu common tangent instead of a 'same-phase' segment of one Redlich-Kister curve, and with
the temperature grid extended below the pure-end liquids (solid-only hull where no liquid exists, liquid on its
sampled sub-range where >= 3 compositions exist; edges flagged).  The 9 mid-composition cells whose solid TI melted
are dropped above 900 K (their QHA-only rows are 15-30 meV/atom off the TI level of the other cells).

Output: out/agcu_eam/reassembled/ (07_two_phase_regions.tsv, 07_invariants.tsv, 07_phase_diagram.png, REPORT.md,
rk_gap.tsv for the SGC comparison).  No new calculations.
"""

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "out", "agcu_eam")
OUT = os.path.join(IN, "reassembled")
T_DIAG = np.arange(700.0, 1400.1, 10.0)
SGC_T = [800.0, 900.0, 1000.0]


def main():
    import matplotlib

    matplotlib.use("Agg")
    from ftphase.assemble import add_configurational_term, builder_from_table, interpolate_T
    from ftphase.diagram import invariants, plot_tx, scan, write_records
    from ftphase.records import FreeEnergyTable

    os.makedirs(OUT, exist_ok=True)
    tab = FreeEnergyTable.from_tsv(os.path.join(IN, "05_free_energies.tsv"))
    df = tab.df.copy()
    df = df[df.config_entropy != "ideal"] if (df.config_entropy == "ideal").all() else df
    # undo the ideal term that assemble_diagram added to fcc rows (it is added again below per phase)
    from ftphase.configurational import ideal_entropy

    fcc = df.phase == "fcc"
    df.loc[fcc & (df.config_entropy == "ideal"), "G"] = df.loc[fcc & (df.config_entropy == "ideal"), "G"].to_numpy() + df.loc[fcc & (df.config_entropy == "ideal"), "T"].to_numpy() * np.array([ideal_entropy(x) for x in df.loc[fcc & (df.config_entropy == "ideal"), "x"]])
    df.loc[fcc, "config_entropy"] = "none"
    # split the terminal solutions; drop mid-composition cells above 900 K (QHA-only, inconsistent level)
    mid = fcc & (df.x > 0.3) & (df.x < 0.7)
    df = df[~(mid & (df["T"] >= 900.0 - 1e-6))]
    df.loc[(df.phase == "fcc") & (df.x <= 0.3), "phase"] = "fccAg"
    df.loc[(df.phase == "fcc") & (df.x >= 0.7), "phase"] = "fccCu"
    df = df[df.phase != "fcc"]
    tab = FreeEnergyTable.from_dataframe(df, dict(tab.meta, stage="agcu re-assembly, split terminal fcc"))
    for ph in ("fccAg", "fccCu"):
        tab = add_configurational_term(tab, ph, "ideal")
    ti = interpolate_T(tab, T_DIAG)
    d = ti.df
    # grid: keep T where the liquid has >= 3 compositions, or no liquid at all (solid-only hull); drop T where only 1-2 liquid points
    cover = d[d.phase == "liquid"].groupby("T")["x"].agg(["size"])
    bad_T = cover[cover["size"] < 3].index
    d = d[~d["T"].isin(bad_T)]
    ti = FreeEnergyTable.from_dataframe(d, ti.meta)
    Ts = np.array(sorted(ti.df["T"].unique()))
    FITS = {"fccAg": "poly", "fccCu": "poly", "liquid": "rk"}
    builder = builder_from_table(ti, fit="spline", fits=FITS, poly_order=3, poly_orders={"liquid": 4, "fccAg": 2, "fccCu": 2})
    reg = scan(builder, Ts, min_width=0.005, gap_tol=2.5)
    # edge flag: boundary at the sampled limit of a phase at that T
    lim = ti.df.groupby(["T", "phase"])["x"].agg(["min", "max"])
    def _edge(r):
        a = lim.loc[(r["T"], r.phase_a)] if (r["T"], r.phase_a) in lim.index else None
        b = lim.loc[(r["T"], r.phase_b)] if (r["T"], r.phase_b) in lim.index else None
        return bool((a is not None and abs(r.x_a - a["max"]) < 1e-6 and a["max"] < 1 - 1e-6 and r.phase_a != r.phase_b) or (b is not None and abs(r.x_b - b["min"]) < 1e-6 and b["min"] > 1e-6 and r.phase_a != r.phase_b))
    reg["edge"] = reg.apply(_edge, axis=1) if len(reg) else []
    inv = invariants(reg)
    write_records(os.path.join(OUT, "07_two_phase_regions.tsv"), reg, {"example": "agcu_eam re-assembly (split terminal fcc)", "fits": str(FITS), "T_step": 10.0})
    inv.to_csv(os.path.join(OUT, "07_invariants.tsv"), sep="\t", index=False)
    ax = plot_tx(reg, xlabel="x_Cu", dT=10.0)
    ax.set_title("EAM Ag-Cu (Williams-Mishin-Hamilton 2006), 0 GPa: fccAg / fccCu (calphy TI >= 900 K) + calphy liquid, re-assembled", fontsize=8)
    ax.figure.savefig(os.path.join(OUT, "07_phase_diagram.png"), dpi=150, bbox_inches="tight")
    gaps = []
    from ftphase.equilibrium import equilibrium_at_T

    for T in SGC_T:
        r = reg[np.isclose(reg["T"], T) & (reg.phase_a == "fccAg") & (reg.phase_b == "fccCu")]
        if len(r):
            gaps.append({"T": T, "x_alpha": float(r["x_a"].iloc[0]), "x_beta": float(r["x_b"].iloc[0]), "edge": bool(r["edge"].iloc[0]), "solid_only": False})
        else:   # the liquid interrupts the gap (above the eutectic): tangent between the two metastable fcc branches, as the SGC MC of the solid sees it
            Tn = float(Ts[np.argmin(np.abs(Ts - T))])
            sol = [p_ for p_ in builder(Tn) if p_.name in ("fccAg", "fccCu")]
            eq = equilibrium_at_T(sol, Tn, min_width=0.005)
            c = [c_ for c_ in eq.coexistence if {c_.phase_a, c_.phase_b} == {"fccAg", "fccCu"}]
            if c:
                gaps.append({"T": T, "x_alpha": float(c[0].x_a), "x_beta": float(c[0].x_b), "edge": False, "solid_only": True})
    pd.DataFrame(gaps).to_csv(os.path.join(OUT, "rk_gap.tsv"), sep="\t", index=False)
    summary = {"T_grid": [float(Ts.min()), float(Ts.max()), int(Ts.size)], "invariants": inv.to_dict("records"), "gap": gaps,
               "same_phase": [{"phase": r.phase_a, "T": float(r.T), "x_a": float(r.x_a), "x_b": float(r.x_b)} for r in reg[reg.phase_a == reg.phase_b].itertuples()]}
    for T in (1000, 1050, 1100, 1200):
        summary[f"regions_at_{T}K"] = reg[np.isclose(reg["T"], T)][["phase_a", "x_a", "phase_b", "x_b", "edge"]].round(4).to_dict("records")
    liq = reg[(reg.phase_a == "liquid") | (reg.phase_b == "liquid")]
    summary["lowest_T_with_liquid_K"] = float(liq["T"].min()) if len(liq) else None
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)
    L = ["# Ag-Cu (example 9) re-assembled: fccAg / fccCu as separate terminal solutions, grid extended to solid-only temperatures", "",
         f"Grid {summary['T_grid']} K; lowest T with liquid {summary['lowest_T_with_liquid_K']}", "", "## Invariant reactions", ""]
    L += [f"* {r['T_low']:.0f}-{r['T_high']:.0f} K: {r['pairs_below']} -> {r['pairs_above']}" for r in summary["invariants"]]
    L += ["", "## fccAg + fccCu gap (for the SGC MC comparison)", ""] + [f"* {g['T']:.0f} K: x_alpha = {g['x_alpha']:.3f}, x_beta = {g['x_beta']:.3f}{' (edge)' if g['edge'] else ''}{' (solid-only tangent, metastable above the eutectic)' if g.get('solid_only') else ''}" for g in gaps]
    for T in (1000, 1050, 1100, 1200):
        L.append(f"* two-phase regions at {T} K: " + "; ".join(f"{c['phase_a']}({c['x_a']:.3f})-{c['phase_b']}({c['x_b']:.3f}){'*' if c['edge'] else ''}" for c in summary[f"regions_at_{T}K"]))
    L += ["", "## Same-phase segments", ""] + ([f"* {s_['phase']}+{s_['phase']} x = {s_['x_a']:.3f}-{s_['x_b']:.3f} at {s_['T']:.0f} K" for s_ in summary["same_phase"]] or ["* none"])
    with open(os.path.join(OUT, "REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
