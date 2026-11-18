"""ACE Al-Li T-x diagram with EVERY compound treated by the same procedure (no prior knowledge of which one has a composition
range): four point defects -> defect free energies eps_d(T) of the largest cell (defect_free_energy.py) -> Wagner-Schottky G(x, T)
within x0 +- 0.03 -> lower hull with fcc, bcc and liquid (example-6 free energies + the full-range fcc/bcc cells of extend_range.py).
Compared with example 6 (Al3Li, Al2Li3, Al4Li9 as points; B32 as a range phase from 16-atom cells).
Liquid included where it covers the composition range (>= 660 K); below that the solids only, as in example 6.
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/uniform_diagram.py   -> out/8_uniform_*.tsv / .png / .md
"""
import json, os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); EX6 = os.path.join(HERE, "..", "alli_ace_txdiagram"); sys.path.insert(0, EX6); sys.path.insert(0, HERE)
WS = {"Al3Li": (3, 1), "B32": (1, 1), "Al2Li3": (2, 3), "Al4Li9": (4, 9)}
MODE = sys.argv[1] if len(sys.argv) > 1 else "interacting"      # interacting: + w (x - x0)^2 from the multi-defect cells, window +-0.06; noninteracting: window +-0.03
HALF = 0.06 if MODE == "interacting" else 0.03; SUF = "" if MODE == "noninteracting" else "_interacting"
MAP = {"A_on_B": "Al_on_Li", "B_on_A": "Li_on_Al", "Va_on_B": "Va_Li", "Va_on_A": "Va_Al"}


