"""Figure 18: G(x) around stoichiometry of the four ACE Al-Li compounds in two treatments.
  solid  = Wagner-Schottky: one point defect in a ~100-site cell, static energies, non-interacting defects (curvature_compounds.py, compound_width.py for B32)
  dashed = 'phase with a composition range': small cells with one anti-site on each side (circles), QHA free energy + two-sublattice
           anti-site configurational entropy, spline through the three compositions (B32: example 6; the others: range_phase_compounds.py)
The common tangent slope of the Wagner-Schottky curve at stoichiometry (dG/dx = mu_Li - mu_Al, about 1.3-1.5 eV) is subtracted from
both, so that the shape is visible.  The legend gives d2G/dx2 at x0 (Wagner-Schottky: parabola fit within x0 +- 0.012, grey band)."""
import json, os, sys
import numpy as np
import pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from ftphase.configurational import wagner_schottky_curve
from ftphase.records import FreeEnergyTable
from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table
from ftphase.aiida.functions import _site_model

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); R = json.load(open(os.path.join(OUT, "2_curvature.json")))
EB32 = json.load(open(os.path.join(OUT, "5_compound_width.json")))["defect_energies_raw_eV"]["B32"]
old = FreeEnergyTable.from_tsv(os.path.join(HERE, "..", "alli_ace_txdiagram", "out_full", "05_free_energies.tsv"))
PAN = [("Al3Li", "Al$_3$Li (L1$_2$)", 0.25, (3, 1), R["Al3Li (L1_2)"]["defect_energies_raw_eV"], 108, 32, 0.045),
       ("B32", "B32 AlLi", 0.5, (1, 1), EB32, 128, 16, 0.07),
       ("Al2Li3", "Al$_2$Li$_3$ (R-3m)", 0.6, (2, 3), R["Al2Li3 (R-3m)"]["defect_energies_raw_eV"], 135, 30, 0.045),
       ("Al4Li9", "Al$_4$Li$_9$ (C2/m)", 9 / 13, (4, 9), R["Al4Li9 (C2/m)"]["defect_energies_raw_eV"], 104, 26, 0.045)]


def range_table(name, x0):
    if name == "B32":
        return FreeEnergyTable.from_dataframe(old.df[old.df.phase == "B32"].copy(), old.meta)       # already carries the sublattice term
    t = FreeEnergyTable.from_rows(pd.read_csv(os.path.join(OUT, f"6_range_{name}.tsv"), sep="\t").to_dict("records"), {})
    return add_configurational_term(t, name, "sublattice", site_model=_site_model("b32_antisite", x0))


