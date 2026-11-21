"""T-x diagram with every compound treated by the uniform procedure (ftphase.compounds): defect free energies of run_defects.py
+ the solutions / liquid and the stoichiometric compound rows of an existing free-energy table.
    python assemble.py nial_eam   -> out/<system>/uniform_{two_phase_regions.tsv, widths.tsv, diagram.png, REPORT.md}
"""
import json, os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); EXA = os.path.join(HERE, "..")
CFG = {"nial_eam": {"table": os.path.join(EXA, "nial_eam", "out_mygardenx1_stage5", "05_free_energies.tsv"), "reference": os.path.join(EXA, "nial_eam", "out_mygardenx1_stage5", "ws", "07_two_phase_regions.tsv"),
                    "reference_label": "stage 5: B2 / L1$_2$ from sampled defect cells (triple-defect / anti-site models chosen by hand), Ni$_2$Al$_3$, NiAl$_3$ as points",
                    "compounds": ["NiAl3", "Ni2Al3", "B2", "L12"], "T": np.arange(960.0, 2000.1, 20.0), "xlabel": "x_Ni",
                    "kw": dict(fit="spline", fits={"fccAl": "poly", "fccNi": "poly", "liquid": "rk"}, poly_order=3, poly_orders={"liquid": 4, "fccAl": 2})}}


def _alli(run, label):
    """Al-Li, solids only (300-700 K): the Li-side solid run of the MLIP (fcc, bcc, B32 and the three compounds; no liquid on the Li side)."""
    d = os.path.join(EXA, "aiida_txdiagram", "out", run)
    return {"table": os.path.join(d, "05_free_energies.tsv"), "reference": os.path.join(d, "07_two_phase_regions.tsv"),
            "reference_label": f"{label}: Al$_3$Li, Al$_2$Li$_3$, Al$_4$Li$_9$ as points, B32 as a range phase (declared in the input); solids only",
            "compounds": ["Al3Li", "B32", "Al2Li3", "Al4Li9"], "T": np.arange(300.0, 700.1, 20.0), "xlabel": "x_Li", "T_report": (300.0, 400.0, 500.0, 600.0, 700.0),
            "kw": dict(fit="spline", fits={"fcc": "poly", "bcc": "poly"}, poly_order=3)}


CFG["alli_grace_fs"] = _alli("alli_grace_fs_liside_solid", "GRACE-FS-OAM")
CFG["alli_ace"] = _alli("alli_ace_liside_solid", "ACE")


