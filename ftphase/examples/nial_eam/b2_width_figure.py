"""B2 NiAl composition range of the GRACE-1L Ni-Al run under three treatments, with the SGTE assessment AlNi-01Dup-4sl (ORCHID-Diagrams)
boundaries in black: (a) stage-2 solid TI as assembled by the WorkChain (constitutional sublattice model, 54-site cells with <= 3 vacancies /
6 anti-sites), (b) the same table re-assembled with the Wagner-Schottky thermal-defect model, (c) + the extended defect cells
(vacancies 4-7, anti-sites 8-10; 3008-3456-atom TI) with Wagner-Schottky.
    python b2_width_figure.py [--base nial_grace_1l] -> out_defects_mlip/b2_width_<base>.png + b2_width_<base>.md
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "aiida_txdiagram", "out"); OC = os.path.join(HERE, "..", "orchid_calphad")
sys.path.insert(0, OC)
from sgte_diagrams import SYSTEMS, load_sgte, draw_ref_boundaries, draw_run  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--base", default="nial_grace_1l"); a = ap.parse_args()
cases = [("(a) WorkChain assembly\nconstitutional sublattice, cells <= 3 Va / 6 anti-sites", os.path.join(OUT, a.base + "_ti")),
         ("(b) same table, Wagner-Schottky\nthermal defects", os.path.join(OUT, a.base + "_ti", "ws")),
         ("(c) + extended B2 cells (Va 4-7, anti-sites 8-10)\nand L1_2 cells (anti-sites 2-4), TI, Wagner-Schottky",
          os.path.join(OUT, a.base + ("_b2l12ext_merged" if os.path.isdir(os.path.join(OUT, a.base + "_b2l12ext_merged")) else "_b2ext_merged"), "ws"))]
S = SYSTEMS["nial"]; ref = next(d for d in load_sgte(S["prefix"]) if d["name"] == S["ref"])
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), sharey=True); colors, seen = {}, {}
rows = []; rows_l12 = []
for ax, (title, d) in zip(axes, cases):
    r = draw_run(ax, d, colors, seen, (900, 2000)); draw_ref_boundaries(ax, ref)
    ax.set(title=title, xlabel="x_Ni", xlim=(0.3, 0.8)); ax.title.set_fontsize(9)
    if r is not None:
        for T in (1000, 1200, 1400, 1600, 1800):
            q = r[np.isclose(r["T"], T)]
            lo = q[q.phase_b == "B2"]["x_b"].min() if (q.phase_b == "B2").any() else np.nan; hi = q[q.phase_a == "B2"]["x_a"].max() if (q.phase_a == "B2").any() else np.nan
            rows.append((title.split("\n")[0], T, lo, hi))
            l_lo = q[q.phase_b == "L12"]["x_b"].min() if (q.phase_b == "L12").any() else np.nan; l_hi = q[q.phase_a == "L12"]["x_a"].max() if (q.phase_a == "L12").any() else np.nan
            rows_l12.append((title.split("\n")[0], T, l_lo, l_hi))
axes[0].set_ylabel("T (K)")
h = {k: v for k, v in seen.items() if "B2" in k or "liquid" in k}
fig.legend(h.values(), h.keys(), loc="lower center", ncol=min(6, len(h)), fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.suptitle(f"{a.base}: B2 NiAl composition range (black = SGTE AlNi-01Dup-4sl boundaries; experiment: B2 reaches x_Ni ~ 0.45 at 1600 K on the Al side)", fontsize=9)
fig.tight_layout(rect=(0, 0.06, 1, 0.95)); out = os.path.join(HERE, "out_defects_mlip", f"b2_width_{a.base}.png"); fig.savefig(out, dpi=130); print("wrote", out)
# SGTE B2 range for reference: read the assessment's B2 phase boundaries at the same temperatures
sg = {}; sg_l12 = {}
for reg in ref.get("regions") or []:
    for side in reg:
        nm = side["phase"].split("#")[0].upper()
        tgt = sg if ("B2" in nm) else (sg_l12 if ("L12" in nm or "FCC_4SL" in nm or "ALNI3" in nm) else None)
        if tgt is not None:
            for T, x in zip(side["T"], side["x"]):
                tgt.setdefault(int(round(T / 100.0) * 100), []).append(x)
print("reference phase names:", sorted({side["phase"].split("#")[0] for reg in ref.get("regions") or [] for side in reg}))
L = [f"# B2 range [x_Ni lower, upper] vs T, {a.base}", "", "| case | 1000 K | 1200 K | 1400 K | 1600 K | 1800 K |", "|---|---|---|---|---|---|"]
for c in dict.fromkeys(r[0] for r in rows):
    L.append(f"| {c} | " + " | ".join(f"{lo:.3f}-{hi:.3f}" if lo == lo else "—" for _, T, lo, hi in [r for r in rows if r[0] == c]) + " |")
if sg:
    L.append("| SGTE AlNi-01Dup-4sl (B2 boundary points near T) | " + " | ".join(f"{min(sg[T]):.3f}-{max(sg[T]):.3f}" if T in sg else "—" for T in (1000, 1200, 1400, 1600, 1800)) + " |")
L += ["", "# L1_2 range [x_Ni lower, upper]", "", "| case | 1000 K | 1200 K | 1400 K | 1600 K | 1800 K |", "|---|---|---|---|---|---|"]
for c in dict.fromkeys(r[0] for r in rows_l12):
    L.append(f"| {c} | " + " | ".join((f"{lo:.3f}-{hi:.3f}" if lo == lo and hi == hi else "—") for _, T, lo, hi in [r for r in rows_l12 if r[0] == c]) + " |")
if sg_l12:
    L.append("| SGTE AlNi-01Dup-4sl (L1_2 boundary points near T) | " + " | ".join(f"{min(sg_l12[T]):.3f}-{max(sg_l12[T]):.3f}" if T in sg_l12 else "—" for T in (1000, 1200, 1400, 1600, 1800)) + " |")
open(out[:-4] + ".md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