fig, axes = plt.subplots(2, 2, figsize=(14.5, 10.5)); S = {}
for ax, (name, pretty, x0, sc, e, nws, nsm, half) in zip(axes.ravel(), PAN):
    xs = np.linspace(x0 - half, x0 + half, 561); tab = range_table(name, x0); S[name] = {}
    DF = json.load(open(os.path.join(OUT, f"7_defectF_{name}.json")))["sizes"]; big = DF[str(max(int(q) for q in DF))]; TT = np.array(big["T"])
    MAP = {"A_on_B": "Al_on_Li", "B_on_A": "Li_on_Al", "Va_on_B": "Va_Li", "Va_on_A": "Va_Al"}
    for T, c in ((300, "#1f77b4"), (500, "#ff7f0e"), (700, "#2ca02c")):
        m = abs(xs - x0) <= 0.012
        gp = old.df[(old.df.phase == name) & np.isclose(old.df.x, x0, atol=1e-3)].sort_values("T"); G0 = float(np.interp(T, gp["T"], gp["G"]))     # perfect compound: true g0 (vacancies change the atom count)
        # (a) static point-defect energies (thin solid): own tangent removed
        g = np.array(wagner_schottky_curve(xs, float(T), sc, e, g0_atom=G0)); pf0 = np.polyfit(xs[m] - x0, g[m], 2); g0 = float(np.interp(x0, xs, g))
        ax.plot(xs, (g - g0 - pf0[1] * (xs - x0)) * 1000, color=c, lw=0.9, label=f"{T} K static ε: {2 * pf0[0]:.1f} eV")
        # (b) temperature-dependent defect free energies eps_d(T) of the largest cell (thick solid): own tangent removed; the dashed range-phase curve uses this tangent
        eT = {k: float(np.interp(T, TT, big["defects"][v]["eps_T_eV"])) for k, v in MAP.items()}
        g = np.array(wagner_schottky_curve(xs, float(T), sc, eT, g0_atom=G0)); pf = np.polyfit(xs[m] - x0, g[m], 2); slope = pf[1]; g0 = float(np.interp(x0, xs, g))
        ax.plot(xs, (g - g0 - slope * (xs - x0)) * 1000, color=c, lw=2.0, label=f"{T} K ε(T): {2 * pf[0]:.1f} eV")
        ti = interpolate_T(tab, np.array([float(T)])); ph = [p for p in builder_from_table(ti, fit="spline", fits={name: "spline"})(float(T)) if p.name == name][0]
        xr = np.linspace(ph.x_min, ph.x_max, 201); gr = ph.g(xr); gr0 = float(ph.g(np.array([x0]))[0]); h = 0.004; c2 = float((ph.g(np.array([x0 + h]))[0] - 2 * gr0 + ph.g(np.array([x0 - h]))[0]) / h ** 2)
        ax.plot(xr, (gr - gr0 - slope * (xr - x0)) * 1000, color=c, lw=1.8, ls="--", label=f"{T} K small cells: {c2:.1f} eV")
        pts = ti.df[ti.df.phase == name].sort_values("x"); ax.plot(pts.x, (pts.G - gr0 - slope * (pts.x - x0)) * 1000, "o", color=c, ms=5, mfc="none")
        S[name][T] = {"d2G_dx2_static_eV": float(2 * pf0[0]), "tangent_slope_static_eV": float(pf0[1]), "d2G_dx2_point_defects_eV": float(2 * pf[0]), "d2G_dx2_range_phase_eV": c2, "tangent_slope_eV": float(slope),
                      "range_phase_minus_point_defects_meV": {f"{x:.4f}": float((gg - gr0 - (np.interp(x, xs, g) - g0)) * 1000) for x, gg in zip(pts.x, pts.G) if abs(x - x0) > 1e-6}}
    ax.axvline(x0, color="0.6", lw=0.6); ax.axvspan(x0 - 0.012, x0 + 0.012, color="0.93", zorder=0)
    ax.set(xlabel="x_Li", ylabel="G(x) − G(x$_0$) − (dG/dx)(x − x$_0$)   (meV/atom)", title=f"{pretty}, x$_0$ = {x0:.4f}   (solid: 1 defect in {max(int(q) for q in DF)} sites; dashed, circles: {nsm}-atom cells)"); ax.title.set_fontsize(9.5)
    lo, hi = ax.get_ylim(); ax.set_ylim(lo, hi + 0.42 * (hi - lo)); ax.legend(fontsize=7.5, title="d$^2$G/dx$^2$ at x$_0$", title_fontsize=8, loc="upper center", ncol=3)
fig.suptitle("ACE Al-Li compounds, G(x) around stoichiometry (tangent at x$_0$ removed; grey band = x$_0$ ± 0.012)\nthin solid: Wagner-Schottky with static defect energies;  thick solid: with defect free energies ε$_d$(T);  dashed + circles: small anti-site cells as a phase with a range", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "2_curvature_tip.png"), dpi=150); json.dump(S, open(os.path.join(OUT, "2_curvature_two_treatments.json"), "w"), indent=1)
for n, v in S.items():
    for T, r in v.items():
        print(n, T, "d2G static %.1f, eps(T) %.1f, small cells %.1f eV; slope %.3f -> %.3f" % (r["d2G_dx2_static_eV"], r["d2G_dx2_point_defects_eV"], r["d2G_dx2_range_phase_eV"], r["tangent_slope_static_eV"], r["tangent_slope_eV"]), {k: round(q, 1) for k, q in r["range_phase_minus_point_defects_meV"].items()})
