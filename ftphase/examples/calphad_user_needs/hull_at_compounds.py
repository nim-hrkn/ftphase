"""Figure 18c: which part of each compound's G(x) is stable?  For every ACE Al-Li compound, G(x) from the defect model (defect free
energies eps_d(T) + interaction) together with the equilibrium line = lower convex hull of ALL phases (fcc, bcc, liquid where it is in
the table, and the four compounds).  The tangent of the compound's own curve at stoichiometry is removed from both, so the vertical
axis is the height above that tangent.  The compound is stable exactly where its curve lies on the hull; where the hull runs straight
below the curve, the alloy is a two-phase mixture with a neighbouring phase.  'Lowest phase' is not the criterion: the hull is.
    ./env/ftphase/bin/python ftphase/examples/calphad_user_needs/hull_at_compounds.py   -> out/11_hull_at_compounds.png / .json
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); sys.path.insert(0, HERE)
sys.argv = [sys.argv[0], "extended"]


def main():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from ftphase.equilibrium import lower_hull
    import uniform_diagram as ud
    builder, models, df, old = ud.setup(half=0.12); PRETTY = {"Al3Li": "Al$_3$Li", "B32": "B32 AlLi", "Al2Li3": "Al$_2$Li$_3$", "Al4Li9": "Al$_4$Li$_9$"}; TS = (300.0, 500.0, 700.0)
    import pandas as pd
    from ftphase.records import FreeEnergyTable
    from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table
    from ftphase.aiida.functions import _site_model

    def small_cell_phases(T):
        """The same compounds computed the other way: small cells with one anti-site on each side (3 compositions), QHA free energy +
        sublattice configurational entropy, spline.  B32: the 16-atom cells of example 6; the others: range_phase_compounds.py."""
        out = {}
        for name, m in models.items():
            if name == "B32":
                tb = FreeEnergyTable.from_dataframe(old.df[old.df.phase == "B32"].copy(), old.meta)
            else:
                tb = add_configurational_term(FreeEnergyTable.from_rows(pd.read_csv(os.path.join(OUT, f"6_range_{name}.tsv"), sep="\t").to_dict("records"), {}), name, "sublattice", site_model=_site_model("b32_antisite", m.x0))
            ti = interpolate_T(tb, np.array([T])); out[name] = ([q for q in builder_from_table(ti, fit="spline", fits={name: "spline"})(T) if q.name == name][0], ti.df[ti.df.phase == name].sort_values("x"))
        return out

    fig, axes = plt.subplots(len(TS), 4, figsize=(18, 4.6 * len(TS))); S = {}; frames = {}
    for r, T in enumerate(TS):
        ph = builder(T); pts, labs, idx = lower_hull(ph); o = np.argsort(pts[idx, 0]); hx, hg = pts[idx, 0][o], pts[idx, 1][o]; hl = np.array(labs)[idx][o]; S[int(T)] = {}
        sm = small_cell_phases(T); ph2 = [q for q in ph if q.name not in models] + [v[0] for v in sm.values()]       # second hull: the compounds from the small cells
        pts2, labs2, idx2 = lower_hull(ph2); o2 = np.argsort(pts2[idx2, 0]); hx2, hg2 = pts2[idx2, 0][o2], pts2[idx2, 1][o2]; hl2 = np.array(labs2)[idx2][o2]
        fitted = {}; mcph = {}; pend = []
        for c, (name, m) in enumerate(models.items()):
            ax = axes[r, c]; p = [q for q in ph if q.name == name][0]; xs, g = p.sample(); h = 2e-3
            g0 = float(p.g(np.array([m.x0]))[0]); slope = float((p.g(np.array([m.x0 + h]))[0] - p.g(np.array([m.x0 - h]))[0]) / (2 * h)); f = lambda x, y: (y - g0 - slope * (x - m.x0)) * 1000
            w = 0.09; sel = (xs > m.x0 - w) & (xs < m.x0 + w); ax.plot(xs[sel], f(xs[sel], g[sel]), color="#1f77b4", lw=1.6, label="G(x) from the defect model (point defects + interaction)")
            # The same G(x) from directly computed cells (no model in between): every cell with anti-sites that was computed, i.e. the small
            # cells with one anti-site (open circles) and the large cells with 2-20 anti-sites (dots = mean over 3 random configurations, bar =
            # their spread).  G of a cell = its QHA free energy per atom - T x (ideal configurational entropy of its anti-sites on the sublattice).
            # If calculation A is right, these points lie on the blue curve: at each composition there is only one G of the phase.
            from ftphase.configurational import sublattice_entropy, b32_antisite_site_fractions
            scf = lambda x: sublattice_entropy(*b32_antisite_site_fractions(float(x), stoich_x=m.x0), basis="atom")
            tp = df[(df.phase == name) & np.isclose(df.x, m.x0, atol=1e-3)].sort_values("T"); gperf = float(np.interp(T, tp["T"], tp["G"]))      # PERFECT compound (table), not the model value at x0 (which thermal defects lower)
            q, cells = sm[name]; off = gperf - float(cells.G.to_numpy()[np.argmin(np.abs(cells.x.to_numpy() - m.x0))])        # small cells: their perfect cell aligned with the table cell (they differ by the phonon supercell)
            cx = cells.x.to_numpy(); cg = cells.G.to_numpy() + off; ax.plot(cx, f(cx, cg), "o", color="#ff7f0e", ms=6, mfc="none", mew=1.5, label="computed: small cells, 1 anti-site")
            by = {}; gone = []; fce = os.path.join(HERE, "..", "uniform_compounds", "out", "alli_ace", f"ce_{name}", "cells.json")
            if os.path.exists(fce) and any("left_parent" in v for v in json.load(open(fce))["cells"].values()):
                # cells of the cluster-expansion training set (their structures were checked): only one kind of anti-site, no imaginary mode;
                # cells that left the parent structure on relaxation (shape strain > 2 %) are another phase: drawn as grey crosses, not used
                rc = json.load(open(fce)); Tc = np.array(rc["T"]); Nc = rc["n_sites"]; gpc = np.interp(T, Tc, rc["cells"]["perfect"]["G_T_eV"])
                for tg, cc in rc["cells"].items():
                    if "G_T_eV" not in cc or cc.get("n_imag", 0) > 0 or (cc["n_B_on_A"] > 0 and cc["n_A_on_B"] > 0) or tg == "perfect" or abs(cc["x"] - m.x0) >= w:
                        continue
                    val = gperf + (float(np.interp(T, Tc, cc["G_T_eV"])) - gpc) / Nc - T * scf(cc["x"])
                    (gone if cc.get("left_parent") else by.setdefault(round(cc["x"], 5), [])).append((cc["x"], val) if cc.get("left_parent") else val)
            else:
                r9 = json.load(open(os.path.join(OUT, f"9_interaction_{name}.json"))); N9 = r9["n_sites"]; T9 = np.array(r9["T"])
                for cc in r9["cells"].values():
                    if "dG_T_eV" in cc and cc.get("n_imag", 0) == 0 and abs(cc["x"] - m.x0) < w:
                        by.setdefault(round(cc["x"], 5), []).append(gperf + float(np.interp(T, T9, cc["dG_T_eV"])) / N9 - T * scf(cc["x"]))
            if gone:
                gx_ = np.array([v[0] for v in gone]); gy_ = np.array([v[1] for v in gone]); ax.plot(gx_, f(gx_, gy_), "x", color="0.55", ms=6, label="cells that left the parent structure (not this phase)")
                S[int(T)][name + "_left_parent_x"] = [round(float(gx_.min()), 4), round(float(gx_.max()), 4)]
            mx = np.array(sorted(by)); mg = np.array([np.mean(by[x]) for x in mx]); me = np.array([np.std(by[x]) for x in mx])
            if len(mx):
                ax.errorbar(mx, f(mx, mg), yerr=me * 1000, fmt=".", color="#ff7f0e", ms=7, elinewidth=1.0, capsize=2, label="computed: large cells, 2–20 anti-sites")
            allx = np.concatenate([cx[np.abs(cx - m.x0) > 1e-6], mx]); allg = np.concatenate([cg[np.abs(cx - m.x0) > 1e-6], mg]); res = (allg - p.g(allx)) * 1000
            # Interpolation of the computed points WITHOUT a spline: the value at x0 is fixed to the perfect compound, the analytic configurational
            # entropy of the anti-sites (which makes the V at x0) is kept exact, and only the energy part is fitted, one polynomial per side through zero:
            #     G(x) = g_perfect + [a d + b d^2 + c d^3] - T S_conf(x),   d = x - x0   (c only with >= 4 points on that side)
            fitc = {}
            for side, sel_ in (("A_rich", allx < m.x0), ("B_rich", allx > m.x0)):
                dx = allx[sel_] - m.x0; e_ = allg[sel_] + T * np.array([scf(v) for v in allx[sel_]]) - gperf
                if len(dx) >= 1:
                    # the slope at x0 is not fitted either: it is the free energy of ONE isolated anti-site (eps_d(T) of the largest cell); only the
                    # quadratic and cubic terms (the interaction) are fitted.  A free linear term let the cubic dip below zero next to x0.
                    a1 = (-m.energies(T)["A_on_B"] if side == "A_rich" else m.energies(T)["B_on_A"])           # d e / d(delta): one anti-site per site changes x by -1 (A on B) or +1 (B on A)
                    nun = len(np.unique(np.round(dx, 5))); order = 3 if nun >= 4 else (2 if nun >= 2 else 1)
                    if order >= 2:
                        Af = np.array([dx ** n_ for n_ in range(2, order + 1)]).T; cf2, *_ = np.linalg.lstsq(Af, e_ - a1 * dx, rcond=None); cf = np.concatenate([[a1], cf2])
                    else:
                        cf = np.array([a1])
                    pred = sum(cf[n_] * dx ** (n_ + 1) for n_ in range(len(cf))); fitc[side] = (cf, float(np.abs(dx).max()), float(np.sqrt(np.mean((pred - e_) ** 2)) * 1000))
            def gfit(xv):
                xv = np.asarray(xv, dtype=float); d_ = xv - m.x0; out_ = np.full(len(xv), gperf)
                for side, sgn in (("A_rich", -1), ("B_rich", 1)):
                    if side in fitc:
                        mk = (d_ * sgn > 0); cf = fitc[side][0]; out_[mk] += sum(cf[n_] * d_[mk] ** (n_ + 1) for n_ in range(len(cf)))
                return out_ - T * np.array([scf(v) for v in xv])
            xl = m.x0 - (fitc["A_rich"][1] if "A_rich" in fitc else 0.0); xh = m.x0 + (fitc["B_rich"][1] if "B_rich" in fitc else 0.0); xf_ = np.unique(np.concatenate([np.linspace(xl, xh, 241), [m.x0]]))
            ax.plot(xf_, f(xf_, gfit(xf_)), color="#ff7f0e", lw=1.4, ls="--", label="fit to the computed cells (value and slope at x$_0$ fixed, entropy analytic)")
            S[int(T)][name + "_fit_rms_meV"] = {k_: round(v_[2], 2) for k_, v_ in fitc.items()}
            from ftphase.equilibrium import PhaseCurve
            fitted[name] = PhaseCurve.from_points(name, xf_, gfit(xf_), fit="spline", limited=True, n_sample=801)
            S[int(T)][name + "_cells_minus_A_meV"] = {"rms": round(float(np.sqrt(np.mean(res ** 2))), 2), "max_abs": round(float(np.abs(res).max()), 2), "n": int(len(res)), "small_cell_stoichiometric_offset_meV": round(-off * 1000, 2), "thermal_defect_lowering_at_x0_meV": round((g0 - gperf) * 1000, 2)}
            xd = np.linspace(m.x0 - w, m.x0 + w, 500); hd = np.interp(xd, hx, hg); ax.plot(xd, f(xd, hd), color="k", lw=1.0, ls="--", label="equilibrium: lower convex hull of all phases")
            on = (hl == name)
            if on.any():
                xo = hx[on]; ax.plot(xo, f(xo, hg[on]), color="#d62728", lw=4.0, alpha=0.75, solid_capstyle="butt", label=f"stable (on the hull): x = {xo.min():.3f}–{xo.max():.3f}")
                S[int(T)][name] = [round(float(xo.min()), 4), round(float(xo.max()), 4)]; lo_x, hi_x = xo.min(), xo.max()
            else:
                gap = float(np.interp(m.x0, hx, hg)); ax.text(0.5, 0.42, f"not stable at {T:.0f} K:\nthe hull is {1000 * (g0 - gap):.1f} meV/atom below\nthe stoichiometric compound", transform=ax.transAxes, ha="center", va="center", fontsize=9, color="#d62728"); S[int(T)][name] = None; lo_x = hi_x = m.x0
            left = [(x, l) for x, l in zip(hx, hl) if x < lo_x - 1e-9 and l != name]; right = [(x, l) for x, l in zip(hx, hl) if x > hi_x + 1e-9 and l != name]
            if left:
                ax.text(0.02, 0.04, f"← two-phase with {left[-1][1]} (x = {left[-1][0]:.3f})", transform=ax.transAxes, fontsize=7.5, color="0.2", ha="left")
            if right:
                ax.text(0.98, 0.04, f"two-phase with {right[0][1]} (x = {right[0][0]:.3f}) →", transform=ax.transAxes, fontsize=7.5, color="0.2", ha="right")
            ax.axvline(m.x0, color="0.7", lw=0.6); ax.set_xlim(m.x0 - w, m.x0 + w); lo = min(float(f(xd, hd).min()), -1.0); ax.set_ylim(lo * 1.35 - 1, max(13.0, -lo * 1.5))
            fmc = os.path.join(HERE, "..", "uniform_compounds", "out", "alli_ace", f"ce_{name}", f"G_{int(T)}.tsv")
            if os.path.exists(fmc) and json.load(open(os.path.join(os.path.dirname(fmc), "fit.json")))[str(int(T))]["rmse_cv_meV"] < 1.0:         # (an expansion with a cross-validation error above 1 meV/atom is not used)  # cluster expansion of the defect configurations + semi-grand-canonical MC: G(x) - G(x0) = integral of (mu_B - mu_A) dx
                gm = pd.read_csv(fmc, sep="\t"); fit_ = json.load(open(os.path.join(os.path.dirname(fmc), "fit.json"))); keep = []
                for br, q_ in gm.groupby("branch"):
                    q_ = q_.sort_values("dmu", ascending=(br == "B_rich")).reset_index(drop=True); stop = len(q_)        # in the order of the scan, away from the stoichiometric plateau
                    for n_ in range(1, len(q_)):          # the branch of the compound ends where the composition jumps (another state) or leaves the training range
                        if abs(q_.x[n_] - q_.x[n_ - 1]) > 0.02 or q_.x[n_] < fit_["x_range_of_training"][0] or q_.x[n_] > fit_["x_range_of_training"][1]:
                            stop = n_; break
                    q_ = q_.iloc[:stop].copy(); q_ = q_[q_.antisite_fraction.cummax() < 0.25]        # beyond a quarter of the sites exchanged the state is no longer the ordered compound
                    if len(q_):       # a branch that starts slightly off x0 (thermal anti-sites at high T) is anchored by its first chemical potential: G(x1) - G(x0) = dmu * (x1 - x0)
                        q_["G_minus_Gx0"] = q_.G_minus_Gx0 - q_.G_minus_Gx0.iloc[0] + q_.dmu.iloc[0] * (q_.x.iloc[0] - m.x0)
                    keep.append(q_)
                gm = pd.concat(keep).sort_values("x").drop_duplicates("x")
            if os.path.exists(fmc) and json.load(open(os.path.join(os.path.dirname(fmc), "fit.json")))[str(int(T))]["rmse_cv_meV"] < 1.0 and len(gm) >= 4 and gm.x.max() - gm.x.min() >= 0.02:      # a branch that leaves the ordered compound at once (the expansion puts a far-away state lower) gives no curve: the model line is kept
                xm = gm.x.to_numpy(); ym = g0 + gm.G_minus_Gx0.to_numpy()
                ax.plot(xm, f(xm, ym), color="#2ca02c", lw=1.8, label="cluster expansion of the defects + Monte Carlo")
                mcph[name] = PhaseCurve.from_points(name, xm, ym, fit="spline", limited=True, n_sample=801)
                S[int(T)][name + "_MC_minus_model_meV"] = {f"{xq:.3f}": round(float((np.interp(xq, xm, ym) - p.g(np.array([xq]))[0]) * 1000), 2) for xq in (0.49, 0.51, 0.52, 0.54, 0.56, 0.58, 0.60) if xm.min() <= xq <= xm.max()}; S[int(T)][name + "_MC_range"] = [round(float(xm.min()), 4), round(float(xm.max()), 4)]
            ax.set_title(f"{PRETTY[name]}, {T:.0f} K", fontsize=10); frames[(r, c)] = (ax, name, (lambda x, y, g0=g0, slope=slope, x0=m.x0: (y - g0 - slope * (x - x0)) * 1000)); ax.legend(fontsize=6.6, loc="upper center")
            if r == len(TS) - 1: ax.set_xlabel("x_Li")
            if c == 0: ax.set_ylabel("G − tangent of the compound at x$_0$   (meV/atom)")
        ph3 = [q for q in ph if q.name not in models] + list(fitted.values()); pts3, labs3, idx3 = lower_hull(ph3); o3 = np.argsort(pts3[idx3, 0]); hx3, hg3, hl3 = pts3[idx3, 0][o3], pts3[idx3, 1][o3], np.array(labs3)[idx3][o3]
        for (rr, c), (ax, name, f) in list(frames.items()):
            if rr != r:
                continue
            on3 = hl3 == name; S[int(T)][name + "_stable_by_fit"] = [round(float(hx3[on3].min()), 4), round(float(hx3[on3].max()), 4)] if on3.any() else None
            if on3.any():
                ax.plot(hx3[on3], f(hx3[on3], hg3[on3]), color="#ff7f0e", lw=7.0, alpha=0.3, solid_capstyle="butt", label=f"stable by the fit: x = {hx3[on3].min():.3f}–{hx3[on3].max():.3f}")
            pend.append((ax, name, f))
        # Monte Carlo: the hull is taken again with EVERY compound that has a Monte Carlo curve replaced at once (neighbours compared at the same level)
        ph4 = [q for q in ph if q.name not in mcph] + list(mcph.values())
        if mcph:
            pts4, labs4, idx4 = lower_hull(ph4); o4 = np.argsort(pts4[idx4, 0]); hx4, hg4, hl4 = pts4[idx4, 0][o4], pts4[idx4, 1][o4], np.array(labs4)[idx4][o4]
        for ax, name, f in pend:
            if name in mcph:
                on4 = hl4 == name; S[int(T)][name + "_stable_by_MC"] = [round(float(hx4[on4].min()), 4), round(float(hx4[on4].max()), 4)] if on4.any() else None
                if on4.any():
                    ax.plot(hx4[on4], f(hx4[on4], hg4[on4]), color="#2ca02c", lw=9.0, alpha=0.25, solid_capstyle="butt", label=f"stable by Monte Carlo: x = {hx4[on4].min():.3f}–{hx4[on4].max():.3f}")
            ax.legend(fontsize=6.0, loc="upper center")
    fig.suptitle("ACE Al-Li: G(x) of each compound from the defect model (blue) and from the cells that were computed directly (orange points), with the equilibrium line (lower convex hull of all phases, dashed).\n"
                 "At each composition the phase has one G: the points lie on the curve. The compound is stable where the curve lies on the hull (red).", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "11_hull_at_compounds.png"), dpi=130); json.dump(S, open(os.path.join(OUT, "11_hull_at_compounds.json"), "w"), indent=1); print(json.dumps(S))


if __name__ == "__main__":
    main()
