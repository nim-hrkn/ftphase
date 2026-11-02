"""Al-Li T-x diagrams of all MLIP runs side by side (artifact Fig. 7) from each run's 07_two_phase_regions.tsv.

    python mlip_panels.py            -> out/mlip_compare/panels.png

Same-phase segments (fcc+fcc, liquid+liquid: fit noise, see the WorkChain REPORT) are left out; phases are ordered
alphabetically within a pair (B32+fcc = fcc+B32).  Dashed line: experimental eutectic 875 K."""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = [("ACE (system-specific)", "alli_ace_m6"), ("GRACE-FS-OAM", "alli_grace_fs"), ("GRACE-1L-OMAT", "alli_grace_1l"), ("GRACE-2L-OMAT", "alli_grace_2l"),
        ("SevenNet-0", "alli_sevenn_0"), ("SevenNet-MF-ompa", "alli_sevenn_mf_ompa"), ("MACE-MPA-0", "alli_mace_mpa_0"),
        ("MatterSim-v1-1M", "alli_mattersim_1m"), ("NequIP-OAM-M", "alli_nequip_oam_m")]
COLORS = {"B32+fcc": "#5b9bd5", "fcc+liquid": "#70ad47", "B32+liquid": "#f4a259", "Al3Li+fcc": "#a05195", "Al3Li+liquid": "#d45087", "Al3Li+B32": "#888888"}


def main(out=os.path.join(HERE, "out", "mlip_compare", "panels.png")):
    n = len(RUNS) + 1
    ncol = 5
    fig, axes = plt.subplots((n + ncol - 1) // ncol, ncol, figsize=(4 * ncol, 3.6 * ((n + ncol - 1) // ncol)), squeeze=False)
    seen = {}
    for ax, (label, d) in zip(axes.flat, RUNS):
        r = pd.read_csv(os.path.join(HERE, "out", d, "07_two_phase_regions.tsv"), sep="\t")
        r = r[r.phase_a != r.phase_b]
        dT = float(r["T"].diff().abs()[lambda s: s > 0].min() or 10.0) if len(r) > 1 else 10.0
        for _, row in r.iterrows():
            pair = "+".join(sorted([row.phase_a, row.phase_b]))
            c = COLORS.get(pair, "#cccccc")
            h = ax.fill_between([min(row.x_a, row.x_b), max(row.x_a, row.x_b)], row["T"] - dT / 2, row["T"] + dT / 2, color=c, lw=0)
            seen.setdefault(pair, h)
        ax.axhline(875, ls="--", lw=0.8, color="k")
        ax.set(xlim=(0, 0.55), ylim=(690, 1110), xlabel="x_Li", ylabel="T (K)", title=label)
    tail = list(axes.flat)[len(RUNS):]
    for ax in tail:
        ax.axis("off")
    tail[0].text(0.02, 0.95, "Al-Li, 0 GPa, classical level\nsame cells, spec, T grid and fits\nsingle precision where available\nQHA solids, calphy TI liquid\n"
                 "dashed: experimental eutectic 875 K\n(Al melting: 933.5 K)\nsame-phase hull segments removed", va="top", fontsize=10, transform=tail[0].transAxes)
    tail[0].legend(seen.values(), seen.keys(), loc="lower left")
    fig.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=110)
    print("wrote", out)


if __name__ == "__main__":
    main()
