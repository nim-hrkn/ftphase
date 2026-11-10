"""Pt-Rh: the CALPHAD route (Saengdeejing-type TDB from MACE-MPA-0, calphad_params.py + calphad_tdb.py) next to the reference
(SGTE fcc+liquid + the paper's Table 7) and the project's hull route for the same MLIP (overlay_full.py panels).
Broken y axis 100-400 K / 1700-2400 K.   python calphad_figure.py [--tag mace_mpa_0] [--label MACE-MPA-0]
"""
import argparse, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from overlay_full import AT, SGTE, COLORS, regions, fill, sgte_lines, paper_lines
from solid_panels_filtered import CEMC

HERE = os.path.dirname(os.path.abspath(__file__))
CAL_COLORS = dict(COLORS, **{"PtRh": "#2f6db5", "Pt3Rh": "#6d2c7a", "PtRh3": "#d9781f", "Pt3Rh+PtRh": "#c9a9d4", "PtRh+PtRh3": "#f3cfa6", "liquid": "#fde9c9", "fcc": "#f2f2f2"})


def phase_name(p, x):
    return {"PTRH_I41AMD": "PtRh", "FCC_A1": "fcc", "LIQUID": "liquid"}.get(p, ("Pt3Rh" if x < 0.5 else "PtRh3") if p == "D022" else p)


def fill_grid(ax, path, dT, dx):
    path = path if os.path.exists(path) else path + ".gz"
    g = pd.read_csv(path, sep="\t")
    for r in g.itertuples():
        xph = json.loads(r[4]); names = sorted(phase_name(p, q[0]) for p, q in xph.items())
        if len(names) == 1 and names[0] == "fcc":
            continue
        key = "+".join(sorted(names, key=lambda p: (p in ("fcc", "liquid"), p)))
        if key == "PtRh3+Pt3Rh":
            key = "Pt3Rh+PtRh3"
        ax.fill_between([r.x_Rh - dx / 2, r.x_Rh + dx / 2], r.T_K - dT / 2, r.T_K + dT / 2, color=CAL_COLORS.get(key, "#bbbbbb"), lw=0, label=key)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="mace_mpa_0"); ap.add_argument("--label", default="MACE-MPA-0")
    ap.add_argument("--out", default=None); a = ap.parse_args()
    cal = os.path.join(HERE, "out", f"calphad_{a.tag}"); out = a.out or os.path.join(cal, "calphad_vs_hull.png")
    sg = json.load(open(SGTE, encoding="utf-8")); inv = json.load(open(os.path.join(cal, "invariants_plain_lowT.json")))
    fig, axes = plt.subplots(2, 3, figsize=(12.0, 6.4), sharex=True, gridspec_kw={"height_ratios": [1.1, 1.0], "hspace": 0.08})
    # 1: reference
    top, bot = axes[0, 0], axes[1, 0]
    sgte_lines(top, sg, fillband=True); paper_lines(bot)
    bot.text(0.02, 0.9, "paper Table 7: PFP solid, DFT dashed\n(fcc<->PtRh 258/211 K, PtRh3 235/156 K,\n Pt3Rh 146 K; eutectoids 146, 211/149 K)", fontsize=7, transform=bot.transAxes, va="top")
    top.set_title("reference: SGTE PtRh-98Jac (fcc+L)\n+ Saengdeejing 2026 Table 7", fontsize=9.5)
    # 2: hull route of the same MLIP (07 liquid window of the +TI-ends run, filtered low-T solids, CE+MC)
    top, bot = axes[0, 1], axes[1, 1]
    base = f"ptrh_{a.tag}"
    fill(top, regions(os.path.join(AT, base + "_ti", "07_two_phase_regions.tsv"))); sgte_lines(top, sg)
    fill(bot, regions(os.path.join(AT, base, "lowT", "07_two_phase_regions.tsv")), label=a.label, filt=True); paper_lines(bot)
    for x, Tc in CEMC.get(a.label, {}).items():
        bot.plot([x], [Tc], marker="v", color="k", ms=6, ls="none", label="CE+MC T_c")
    top.set_title(f"{a.label}, hull route (ftphase 01-07)\nQHA/TI solids + calphy liquid", fontsize=9.5)
    # 3: CALPHAD route
    top, bot = axes[0, 2], axes[1, 2]
    fill_grid(top, os.path.join(cal, "grid_plain.tsv"), 10.0, 0.005); sgte_lines(top, sg)
    fill_grid(bot, os.path.join(cal, "grid_plain_lowT.tsv"), 2.0, 0.005); paper_lines(bot)
    for x, Tc in CEMC.get(a.label, {}).items():
        bot.plot([x], [Tc], marker="v", color="k", ms=6, ls="none")
    pt = inv.get("PTRH_I41AMD_single_phase_Tmax_K"); d0 = inv.get("D022_single_phase_Tmax_K")
    eut = [m for m in inv.get("mapping_invariants", []) if m.get("T", 1e9) < 1000]
    txt = f"fcc<->PtRh {pt:.0f} K, fcc<->PtRh3 {d0:.0f} K" if pt and d0 else ""
    if eut:
        Ts = sorted(set(round(m["T"]) for m in eut)); txt += "\neutectoids " + ", ".join(f"{t} K" for t in Ts)
    bot.text(0.02, 0.9, txt, fontsize=7, transform=bot.transAxes, va="top")
    top.set_title(f"{a.label}, CALPHAD route (paper's method)\nSGTE + RK fcc + 2-sublattice CEF, ideal L", fontsize=9.5)
    for j in range(3):
        axes[0, j].set_ylim(1700, 2400); axes[1, j].set_ylim(100, 400); axes[0, j].set_xlim(0, 1)
        axes[1, j].set_xlabel("x_Rh"); axes[0, j].spines["bottom"].set_visible(False); axes[1, j].spines["top"].set_visible(False)
        axes[0, j].tick_params(labelbottom=False, bottom=False)
    axes[0, 0].set_ylabel("T (K)"); axes[1, 0].set_ylabel("T (K)")
    h = {}
    for ax in axes.flat:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            h.setdefault(ll, hh)
    fig.legend(h.values(), h.keys(), loc="lower center", ncol=7, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Pt-Rh with one MLIP by two routes (axis broken 400-1700 K): black = SGTE fcc/liquid and the paper's ordering reactions (PFP solid, DFT dashed), triangles = CE+MC", fontsize=9)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95)); fig.savefig(out, dpi=130); print("wrote", out)


if __name__ == "__main__":
    main()
