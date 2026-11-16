"""Figure of the tip of G(x) at the Al-Li line compounds (data: out/2_curvature.json from curvature_compounds.py).
The common tangent slope at stoichiometry (dG/dx = mu_Li - mu_Al, about 1.4 eV) is subtracted so that the shape of the tip is
visible: solid = Wagner-Schottky G(x), dashed = the parabola 0.5 d2G/dx2 (x - x0)^2 fitted within x0 +- 0.012."""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from ftphase.configurational import wagner_schottky_curve

HERE = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(os.path.join(HERE, "out", "2_curvature.json")))
SC = {"Al3Li (L1_2)": (3, 1), "Al2Li3 (R-3m)": (2, 3), "Al4Li9 (C2/m)": (4, 9)}; PRETTY = {"Al3Li (L1_2)": "Al$_3$Li (L1$_2$)", "Al2Li3 (R-3m)": "Al$_2$Li$_3$ (R-3m)", "Al4Li9 (C2/m)": "Al$_4$Li$_9$ (C2/m)"}
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), sharey=True)
for ax, (name, r) in zip(axes, R.items()):
    x0 = r["x0"]; xs = np.linspace(x0 - 0.03, x0 + 0.03, 241)
    for T, c in ((300, "#1f77b4"), (500, "#ff7f0e"), (700, "#2ca02c")):
        g = np.array(wagner_schottky_curve(xs, float(T), SC[name], r["defect_energies_raw_eV"], g0_atom=0.0)); v = r["T"][str(T)]
        g0 = float(np.interp(x0, xs, g)); tip = (g - g0 - v["dG_dx_eV"] * (xs - x0)) * 1000
        ax.plot(xs, tip, color=c, lw=1.8, label=f"{T} K: {v['d2G_dx2_eV']:.1f} eV ({v['d2G_dx2_kJ_mol']:.0f} kJ/mol)")
        ax.plot(xs, 0.5 * v["d2G_dx2_eV"] * (xs - x0) ** 2 * 1000, color=c, lw=0.9, ls="--")
    ax.axvline(x0, color="0.6", lw=0.6); ax.axvspan(x0 - 0.012, x0 + 0.012, color="0.92", zorder=0)
    ax.set(xlabel="x_Li", title=f"{PRETTY[name]}, x$_0$ = {x0:.4f}"); ax.title.set_fontsize(10); ax.legend(fontsize=7.5, title="d$^2$G/dx$^2$ at x$_0$", title_fontsize=8, loc="upper center")
axes[0].set_ylabel("G(x) − G(x$_0$) − (dG/dx)(x − x$_0$)   (meV/atom)"); axes[0].set_ylim(-0.5, 16)
fig.suptitle("ACE Al-Li line compounds: tip of G(x) from point-defect energies (solid) and the fitted parabola (dashed); grey band = fit range ±0.012", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "out", "2_curvature_tip.png"), dpi=150); print("wrote 2_curvature_tip.png")
