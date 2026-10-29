"""Compare T-x diagrams of the same system computed with different MLIPs (same WorkChain spec, same cells).

    python mlip_compare.py ace=out/alli_ace_m6 grace-fs=out/alli_grace_fs [--out out/mlip_compare] [--T 800]

Reads each run's hull.json (stage 01), 05_free_energies.tsv (03A/03B/04), 07_two_phase_regions.tsv, 07_invariants.tsv and
summary.json, and writes REPORT.md + overlay.png.  Energies are compared only as differences within one MLIP (formation
energies at 0 K; G relative to the pure/stoichiometric end members of the same MLIP at T; liquid minus solid at the same
x), never as absolute values across MLIPs.  Units eV/atom, 0 GPa, classical level (the WorkChain lowers QHA to it)."""

import argparse
import json
import os

import numpy as np
import pandas as pd


def load(d):
    r = {"hull": json.load(open(os.path.join(d, "hull.json"))), "tab": pd.read_csv(os.path.join(d, "05_free_energies.tsv"), sep="\t"),
         "reg": pd.read_csv(os.path.join(d, "07_two_phase_regions.tsv"), sep="\t"), "inv": pd.read_csv(os.path.join(d, "07_invariants.tsv"), sep="\t"),
         "sum": json.load(open(os.path.join(d, "summary.json")))}
    r["model"] = r["tab"]["model"].iloc[0]
    return r