def main(system):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import interpolate_T, builder_from_table
    from ftphase.compounds import CompoundModel, with_compound_models, widths_from_regions, classify, interaction_polynomial, size_convergence
    from ftphase.diagram import scan, plot_tx, write_records, invariants
    c = CFG[system]; out = os.path.join(HERE, "out", system); tab = FreeEnergyTable.from_tsv(c["table"]); df = tab.df; models, info = {}, {}
    keep = []
    for name in c["compounds"]:
        r = json.load(open(os.path.join(out, f"defects_{name}.json"))); x0 = r["x0"]; sizes = sorted(int(k) for k, v in r["sizes"].items() if v.get("done")); N = sizes[-1]; big = r["sizes"][str(N)]; T = np.array(big["T"])
        eps = {k: np.array(v["eps_T_eV"]) for k, v in big["defects"].items() if "eps_T_eV" in v}; w = {}; w3 = {}; ext = {}; inf = {"n_sites": N, "sizes": sizes, "defects_ok": sorted(eps), "defects_failed": sorted(k for k in big["defects"] if k not in eps)}
        iT = int(np.argmin(abs(T - c.get("T_conv", 1200.0 if T.max() > 1500 else 500.0))))
        if "A_on_B" in eps and "B_on_A" in eps:      # convergence with cell size: anti-site pair free energy at 1200 K
            pair = {n: r["sizes"][str(n)]["defects"]["A_on_B"]["eps_T_eV"][iT] + r["sizes"][str(n)]["defects"]["B_on_A"]["eps_T_eV"][iT] for n in sizes if all("eps_T_eV" in r["sizes"][str(n)]["defects"].get(q, {}) for q in ("A_on_B", "B_on_A"))}
            inf["antisite_pair_by_size_eV"] = {int(k): round(float(v), 3) for k, v in pair.items()}; inf["size_converged_0.02eV"] = size_convergence(pair, 0.02)[0] if len(pair) > 1 else None
        mu = r.get("multi", {}); half = 0.03; sd = mu.get("constitutional_defects")
        if sd:
            inf["constitutional_defects"] = sd; xs = []
            for side, dk in sd.items():
                cells = [v for v in mu["cells"].values() if v["side"] == side and "dG_T_eV" in v and v.get("n_imag", 0) == 0]
                inf[f"cells_{side}"] = f"{len(cells)}/{sum(1 for v in mu['cells'].values() if v['side'] == side)}"
                if len(cells) >= 6 and dk in eps:
                    kk = np.array([v["k"] for v in cells]); dG = np.array([v["dG_T_eV"] for v in cells]); ww = np.array([interaction_polynomial(dG[:, i], kk, eps[dk][i], N) for i in range(len(T))]); w[dk] = ww[:, 0]; w3[dk] = ww[:, 1]
                    ext[side] = min(max(abs(v["x"] - x0) for v in cells), 0.15)
                    inf[f"w_{dk}_at_T_eV"] = {int(t): round(float(np.interp(t, T, w[dk])), 2) for t in (c.get("T_report", (1000.0, 1400.0, 1800.0))[0], c.get("T_report", (1000.0, 1400.0, 1800.0))[-1])}; xs += [abs(v["x"] - x0) for v in cells]
        half = (ext.get("A_rich", 0.03), ext.get("B_rich", 0.03))            # window = the compositions sampled on each side
        models[name] = CompoundModel(name, x0, tuple(r["site_counts"]), T, eps, w, half_width=half, side_defects=sd, w3=w3); inf["window"] = [round(x0 - half[0], 3), round(x0 + half[1], 3)]; info[name] = inf
        keep.append(df[(df.phase == name) & np.isclose(df.x, x0, atol=2e-4)])
    d2 = pd.concat([df[~df.phase.isin(c["compounds"])]] + keep, ignore_index=True); ti = interpolate_T(FreeEnergyTable.from_dataframe(d2, tab.meta), c["T"])
    if (ti.df.phase == "liquid").any():
        cover = ti.df[ti.df.phase == "liquid"].groupby("T")["x"].agg(["size"]); okT = cover[cover["size"] >= 3].index; ti = FreeEnergyTable.from_dataframe(ti.df[ti.df["T"].isin(okT)], ti.meta)
    Ts = np.array(sorted(ti.df["T"].unique())); full = with_compound_models(builder_from_table(ti, **c["kw"]), models); cache = {}

    def builder(T):
        if T not in cache:
            cache[T] = full(T)
        return cache[T]

    reg = scan(builder, Ts, min_width=0.002, gap_tol=2.5); reg = reg[reg.phase_a != reg.phase_b]
    write_records(os.path.join(out, "uniform_two_phase_regions.tsv"), reg, {"example": f"{system}: every compound by defect free energies (assemble.py)"})
    w = widths_from_regions(reg, models); w.to_csv(os.path.join(out, "uniform_widths.tsv"), sep="\t", index=False, float_format="%.4f"); cls = classify(w); invariants(reg).to_csv(os.path.join(out, "uniform_invariants.tsv"), sep="\t", index=False)
    ref = pd.read_csv(c["reference"], sep="\t", comment="#"); ref = ref[(ref.phase_a != ref.phase_b) & (ref["T"] >= Ts.min() - 1) & (ref["T"] <= Ts.max() + 1)]
    keys = sorted(set("+".join(sorted((a_, b_))) for d_ in (ref, reg) for a_, b_ in zip(d_.phase_a, d_.phase_b)))
    pal = ["#b0b0b0", "#f4a259", "#5b9bd5", "#a05195", "#70ad47", "#d45087", "#8dd3c7", "#ffa600", "#bc80bd", "#fb8072", "#665191", "#b3de69", "#80b1d3", "#fdb462", "#bebada", "#ccebc5"]; COL = {}
    for n_, k_ in enumerate(keys):
        a_, b_ = k_.split("+"); COL[f"{a_}+{b_}"] = COL[f"{b_}+{a_}"] = pal[n_ % len(pal)]
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 6), sharey=True)
    plot_tx(ref, xlabel=c["xlabel"], dT=10, ax=axes[0], colors=COL); axes[0].set_title(c["reference_label"], fontsize=8.5)
    plot_tx(reg, xlabel=c["xlabel"], dT=float(np.diff(Ts).min()), ax=axes[1], colors=COL); axes[1].set_title("same solutions and liquid; every compound by defect free energies ε$_d$(T) + interaction, kind read from the hull", fontsize=8.5)
    fig.tight_layout(); fig.savefig(os.path.join(out, "uniform_diagram.png"), dpi=140)
    L = [f"# {system}: uniform compound procedure", "", f"Classification read from the hull: {cls}", "", "## Width of each compound (x of the second element; '*' = at the edge of the window)", "",
         "| T (K) | " + " | ".join(c["compounds"]) + " |", "|---|" + "---|" * len(c["compounds"])]
    for T in sorted(w["T"].unique())[::5]:
        g = w[np.isclose(w["T"], T)].set_index("phase"); L.append(f"| {T:.0f} | " + " | ".join("—" if not g.loc[k, "stable"] else f"{g.loc[k, 'x_min']:.3f}–{g.loc[k, 'x_max']:.3f}" + ("*" if g.loc[k, "at_window_edge"] else "") for k in c["compounds"]) + " |")
    top = {k: (float(w[(w.phase == k) & w.stable]["T"].max()) if w[w.phase == k].stable.any() else None) for k in c["compounds"]}
    L += ["", f"Highest temperature on the hull: {top}", "", "## Inputs per compound", ""] + [f"* {k}: {json.dumps(v)}" for k, v in info.items()]
    open(os.path.join(out, "REPORT.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1])
