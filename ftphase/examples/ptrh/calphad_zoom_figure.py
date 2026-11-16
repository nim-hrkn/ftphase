"""Pt-Rh, CALPHAD route (Saengdeejing-type TDB from MACE-MPA-0): the ordering window enlarged, to compare with the paper's Fig. 10
(-200 .. 100 degC).  Left: 40-220 K from the 2 K x 0.005 grid (calphad_tdb.py --model plain --T 40 220 --dT 2 --suffix _zoom),
phase fields named, the paper's Table 7 reactions as lines (PFP solid, DFT dashed), right axis in degC.  Right: the paper's Fig. 10
is not redrawn here; its reaction temperatures are listed.     python calphad_zoom_figure.py [--tag mace_mpa_0] [--label MACE-MPA-0]
"""
import argparse, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from overlay_full import PAPER
from calphad_figure import CAL_COLORS, phase_name

HERE = os.path.dirname(os.path.abspath(__file__))
PRETTY = {"PtRh": "PtRh", "Pt3Rh": "Pt$_3$Rh", "PtRh3": "PtRh$_3$", "fcc": "fcc"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="mace_mpa_0"); ap.add_argument("--label", default="MACE-MPA-0"); a = ap.parse_args()
    cal = os.path.join(HERE, "out", f"calphad_{a.tag}"); g = pd.read_csv(os.path.join(cal, "grid_plain_zoom_lowT.tsv"), sep="\t")
    inv = json.load(open(os.path.join(cal, "invariants_plain_zoom_lowT.json"))); dT, dx = 2.0, 0.005
    fig, ax = plt.subplots(figsize=(8.6, 6.0)); cells = {}
    for r in g.itertuples():
        xph = json.loads(r[4]); names = sorted(phase_name(p, q[0]) for p, q in xph.items())
        key = "+".join(sorted(set(names), key=lambda p: (p == "fcc", p)))
        if key == "PtRh3+Pt3Rh":
            key = "Pt3Rh+PtRh3"
        cells.setdefault(key, []).append((r.T_K, r.x_Rh))
        if key != "fcc":
            ax.fill_between([r.x_Rh - dx / 2, r.x_Rh + dx / 2], r.T_K - dT / 2, r.T_K + dT / 2, color=CAL_COLORS.get(key, "#bbbbbb"), lw=0)
    box = dict(fc="w", ec="none", alpha=0.8, pad=0.8)
    for key, c in cells.items():
        c = np.array(c)
        if len(c) < 40:
            continue
        if key == "fcc":
            ax.text(0.5, 198, "fcc (disordered solid solution)", fontsize=10, ha="center", bbox=box); continue
        Tm = np.median(c[:, 0]); xs = c[abs(c[:, 0] - Tm) < 1.1, 1]
        lab = " + ".join(PRETTY.get(p, p) for p in key.split("+")); w = xs.max() - xs.min()
        ax.text(xs.mean(), Tm, lab, fontsize=9 if w > 0.1 else 7.5, ha="center", va="center", rotation=0 if w > 0.1 else 90, bbox=box)
    for name, Tp, Td, xs in PAPER:      # the paper's Table 7: PFP solid, DFT dashed
        lo, hi = (min(xs), max(xs)) if len(xs) > 1 else (xs[0] - 0.03, xs[0] + 0.03)
        if Tp <= 220:
            ax.plot([lo, hi], [Tp, Tp], color="k", lw=1.8, solid_capstyle="butt")
        if Td is not None and Td <= 220:
            ax.plot([lo, hi], [Td, Td], color="k", lw=1.3, ls="--")
    eut = sorted({round(m["T"], 1): m for m in inv.get("mapping_invariants", [])}.items())
    for T, m in eut:
        ax.plot([min(m["x"]), max(m["x"])], [T, T], color="#b00020", lw=1.0)
        ax.text(max(m["x"]) + 0.01, T, f"{T:.0f} K", color="#b00020", fontsize=8, va="center")
    for key, lab, x in (("PTRH_I41AMD_single_phase_Tmax_K", "fcc ↔ PtRh", 0.49), ("D022_single_phase_Tmax_K", "fcc ↔ PtRh$_3$", 0.77)):
        T = inv.get(key)
        if T:
            ax.annotate(f"{lab} {T:.0f} K", (x, T), xytext=(x + (0.10 if "3" in lab else 0.0), T + (14 if "3" in lab else 9)), fontsize=8.5, ha="center", color="#b00020", arrowprops=dict(arrowstyle="-", lw=0.6, color="#b00020"))
    ax.set(xlim=(0, 1), ylim=(40, 220), xlabel="x_Rh", ylabel="T (K)")
    ax2 = ax.twinx(); ax2.set_ylim(40 - 273.15, 220 - 273.15); ax2.set_ylabel("T (°C)")
    ax.text(0.01, 0.985, "black lines: Saengdeejing et al. 2026, Table 7 (PFP solid, DFT dashed), shown where ≤ 220 K\n"
            "  (PFP: fcc↔PtRh 258 K, fcc↔PtRh$_3$ 235 K, fcc↔Pt$_3$Rh 146 K, eutectoids 211 / 146 K; DFT: 211, 156 K, eutectoid 149 K)\n"
            "red: this TDB (invariant reactions and the tops of the ordered single-phase fields)", fontsize=7.2, transform=ax.transAxes, va="top", bbox=box)
    ax.set_title(f"Pt-Rh, {a.label}, CALPHAD route (method of Saengdeejing et al. 2026): ordering window 40-220 K", fontsize=10)
    fig.tight_layout(); out = os.path.join(cal, "calphad_zoom.png"); fig.savefig(out, dpi=150); print("wrote", out)
    for key, c in cells.items():
        c = np.array(c); print(key, "T %.0f-%.0f K, x %.3f-%.3f, cells %d" % (c[:, 0].min(), c[:, 0].max(), c[:, 1].min(), c[:, 1].max(), len(c)))


if __name__ == "__main__":
    main()
