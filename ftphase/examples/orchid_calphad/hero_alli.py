"""README hero figure (English): Al-Li by the CALPHAD assessment AlLi-20Lon, the system-specific ACE and two universal MLIPs,
each MLIP panel with the assessment's boundaries in black.  4 panels in one row, 1600 px wide.
    python hero_alli.py [--out ../../../docs/img/alli_hero.png]
"""
import argparse, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sgte_diagrams import AT, SYSTEMS, load_sgte, draw_sgte, draw_run, draw_ref_boundaries

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = [("ACE (system-specific, pyiron workshop)", os.path.join(AT, "alli_ace_m6")),
          ("SevenNet-MF-ompa (universal MLIP, closest)", os.path.join(AT, "alli_sevenn_mf_ompa")),
          ("SevenNet-0 (universal MLIP, fcc phonons too soft)", os.path.join(AT, "alli_sevenn_0"))]
# raw two-phase pair (run names and the assessment's CALPHAD phase names) -> legend label; pairs with the same label share a colour
NICE = {"B32+fcc": "fcc(Al) + B32 AlLi", "BCC_4SL+FCC_A1": "fcc(Al) + B32 AlLi", "BCC_4SL+FCC_4SL": "fcc(Al) + B32 AlLi",
        "fcc+liquid": "fcc(Al) + liquid", "FCC_A1+LIQUID": "fcc(Al) + liquid", "FCC_4SL+LIQUID": "fcc(Al) + liquid",
        "B32+liquid": "B32 + liquid", "BCC_4SL+LIQUID": "B32 + liquid",
        "Al2Li3+B32": "B32 + Al2Li3", "AL2LI3+BCC_4SL": "B32 + Al2Li3", "AL2LI3+LIQUID": "Al2Li3 + liquid",
        "Al2Li3+Al4Li9": "Al2Li3 + Al4Li9", "AL4LI9+LIQUID": "Al4Li9 + liquid", "AL4LI9+BCC_4SL": "B32 + Al4Li9",
        "Al4Li9+bcc": "Al4Li9 + bcc(Li)", "Al4Li9+B32": "B32 + Al4Li9", "B32+bcc": "B32 + bcc(Li)", "AL4LI9+BCC_A2": "Al4Li9 + bcc(Li)", "BCC_A2+LIQUID": "bcc(Li) + liquid", "Al2Li3+bcc": "Al2Li3 + bcc(Li)",
        "AL2LI3+ALLI2": "AlLi2 (assessment only)", "AL4LI9+ALLI2": "AlLi2 (assessment only)", "ALLI2+LIQUID": "AlLi2 (assessment only)",
        "Al3Li+fcc": "fcc + Al3Li (MLIP, metastable)", "Al3Li+B32": "Al3Li + B32 (MLIP, metastable)", "fcc+fcc": "same phase (fit noise)", "bcc+bcc": "same phase (fit noise)", "liquid+liquid": "same phase (fit noise)"}
LABEL_COLORS = {"fcc(Al) + B32 AlLi": "#f9c0dc", "fcc(Al) + liquid": "#8fc37e", "B32 + liquid": "#a05195", "B32 + Al2Li3": "#f4a259", "Al2Li3 + liquid": "#e8734a",
                "Al2Li3 + Al4Li9": "#6a9bd1", "Al4Li9 + liquid": "#3d6fb4", "B32 + Al4Li9": "#2b4c7e", "Al4Li9 + bcc(Li)": "#c94c4c", "bcc(Li) + liquid": "#7fb5c9",
                "Al2Li3 + bcc(Li)": "#d9a066", "B32 + bcc(Li)": "#8c6d46", "AlLi2 (assessment only)": "#9e9e9e", "fcc + Al3Li (MLIP, metastable)": "#ffd27f", "Al3Li + B32 (MLIP, metastable)": "#cde7c3", "same phase (fit noise)": "#e0e0e0"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "..", "docs", "img", "alli_hero.png")); a = ap.parse_args()
    S = SYSTEMS["alli"]; ref = next(d for d in load_sgte(S["prefix"]) if d["name"] == S["ref"])
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.3))
    colors = {pair: LABEL_COLORS[lab] for pair, lab in NICE.items()}; seen = {}
    draw_sgte(axes[0], ref, S["overlay_T"], colors, seen)
    axes[0].set_title("CALPHAD assessment (AlLi-20Lon, SGTE)\nexperiment-based reference", fontsize=10)
    for ax, (label, run_dir) in zip(axes[1:], PANELS):
        draw_run(ax, run_dir, colors, seen, S["overlay_T"]); draw_ref_boundaries(ax, ref)
        ax.set_title(label + "\nftphase: MLIP + QHA + calphy TI, no fitting", fontsize=10)
    for ax in axes:
        ax.set(xlabel="x_Li", xlim=(0, 1)); ax.tick_params(labelsize=9)
    axes[0].set_ylabel("T (K)")
    merged = {}
    for pair, h in seen.items():
        merged.setdefault(NICE.get(pair, pair), h)
    order = list(LABEL_COLORS) + [k for k in merged if k not in LABEL_COLORS]
    merged = {k: merged[k] for k in order if k in merged}
    fig.legend(merged.values(), merged.keys(), loc="lower center", ncol=min(6, len(merged)), fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Al-Li phase diagram: CALPHAD assessment vs. first-principles-style MLIP calculations (black lines = assessment boundaries, dashed = invariants)", fontsize=11)
    fig.tight_layout(rect=(0, 0.12, 1, 0.94)); fig.savefig(a.out, dpi=100); print("wrote", a.out)


if __name__ == "__main__":
    main()
