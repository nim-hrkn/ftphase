"""Pt-Rh over the whole temperature range: SGTE fcc+liquid (ORCHID-Diagrams) + the paper's ordering reactions (Table 7) as the
reference, next to each MLIP's liquid window (WorkChain 07, 1910-2400 K; the +TI-ends run where it exists) and its noise-filtered
solid-only re-assembly (assemble_lowT.py + the solid_panels_filtered.py rule).  Broken y axis: 100-400 K and 1700-2400 K.
    python overlay_full.py [--out out/overlay_ptrh_full.png]
"""
import argparse
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from solid_panels_filtered import E_ORDER, THRESH, CEMC, keep

HERE = os.path.dirname(os.path.abspath(__file__))
AT = os.path.join(HERE, "..", "aiida_txdiagram", "out")
SGTE = os.path.join(HERE, "..", "..", "..", "data", "orchid-v2026.10", "phase-diagrams", "orchid-phase-diagrams-v2026.10", "phase-diagrams", "sgte", "PtRh-98Jac.json")
RUNS = [("MACE-MPA-0", "ptrh_mace_mpa_0", "ptrh_mace_mpa_0_ti"), ("SevenNet-MF-ompa", "ptrh_sevenn_mf_ompa", None),
        ("GRACE-2L-OMAT", "ptrh_grace_2l", "ptrh_grace_2l_ti"), ("NequIP-OAM-M", "ptrh_nequip_oam_m", "ptrh_nequip_oam_m_ti")]
# Saengdeejing et al. 2026, Table 7 (deg C -> K); (T_PFP, T_DFT or None, x points)
PAPER = [("fcc <-> Pt3Rh + PtRh", 145.6, None, (0.2576, 0.2506, 0.4935)), ("fcc <-> PtRh + PtRh3", 211.0, 149.1, (0.6533, 0.5144, 0.7419)),
         ("fcc <-> Pt3Rh", 145.7, None, (0.2505,)), ("fcc <-> PtRh", 257.8, 210.6, (0.5018,)), ("fcc <-> PtRh3", 234.7, 156.0, (0.748,))]
COLORS = {"fcc+liquid": "#70ad47", "PtRh+fcc": "#5b9bd5", "Pt3Rh+fcc": "#a05195", "PtRh3+fcc": "#f4a259"}


def regions(path):
    return pd.read_csv(path, sep="\t") if os.path.exists(path) else None


def fill(ax, reg, label=None, filt=False):
    if reg is None:
        return
    dT = float(reg["T"].drop_duplicates().sort_values().diff().median()) if len(reg) > 1 else 10.0
    for r in reg.itertuples():
        pair = tuple(sorted((r.phase_a, r.phase_b), key=lambda p: (p in ("fcc", "liquid"), p)))
        if filt and not keep(label, pair):
            continue
        if pair[0] == pair[1]:
            continue
        key = "+".join(pair)
        ax.fill_between([min(r.x_a, r.x_b), max(r.x_a, r.x_b)], r.T - dT / 2, r.T + dT / 2, color=COLORS.get(key, "#bbbbbb"), lw=0, label=key)


def sgte_lines(ax, d, fillband=False):
    for a, b in d.get("regions") or []:
        n = min(len(a["T"]), len(b["T"]))
        if fillband:
            ax.fill_betweenx(a["T"][:n], a["x"][:n], b["x"][:n], color="#c8c8c8", lw=0, alpha=0.9, label="FCC_A1+LIQUID (SGTE)")
        ax.plot(a["x"][:n], a["T"][:n], "k-", lw=1); ax.plot(b["x"][:n], b["T"][:n], "k-", lw=1)


def paper_lines(ax):
    for name, Tp, Td, xs in PAPER:
        lo, hi = (min(xs), max(xs)) if len(xs) > 1 else (xs[0] - 0.03, xs[0] + 0.03)
        ax.plot([lo, hi], [Tp, Tp], color="k", lw=1.6, solid_capstyle="butt")
        if Td is not None:
            ax.plot([lo, hi], [Td, Td], color="k", lw=1.2, ls="--")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "out", "overlay_ptrh_full.png")); a = ap.parse_args()
    sg = json.load(open(SGTE, encoding="utf-8"))
    cols = 1 + len(RUNS)
    fig, axes = plt.subplots(2, cols, figsize=(3.9 * cols, 6.2), sharex=True, gridspec_kw={"height_ratios": [1.1, 1.0], "hspace": 0.08})
    # reference column
    top, bot = axes[0, 0], axes[1, 0]
    sgte_lines(top, sg, fillband=True); paper_lines(bot)
    bot.text(0.02, 0.9, "paper Table 7: PFP solid, DFT dashed\n(fcc<->PtRh 258/211 K, PtRh3 235/156 K,\n Pt3Rh 146 K; eutectoids 146, 211/149 K)", fontsize=7, transform=bot.transAxes, va="top")
    top.set_title("CALPHAD SGTE PtRh-98Jac\n+ paper (Saengdeejing 2026)", fontsize=10)
    for (label, base, ti), j in zip(RUNS, range(1, cols)):
        top, bot = axes[0, j], axes[1, j]
        liq = regions(os.path.join(AT, ti or base, "07_two_phase_regions.tsv"))
        fill(top, liq); sgte_lines(top, sg)
        low = regions(os.path.join(AT, base, "lowT", "07_two_phase_regions.tsv"))
        fill(bot, low, label=label, filt=True); paper_lines(bot)
        for x, Tc in CEMC.get(label, {}).items():
            bot.plot([x], [Tc], marker="v", color="k", ms=6, ls="none")
        top.set_title(label + ("  (liquid: +TI ends run)" if ti else "  (liquid: QHA run)"), fontsize=10)
    for j in range(cols):
        axes[0, j].set_ylim(1700, 2400); axes[1, j].set_ylim(100, 400); axes[0, j].set_xlim(0, 1)
        axes[1, j].set_xlabel("x_Rh"); axes[0, j].spines["bottom"].set_visible(False); axes[1, j].spines["top"].set_visible(False)
        axes[0, j].tick_params(labelbottom=False, bottom=False)
    axes[0, 0].set_ylabel("T (K)"); axes[1, 0].set_ylabel("T (K)")
    h, l = {}, []
    for ax in axes.flat:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            h.setdefault(ll, hh)
    fig.legend(h.values(), h.keys(), loc="lower center", ncol=6, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Pt-Rh, 100-400 K and 1700-2400 K (axis broken): black = SGTE PtRh-98Jac fcc/liquid boundaries and the paper's ordering reactions; "
                 "MLIP solids noise-filtered (ordered phase kept only if E_order <= %.0f meV/atom at 0 K), triangles = CE+MC" % THRESH, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95)); fig.savefig(a.out, dpi=130); print("wrote", a.out)


if __name__ == "__main__":
    main()
