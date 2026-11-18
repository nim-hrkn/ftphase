"""Pt-Rh, CALPHAD route (method of [Saengdeejing2026]) with several MLIPs: the ordering window 40-320 K side by side, with and
without the short-range-order term of the fcc solution (sro_fit.py) where a cluster expansion exists.
Grids: calphad_tdb.py out/calphad_<tag> --model plain --T 40 320 --dT 2 --suffix _z320[_sro] [--sro out_ce_<mlip>/sro_fit.json]
    python calphad_zoom_panels.py   -> out/calphad_zoom_panels.png, out/calphad_zoom_panels.json
"""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from overlay_full import PAPER
from calphad_figure import CAL_COLORS, phase_name

HERE = os.path.dirname(os.path.abspath(__file__)); PRETTY = {"PtRh": "PtRh", "Pt3Rh": "Pt$_3$Rh", "PtRh3": "PtRh$_3$", "fcc": "fcc"}
PANELS = [("mace_mpa_0", "MACE-MPA-0", "_z320"), ("mace_mpa_0", "MACE-MPA-0 + SRO in fcc", "_z320_sro"), ("sevenn_mf_ompa", "SevenNet-MF-ompa", "_z320"), ("sevenn_mf_ompa", "SevenNet-MF-ompa + SRO in fcc", "_z320_sro"),
          ("grace_2l", "GRACE-2L-OMAT", "_z320"), ("nequip_oam_m", "NequIP-OAM-M", "_z320")]
T0, T1, dT, dx = 40.0, 320.0, 2.0, 0.005


def draw(ax, tag, label, suf):
    cal = os.path.join(HERE, "out", f"calphad_{tag}"); f = os.path.join(cal, f"grid_plain{suf}_lowT.tsv")
    if not os.path.exists(f):
        ax.text(0.5, 0.5, "not computed", transform=ax.transAxes, ha="center"); ax.set_title(label, fontsize=9.5); return None
    g = pd.read_csv(f, sep="\t"); inv = json.load(open(os.path.join(cal, f"invariants_plain{suf}_lowT.json"))); cells = {}
    for r in g.itertuples():
        xph = json.loads(r[4]); names = sorted(phase_name(p, q[0]) for p, q in xph.items()); key = "+".join(sorted(set(names), key=lambda p: (p == "fcc", p)))
        key = "Pt3Rh+PtRh3" if key == "PtRh3+Pt3Rh" else key; cells.setdefault(key, []).append((r.T_K, r.x_Rh))
        if key != "fcc":
            ax.fill_between([r.x_Rh - dx / 2, r.x_Rh + dx / 2], r.T_K - dT / 2, r.T_K + dT / 2, color=CAL_COLORS.get(key, "#bbbbbb"), lw=0)
    box = dict(fc="w", ec="none", alpha=0.8, pad=0.6); top = {}
    for key, c in cells.items():
        c = np.array(c)
        if key != "fcc":
            for p in key.split("+"):
                if p != "fcc":
                    top[p] = max(top.get(p, 0.0), float(c[:, 0].max()))
        if len(c) < 60 or key == "fcc":
            continue
        Tm = np.median(c[:, 0]); xs = c[abs(c[:, 0] - Tm) < 1.1, 1]; w = xs.max() - xs.min()
        ax.text(xs.mean(), Tm, " + ".join(PRETTY.get(p, p) for p in key.split("+")), fontsize=8 if w > 0.12 else 6.5, ha="center", va="center", rotation=0 if w > 0.12 else 90, bbox=box)
    ax.text(0.5, T1 - 12, "fcc (disordered)", fontsize=8.5, ha="center", va="top", bbox=box)
    for name, Tp, Td, xs in PAPER:      # [Saengdeejing2026] Table 7: PFP solid, DFT dashed
        lo, hi = (min(xs), max(xs)) if len(xs) > 1 else (xs[0] - 0.03, xs[0] + 0.03)
        ax.plot([lo, hi], [Tp, Tp], color="k", lw=1.6, solid_capstyle="butt")
        if Td is not None:
            ax.plot([lo, hi], [Td, Td], color="k", lw=1.2, ls="--")
    res = {"label": label, "fcc<->PtRh_K": inv.get("PTRH_I41AMD_single_phase_Tmax_K"), "top_of_fields_K": top}
    d022 = [(T, x) for T, x in cells.get("PtRh3", [])]; res["fcc<->PtRh3_K"] = max((T for T, x in d022 if 0.6 < x < 0.9), default=None)
    d022 = [(T, x) for T, x in cells.get("Pt3Rh", [])]; res["fcc<->Pt3Rh_K"] = max((T for T, x in d022 if 0.1 < x < 0.4), default=None)
    txt = "this TDB: " + ", ".join(f"{n} {v:.0f} K" if v else f"{n} none" for n, v in (("PtRh", res["fcc<->PtRh_K"]), ("PtRh$_3$", res["fcc<->PtRh3_K"]), ("Pt$_3$Rh", res["fcc<->Pt3Rh_K"])))
    ax.text(0.5, T0 + 4, txt, fontsize=7.5, ha="center", va="bottom", color="#b00020", bbox=box)
    if suf.endswith("_sro"):      # the SRO term was fitted to the disordered state above 1.15 x the order-disorder temperature of the MC cell: below that line it is an extrapolation
        fit = json.load(open(os.path.join(HERE, f"out_ce_{tag.replace('_', '-')}", "sro_fit.json"))); xv = sorted(float(k) for k in fit["T_c_MC_K"]); tv = [max(1.15 * fit["T_c_MC_K"][f"{k:g}" if f"{k:g}" in fit["T_c_MC_K"] else str(k)], T0) for k in xv]
        ax.plot(xv, tv, color="k", lw=1.0, ls=":"); ax.fill_between(xv, T0, tv, facecolor="none", edgecolor="0.35", hatch="///", lw=0, alpha=0.5)
        ax.text(0.5, max(tv) + 6, "below the dotted line the SRO term is extrapolated (hatched: not reliable)", fontsize=7, ha="center", va="bottom", bbox=box)
        res["sro_valid_above_K_at_x0.5"] = float(np.interp(0.5, xv, tv)); res["ordered_phase_above_validity_line"] = bool(any(T > np.interp(x, xv, tv) for k2, c2 in cells.items() if k2 != "fcc" for T, x in c2))
    ax.set(xlim=(0, 1), ylim=(T0, T1)); ax.set_title(label, fontsize=9.5); return res


def main():
    n = len(PANELS); fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.4), sharex=True, sharey=True); out = {}
    for ax, (tag, label, suf) in zip(axes.T.ravel() if False else axes.ravel(), PANELS):
        out[label] = draw(ax, tag, label, suf)
    for ax in axes[-1]: ax.set_xlabel("x_Rh")
    for ax in axes[:, 0]: ax.set_ylabel("T (K)")
    fig.suptitle("Pt-Rh ordering window by the CALPHAD route with four MLIPs (coloured: ordered single-phase and two-phase fields; white: fcc)\n"
                 "Black lines: [Saengdeejing2026] Table 7 (PFP solid: 258, 235, 146 K, eutectoids 211, 146 K; DFT dashed: 211, 156 K, eutectoid 149 K)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "out", "calphad_zoom_panels.png"), dpi=140); json.dump(out, open(os.path.join(HERE, "out", "calphad_zoom_panels.json"), "w"), indent=1); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