def g_at(tab, phase, x, T, method_filter=None):
    """G (eV/atom) of a phase at composition x (nearest sampled) and temperature T by interpolation; NaN if absent."""
    t = tab[tab.phase == phase]
    if method_filter:
        t = t[t.method.str.contains(method_filter, na=False)]
    if not len(t):
        return np.nan, np.nan
    xs = np.array(sorted(t.x.unique())); xx = xs[np.argmin(np.abs(xs - x))]
    s = t[np.isclose(t.x, xx)].groupby("T")["G"].mean()
    if T < s.index.min() or T > s.index.max():
        return np.nan, xx
    return float(np.interp(T, s.index.values, s.values)), xx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="label=outdir")
    ap.add_argument("--out", default=None)
    ap.add_argument("--T", type=float, nargs="+", default=[700.0, 800.0])
    a = ap.parse_args()
    runs = {k: load(v) for k, v in (s.split("=", 1) for s in a.runs)}
    out = a.out or os.path.join(os.path.dirname(list(a.runs[0].split("=", 1))[1].rstrip("/")), "mlip_compare"); os.makedirs(out, exist_ok=True)
    labels = list(runs)
    L = ["# Same system, different MLIPs: " + " vs ".join(f"{k} ({runs[k]['model']})" for k in labels), ""]
    # ---- 01: 0 K formation energies of the candidates
    L += ["## 01: 0 K formation energies of the candidate phases (eV/atom, vs the pure end members of the same MLIP) and hull status", "",
          "| candidate | x | " + " | ".join(f"{k} E_form | {k} on hull" for k in labels) + " |", "|---|---|" + "---|---|" * len(labels)]
    names = [h["name"] for h in runs[labels[0]]["hull"]["hull"]]
    for n in names:
        row = [n]
        xx = None
        for k in labels:
            h = next((q for q in runs[k]["hull"]["hull"] if q["name"] == n), None)
            xx = h["x"] if h else xx
            row += [f"{h['e_form']:+.4f}" if h else "-", ("yes" if h["on_hull"] else f"no (+{h['e_above_hull']*1000:.0f} meV)") if h else "-"]
        L.append(f"| {row[0]} | {xx} | " + " | ".join(row[1:]) + " |")
    L += ["", "Relaxed volumes (A^3/atom): " + "; ".join(f"{k}: " + ", ".join(f"{q['name']} {q['V']:.2f}" for q in runs[k]["hull"]["relaxed"]) for k in labels), ""]
    # ---- 03A: vibrational free energy and thermal expansion of the end members
    L += ["## 03A: solids, G(T) - G(lowest T) of the end members (eV/atom; vibrational + thermal expansion, classical level)", "",
          "| phase, x | T (K) | " + " | ".join(labels) + " |", "|---|---|" + "---|" * len(labels)]
    ends = [("fcc", 0.0), ("B32", 0.5), ("Al3Li", 0.25)]
    for ph, x in ends:
        for T in a.T:
            row = []
            for k in labels:
                t = runs[k]["tab"]; t = t[(t.phase == ph) & t.method.str.contains("QHA", na=False)]
                if not len(t):
                    row.append("-"); continue
                xs = np.array(sorted(t.x.unique())); xx = xs[np.argmin(np.abs(xs - x))]
                s = t[np.isclose(t.x, xx)].groupby("T")["G"].mean()
                row.append(f"{np.interp(T, s.index, s.values) - s.iloc[0]:+.4f} (from {s.index.min():.0f} K)")
            L.append(f"| {ph}, x = {x} | {T:.0f} | " + " | ".join(row) + " |")
    L += ["", "## 03A: fcc Al thermal expansion V(T)/V(T_min) and B32 anti-site cost", ""]
    for k in labels:
        t = runs[k]["tab"]; f = t[(t.phase == "fcc") & np.isclose(t.x, 0.0) & t.method.str.contains("QHA", na=False)].groupby("T")["V"].mean()
        b = t[(t.phase == "B32") & t.method.str.contains("QHA", na=False)]
        bx = b.groupby("x")["G"].apply(lambda s: s.iloc[0])
        L.append(f"* {k}: fcc Al V({a.T[-1]:.0f} K)/V({f.index.min():.0f} K) = {np.interp(a.T[-1], f.index, f.values) / f.iloc[0]:.4f}" + (f"; B32 G(x) at lowest T relative to x = 0.5: " + ", ".join(f"x={x:.4f}: {(g - bx.get(0.5, np.nan))*1000:+.1f} meV" for x, g in bx.items()) if len(bx) else ""))
    # ---- 03B / 04: liquid vs solid driving force at the same composition
    L += ["", "## 03B: liquid minus solid at the same composition (eV/atom; negative = liquid stable)", "",
          "| x | solid | T (K) | " + " | ".join(labels) + " |", "|---|---|---|" + "---|" * len(labels)]
    for x, ph in ((0.0, "fcc"), (0.5, "B32"), (0.25, "Al3Li")):
        for T in a.T + [900.0]:
            row = []
            for k in labels:
                gl, xl = g_at(runs[k]["tab"], "liquid", x, T); gs, xsol = g_at(runs[k]["tab"], ph, x, T)
                row.append(f"{gl - gs:+.4f}" if np.isfinite(gl) and np.isfinite(gs) and abs(xl - x) < 0.02 else "-")
            L.append(f"| {x} | {ph} | {T:.0f} | " + " | ".join(row) + " |")
    # ---- 07: diagram features
    L += ["", "## 06-07: diagram features", "", "| feature | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
    def feat(k):
        r = runs[k]; s = r["sum"]; reg = r["reg"]
        b32l = reg[((reg.phase_a == "B32") & (reg.phase_b == "liquid")) | ((reg.phase_a == "liquid") & (reg.phase_b == "B32"))]
        fccb = reg[((reg.phase_a == "fcc") & (reg.phase_b == "B32")) | ((reg.phase_a == "B32") & (reg.phase_b == "fcc"))]
        solv = {T: (fccb[np.isclose(fccb["T"], T)][["x_a", "x_b"]].min(axis=1).max() if len(fccb[np.isclose(fccb["T"], T)]) else np.nan) for T in a.T}
        al3li = reg[(reg.phase_a == "Al3Li") | (reg.phase_b == "Al3Li")]
        return {"lowest T with liquid (eutectic bracket)": f"{s.get('lowest_T_with_liquid_K')} K; {s.get('coexistence_at_that_T')}",
                "pure Al melting bracket": str(s.get("pure_A_melting_bracket_K")),
                "B32 + liquid present up to": f"{b32l['T'].max():.0f} K" if len(b32l) else "none",
                "fcc solvus x_Li (fcc+B32 tangent)": "; ".join(f"{T:.0f} K: {v:.3f}" for T, v in solv.items()),
                "Al3Li appears": f"up to {al3li['T'].max():.0f} K" if len(al3li) else "never",
                "same-phase segments (fit noise)": str(s.get("same_phase_segments"))[:120],
                "invariants": "; ".join(f"{r_['T_low']:.0f}-{r_['T_high']:.0f} K" for r_ in r["inv"].to_dict("records"))}
    F = {k: feat(k) for k in labels}
    for key in F[labels[0]]:
        L.append(f"| {key} | " + " | ".join(F[k][key] for k in labels) + " |")
    # ---- overlay figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["tab:blue", "tab:red", "tab:green", "tab:purple", "tab:orange", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
    for (k, c) in zip(labels, colors):
        reg = runs[k]["reg"]; reg = reg[reg.phase_a != reg.phase_b]
        ax.plot(reg.x_a, reg["T"], ".", color=c, ms=3, label=f"{k}: {runs[k]['model'][:28]}"); ax.plot(reg.x_b, reg["T"], ".", color=c, ms=3)
    ax.set_xlabel("x_Li"); ax.set_ylabel("T (K)"); ax.set_title("Two-phase boundaries, same cells and spec, different MLIPs", fontsize=9); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(out, "overlay.png"), dpi=150)
    with open(os.path.join(out, "REPORT.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L)); print("->", out)


if __name__ == "__main__":
    main()