def main():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table
    from ftphase.configurational import wagner_schottky_curve
    from ftphase.equilibrium import PhaseCurve
    from ftphase.diagram import scan, plot_tx, write_records, invariants
    import extend_range as er
    st = json.load(open(er.STAT)); new = pd.read_csv(er.TSV, sep="\t"); bad = {(v["phase"], v["x"]) for v in st.values() if v.get("ok") and (v["n_imag_modes"] > 0 or v["disp_max_A"] > 0.5)}
    new = new[[(p, x) not in bad for p, x in zip(new.phase, new.x)]]; tabn = FreeEnergyTable.from_rows(new.to_dict("records"), {})
    for ph in ("fcc", "bcc"):
        if (tabn.df.phase == ph).any() and tabn.df[tabn.df.phase == ph]["x"].nunique() > 1:
            tabn = add_configurational_term(tabn, ph, "ideal")
    old = FreeEnergyTable.from_tsv(os.path.join(EX6, "out_full", "05_free_energies.tsv")); df = pd.concat([old.df, tabn.df], ignore_index=True)
    b32pt = df[(df.phase == "B32") & np.isclose(df.x, 0.5)].copy(); df = pd.concat([df[df.phase != "B32"], b32pt], ignore_index=True)       # B32: its stoichiometric cell only, like the others
    from ftphase.compounds import CompoundModel, with_compound_models, widths_from_regions, classify, interaction_coefficient
    models = {}; winfo = {}
    for k, sc in WS.items():           # defect free energies of the largest cell + interaction coefficients of the multi-defect cells
        d = json.load(open(os.path.join(OUT, f"7_defectF_{k}.json")))["sizes"]; N = max(int(q) for q in d); big = d[str(N)]; Tg = np.array(big["T"])
        eps = {a: np.array(big["defects"][b]["eps_T_eV"]) for a, b in MAP.items()}; w = {}; winfo[k] = {}
        f9 = os.path.join(OUT, f"9_interaction_{k}.json")
        if MODE != "noninteracting" and os.path.exists(f9):
            r9 = json.load(open(f9))
            for a, b in (("A_on_B", "Al_on_Li"), ("B_on_A", "Li_on_Al")):
                cells = [c for c in r9["cells"].values() if c["side"] == b and "dG_T_eV" in c and c.get("n_imag", 0) == 0]
                if len(cells) >= 6:
                    kk = np.array([c["k"] for c in cells]); dG = np.array([c["dG_T_eV"] for c in cells])
                    w[a] = np.array([interaction_coefficient(dG[:, i], kk, eps[a][i], N) for i in range(len(Tg))])
                    winfo[k][b] = {"n_cells": len(cells), "x_sampled": [min(c["x"] for c in cells), max(c["x"] for c in cells)], "w_300_500_700_eV": [float(np.interp(t, Tg, w[a])) for t in (300, 500, 700)]}
        models[k] = CompoundModel(k, sc[1] / (sc[0] + sc[1]), sc, Tg, eps, w, half_width=HALF)
    kw = dict(fit="spline", fits={"fcc": "poly", "bcc": "poly", "liquid": "rk"}, poly_order=3, poly_orders={"liquid": 4, "fcc": 4, "bcc": 4})
    Ts = np.arange(300.0, 1100.1, 20.0); cache = {}

    def base(T):
        d = df if T >= 660 else df[df.phase != "liquid"]; ti = interpolate_T(FreeEnergyTable.from_dataframe(d, old.meta), np.array([T]))
        return builder_from_table(ti, **kw)(T)

    full = with_compound_models(base, models)

    def builder(T):
        if T not in cache:
            cache[T] = full(T)
        return cache[T]

    reg = scan(builder, Ts, min_width=0.002, gap_tol=2.5); reg = reg[reg.phase_a != reg.phase_b]
    write_records(os.path.join(OUT, f"8_uniform_two_phase_regions{SUF}.tsv"), reg, {"example": "ACE Al-Li, every compound by point defects + eps_d(T) + Wagner-Schottky (uniform_diagram.py)", "x_window": HALF, "mode": MODE})
    w = widths_from_regions(reg, models); w.to_csv(os.path.join(OUT, f"8_uniform_widths{SUF}.tsv"), sep="\t", index=False, float_format="%.4f"); cls = classify(w)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True)
    ref = pd.read_csv(os.path.join(EX6, "out_full", "07_two_phase_regions.tsv"), sep="\t", comment="#"); ref = ref[ref.phase_a != ref.phase_b]
    low = os.path.join(EX6, "out_full", "lowT", "07_two_phase_regions.tsv")
    if os.path.exists(low):
        l = pd.read_csv(low, sep="\t", comment="#"); ref = pd.concat([l[(l.phase_a != l.phase_b) & (l["T"] < ref["T"].min())], ref], ignore_index=True)
    plot_tx(ref, xlabel="x_Li", dT=10, ax=axes[0]); axes[0].set_title("example 6: Al$_3$Li, Al$_2$Li$_3$, Al$_4$Li$_9$ as points, B32 as a range phase (prior knowledge)", fontsize=9)
    plot_tx(reg, xlabel="x_Li", dT=20, ax=axes[1]); axes[1].set_title(f"same free energies, every compound by defect free energies ({MODE}, x$_0$ ± {HALF})", fontsize=9)
    for ax in axes: ax.set_ylim(300, 1100)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, f"8_uniform_diagram{SUF}.png"), dpi=140)
    inv = invariants(reg); inv.to_csv(os.path.join(OUT, f"8_uniform_invariants{SUF}.tsv"), sep="\t", index=False)
    L = [f"# ACE Al-Li: widths of the compounds from the uniform procedure, {MODE} (x_Li; '*' = at the edge of the x0 +- {HALF} window)", "", "| T (K) | " + " | ".join(WS) + " |", "|---|" + "---|" * len(WS)]
    for T in (300, 400, 500, 600, 700, 800, 900):
        g = w[np.isclose(w["T"], T)].set_index("phase"); L.append(f"| {T} | " + " | ".join("—" if not g.loc[k, "stable"] else f"{g.loc[k, 'x_min']:.3f}–{g.loc[k, 'x_max']:.3f}" + ("*" if g.loc[k, "at_window_edge"] else "") for k in WS) + " |")
    top = {k: float(w[(w.phase == k) & w.stable]["T"].max()) if (w[(w.phase == k)].stable).any() else None for k in WS}; L += ["", f"Highest temperature at which each compound is on the hull (20 K grid): {top}", "", f"Classification read from the hull: {cls}", "", f"Interaction coefficients: {json.dumps(winfo)}"]
    open(os.path.join(OUT, f"8_uniform_widths{SUF}.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
