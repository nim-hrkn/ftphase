"""Pt-Rh solid-only T-x panels with the configuration-noise features removed (2026-11-10, user request).

Reads <run>/lowT/07_two_phase_regions.tsv of the solid-only re-assemblies (assemble_lowT.py) and keeps a two-phase region
only if every phase in it passes the 0 K ordering-energy test of README "結果 1": an ordered phase is kept for an MLIP only
when E(ordered) - E(random fcc, same x) <= -7 meV/atom (configuration noise of the 32-atom random cells is ~5 meV/atom;
MACE-MPA-0 / SevenNet-MF-ompa PtRh -11.7 / -10.6 pass, their A3B phases (-5 to -6) and every GRACE-2L / NequIP-OAM-M ordered
phase (0 +- 2) fail).  Same-phase segments (fcc+fcc: Redlich-Kister fit artefact; PtRh+PtRh etc.) are dropped as well.
What remains is the physics the data support: the PtRh ordering band of the two MLIPs with a real ordering energy.
Reference marks: paper (Saengdeejing et al. 2026) DFT 210 K and PFP 258 K for fcc<->PtRh (Table 7), and the CE + canonical
MC transition temperatures of ce_mc.py (MACE 160/140/100 K, SevenNet-MF-ompa 180/120/120 K at x_Rh 0.5/0.75/0.25).
    python solid_panels_filtered.py [--out out/solid_panels_filtered.png]
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
AT = os.path.join(HERE, "..", "aiida_txdiagram", "out")
E_ORDER = {  # meV/atom, README 結果 1 (CPU seeds for MACE/SevenNet, AiiDA seeds for GRACE-2L/NequIP)
    "MACE-MPA-0": {"PtRh": -11.7, "PtRh3": -5.7, "Pt3Rh": -5.5},
    "SevenNet-MF-ompa": {"PtRh": -10.6, "PtRh3": -5.1, "Pt3Rh": -5.3},
    "GRACE-2L-OMAT": {"PtRh": 0.9, "PtRh3": 0.3, "Pt3Rh": -0.6},
    "NequIP-OAM-M": {"PtRh": 0.0, "PtRh3": 1.5, "Pt3Rh": -3.6},
}
RUNS = [("MACE-MPA-0", "ptrh_mace_mpa_0"), ("SevenNet-MF-ompa", "ptrh_sevenn_mf_ompa"), ("GRACE-2L-OMAT", "ptrh_grace_2l"), ("NequIP-OAM-M", "ptrh_nequip_oam_m")]
CEMC = {"MACE-MPA-0": {0.5: 160, 0.75: 140, 0.25: 100}, "SevenNet-MF-ompa": {0.5: 180, 0.75: 120, 0.25: 120}}
THRESH = -7.0
COLORS = {"PtRh+fcc": "#5b9bd5", "Pt3Rh+fcc": "#70ad47", "PtRh3+fcc": "#f4a259", "Pt3Rh+PtRh": "#a05195", "PtRh+PtRh3": "#d45087"}


def keep(label, pair):
    a, b = pair
    if a == b:
        return False
    for p in (a, b):
        if p != "fcc" and E_ORDER[label].get(p, 0.0) > THRESH:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "out", "solid_panels_filtered.png"))
    ap.add_argument("--T", nargs=2, type=float, default=[100.0, 1000.0])
    a = ap.parse_args()
    fig, axes = plt.subplots(1, len(RUNS), figsize=(4.2 * len(RUNS), 4.6), sharey=True)
    for ax, (label, d) in zip(axes, RUNS):
        f = os.path.join(AT, d, "lowT", "07_two_phase_regions.tsv")
        reg = pd.read_csv(f, sep="\t")
        dT = float(reg["T"].drop_duplicates().sort_values().diff().median()) if len(reg) > 1 else 10.0
        n_all, n_kept = len(reg), 0
        for r in reg.itertuples():
            pair = tuple(sorted((r.phase_a, r.phase_b), key=lambda p: (p == "fcc", p)))
            if not keep(label, pair):
                continue
            n_kept += 1
            key = "+".join(pair)
            ax.fill_between([min(r.x_a, r.x_b), max(r.x_a, r.x_b)], r.T - dT / 2, r.T + dT / 2, color=COLORS.get(key, "#999999"), lw=0, label=key)
        ax.axhline(210, color="k", ls="--", lw=0.8); ax.axhline(258, color="k", ls=":", lw=0.8)
        for x, Tc in CEMC.get(label, {}).items():
            ax.plot([x], [Tc], marker="v", color="k", ms=6, ls="none")
        ax.set_xlim(0, 1); ax.set_ylim(*a.T); ax.set_xlabel("x_Rh"); ax.set_title(f"{label}\n{n_kept}/{n_all} regions kept")
        h, l = ax.get_legend_handles_labels(); uniq = dict(zip(l, h))
        if uniq:
            ax.legend(uniq.values(), uniq.keys(), fontsize=7, loc="upper right")
    axes[0].set_ylabel("T (K)")
    fig.suptitle("Pt-Rh solids only, noise-filtered: ordered phase kept only if E(ordered) - E(random fcc) <= -7 meV/atom at 0 K; same-phase (fcc+fcc) segments dropped.\n"
                 "dashed 210 K = paper DFT, dotted 258 K = paper PFP fcc<->PtRh; triangles = CE + canonical MC transitions (ce_mc.py)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.9)); os.makedirs(os.path.dirname(a.out), exist_ok=True); fig.savefig(a.out, dpi=130)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
