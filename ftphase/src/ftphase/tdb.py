"""Write a CALPHAD database (TDB) from a free-energy table (stage 05 export).

The table (:class:`ftphase.records.FreeEnergyTable`, eV/atom, x = fraction of the second element) already holds what the
CALPHAD-type routes of the literature build their databases from, so those routes become settings of one export:

  solutions (fcc, bcc, liquid ...)   one sublattice (A,B): end-member functions fitted to the pure-element rows of that phase,
                                     Redlich-Kister excess L_k = a_k + b_k T fitted to the rows minus the analytic ideal mixing
  compounds
     kind 'stoichiometric'           (A)a(B)b with G = fitted function of T of the stoichiometric rows (two numbers dH - T dS
                                     with ``compound_terms=2``: the description of Zhang et al. 2027)
     kind 'cef'                      two sublattices (A,B)a(A,B)b fed by the anti-site free energies (and interaction
                                     coefficients) of a :class:`ftphase.compounds.CompoundModel`.  G(A:B) = g0.  The far
                                     end-members are the pure-element references plus a penalty (not the linear extrapolation
                                     of the dilute defect energy, which can undercut the real phases), and three interaction
                                     parameters per sublattice make the dilute limit exact: slope = site fraction x eps_d(T),
                                     quadratic term = w (x - x0)^2, then a quartic wall (the window of the hull route).  Near stoichiometry this is the Wagner-Schottky model with
                                     anti-sites only (no vacancies); it is the two-sublattice description of Saengdeejing et
                                     al. 2026 with the parameters taken from defect cells instead of Neumann-Kopp sums.
  reference                          the absolute free energies of the table (default) or anything the table was shifted to
                                     beforehand (e.g. SGTE with :func:`ftphase.assemble.reference_pure_elements`)

Every temperature function is  a + b T + c T ln T + d T^2  (``terms`` = 2, 3 or 4 leading coefficients), fitted by least
squares over ``T_fit``; the residuals are returned so that the loss against the table is visible.  Units in the file: J per mole
of atoms (solutions) / per mole of sites with the site ratios summing to 1 (compounds), 1 eV/atom = 96485.332 J/mol.
The file is plain TDB text and is checked by reading it back with pycalphad (tests, :func:`ftphase.assemble.check_with_pycalphad`).
"""

from __future__ import annotations

from typing import Dict, Mapping, Optional, Sequence, Tuple

import numpy as np

EV = 96485.33212   # J/mol per eV/atom
R = 8.314462618    # J/mol/K
_MASS = None


def fit_T(T, G, terms: int = 4) -> Tuple[np.ndarray, float]:
    """Least-squares coefficients (a, b, c, d) of G = a + b T + c T ln T + d T^2 (unused ones zero) and the rms residual."""
    T = np.asarray(T, dtype=float)
    G = np.asarray(G, dtype=float)
    cols = [np.ones_like(T), T, T * np.log(T), T ** 2][:terms]
    A = np.array(cols).T
    c, *_ = np.linalg.lstsq(A, G, rcond=None)
    out = np.zeros(4)
    out[:terms] = c
    return out, float(np.sqrt(np.mean((A @ c - G) ** 2)))


def _expr(c: Sequence[float]) -> str:
    """TDB expression of a + b T + c T ln T + d T^2 (J/mol)."""
    a, b, cc, d = (float(v) for v in c)
    s = f"{a:+.4f}"
    if b:
        s += f"{b:+.6f}*T"
    if cc:
        s += f"{cc:+.6f}*T*LN(T)"
    if d:
        s += f"{d:+.6e}*T**2"
    return s


def _mass(sym: str) -> float:
    from ase.data import atomic_masses, atomic_numbers

    return float(atomic_masses[atomic_numbers[sym.capitalize()]])


def _table_hull(df, T):
    """x -> lower convex hull (eV/atom) of all rows of the table at temperature T."""
    from .equilibrium import lower_hull_2d

    g = df[np.isclose(df["T"], T)]
    pts = g[["x", "G"]].to_numpy(dtype=float)
    idx = lower_hull_2d(pts)
    hx, hg = pts[idx, 0], pts[idx, 1]
    o = np.argsort(hx)
    return lambda xv: float(np.interp(xv, hx[o], hg[o]))


def _rows(df, phase, T_fit):
    g = df[(df.phase == phase) & (df["T"] >= T_fit[0]) & (df["T"] <= T_fit[1])]
    return g


def write_tdb(table, elements: Sequence[str], solutions: Mapping[str, str], compounds: Optional[Mapping[str, Mapping]] = None,
              T_fit: Tuple[float, float] = (300.0, 1000.0), terms: int = 4, rk_order=2, compound_terms: int = 4,
              models: Optional[Mapping] = None, path: Optional[str] = None, T_range: Tuple[float, float] = (1.0, 6000.0), comment: str = "",
              reference: Optional[Tuple[str, str]] = None, antisite_end_penalty: float = 500000.0, guard_margin_eV: float = 0.02, guard_weight: float = 1.0):
    """Return (tdb_text, report).  ``solutions`` maps table phase -> TDB phase name; ``compounds`` maps table phase ->
    {'name': TDB name, 'site_counts': (a, b), 'kind': 'stoichiometric' | 'cef'} (kind 'cef' needs ``models[phase]``, a
    :class:`ftphase.compounds.CompoundModel`).  The table rows of the solutions must be total free energies (config_entropy 'ideal'
    for lattice solutions, or a liquid from thermodynamic integration); rows of a compound are taken at its stoichiometric composition only.
    ``reference`` = (solution phase of pure A, solution phase of pure B), e.g. ('fcc', 'bcc'): the compounds are then written as
    formation quantities,  G = a' G_A^ref + b' G_B^ref + dH - T dS (+ ...)  with ``compound_terms`` coefficients fitted to the
    formation free energy (2 = the dH, dS pair of Zhang et al. 2027; the curvature of G(T) is carried by the references).
    Without it the compound function is fitted to its absolute G(T), which needs 3-4 terms.
    ``report`` = {'functions': {...}, 'solutions': {phase: {'rk': [(k, a, b)], 'rms_meV': ..}}, 'compounds': {...}}.
    """
    df = table.df
    A, B = (e.upper() for e in elements)
    lo, hi = T_range
    report: Dict = {"functions": {}, "solutions": {}, "compounds": {}, "T_fit": list(T_fit)}
    L = [f"$ Written by ftphase.tdb.write_tdb from a free-energy table ({comment or 'no comment'})",
         f"$ J/mol of atoms; functions a + b T + c T ln T + d T^2 fitted over {T_fit[0]:g}-{T_fit[1]:g} K; reference = the table's own",
         "ELEMENT /-   ELECTRON_GAS              0.0000E+00  0.0000E+00  0.0000E+00!",
         "ELEMENT VA   VACUUM                    0.0000E+00  0.0000E+00  0.0000E+00!",
         f"ELEMENT {A:<4s} REF_{A:<20s} {_mass(A):.4E}  0.0000E+00  0.0000E+00!",
         f"ELEMENT {B:<4s} REF_{B:<20s} {_mass(B):.4E}  0.0000E+00  0.0000E+00!", ""]
    funcs, body = [], ["TYPE_DEFINITION % SEQ *!", "DEFINE_SYSTEM_DEFAULT ELEMENT 2 !", "DEFAULT_COMMAND DEF_SYS_ELEMENT VA /- !", ""]

    def func(name, coef):
        funcs.append(f"FUNCTION {name} {lo:g} {_expr(coef)}; {hi:g} N !")
        return name

    ends_of, basis = {}, (lambda cc, Tv: cc[0] + cc[1] * Tv + cc[2] * Tv * np.log(Tv) + cc[3] * Tv ** 2)
    # ---- solutions
    for ph, tname in solutions.items():
        g = _rows(df, ph, T_fit)
        if g.empty:
            raise ValueError(f"no rows of phase {ph} in {T_fit}")
        if (g.config_entropy == "none").any():
            raise ValueError(f"solution {ph}: the rows must be total free energies (ideal-mixing term added, or a liquid from thermodynamic integration), not config_entropy 'none'")
        ends, missing = {}, []
        for el, xe in ((A, 0.0), (B, 1.0)):
            e = g[np.isclose(g.x, xe)]
            if len(e) < terms:
                missing.append(el)          # the phase was not computed (or is mechanically unstable) at this end: lattice stability fitted below
                continue
            c, rms = fit_T(e["T"], e["G"] * EV, terms)
            ends[el] = c
            report["functions"][f"G{tname[:5]}{el}"] = {"coef_J": c.tolist(), "rms_meV": rms / EV * 1000}
        mid = g[(g.x > 1e-9) & (g.x < 1 - 1e-9)]
        x = mid.x.to_numpy()
        T = mid["T"].to_numpy()
        need = [reference[0 if el == A else 1] for el in missing] if reference is not None else []
        if missing and (reference is None or any(ph_ not in ends_of or el not in ends_of[ph_][0] for ph_, el in zip(need, missing))):
            raise ValueError(f"solution {ph}: no pure-{missing} rows; give `reference` and list the reference phase of that element earlier in `solutions` so that the lattice stability can be set")
        refc = {el: ends_of[reference[0 if el == A else 1]][0][el] for el in missing}
        known = sum((wt * basis(ends[el], T) if el in ends else wt * basis(refc[el], T)) for el, wt in ((A, 1 - x), (B, x)))
        ideal = R * T * (x * np.log(x) + (1 - x) * np.log(1 - x))
        gex = mid["G"].to_numpy() * EV - known - ideal
        # A missing end (the phase was not computed there, or is mechanically unstable) cannot be fixed by alloy rows on one side:
        # a free fit makes the phase spuriously stable far from its data.  The unsampled range is therefore guarded: pseudo-rows
        # at  hull of the whole table + guard_margin  (the phase must stay above everything that is known there), fitted together
        # with the real rows; the end is  reference + (a + b T)  and the excess is limited to a sub-regular form.
        order = rk_order[ph] if isinstance(rk_order, dict) else rk_order
        wts = np.ones(len(x))
        if missing:
            order = min(order, 1)
            xg_lo, xg_hi = float(g.x.min()), float(g.x.max())
            px, pT, pG = [], [], []
            for Tk in np.unique(T):
                h = _table_hull(df, Tk)
                for xv in np.linspace(0.02, 0.98, 25):
                    if xv < xg_lo - 0.02 or xv > xg_hi + 0.02:
                        px.append(xv); pT.append(Tk); pG.append((h(xv) + guard_margin_eV) * EV)
            px, pT, pG = np.array(px), np.array(pT), np.array(pG)
            pknown = sum((wt * basis(ends[el], pT) if el in ends else wt * basis(refc[el], pT)) for el, wt in ((A, 1 - px), (B, px)))
            gex = np.concatenate([gex, pG - pknown - R * pT * (px * np.log(px) + (1 - px) * np.log(1 - px))])
            x, T = np.concatenate([x, px]), np.concatenate([T, pT])
            wts = np.concatenate([wts, np.full(len(px), float(guard_weight))])
        cols = [x * (1 - x) * (1 - 2 * x) ** k * f for k in range(order + 1) for f in (np.ones_like(T), T)]
        for el in missing:
            wt = (1 - x) if el == A else x
            cols += [wt, wt * T]
        M = np.array(cols).T
        coef, *_ = np.linalg.lstsq(M * wts[:, None], gex * wts, rcond=None)
        rk = [(k, float(coef[2 * k]), float(coef[2 * k + 1])) for k in range(order + 1)]
        for n_, el in enumerate(missing):
            dd = coef[2 * (order + 1) + 2 * n_: 2 * (order + 1) + 2 * n_ + 2]
            ends[el] = refc[el] + np.array([dd[0], dd[1], 0.0, 0.0])
            report["functions"][f"G{tname[:5]}{el}"] = {"coef_J": ends[el].tolist(), "lattice_stability_vs_reference_J": [float(dd[0]), float(dd[1])], "not_computed": True,
                                                        "guard": f"hull of the table + {guard_margin_eV * 1000:g} meV/atom outside x = {g.x.min():.3f}-{g.x.max():.3f}"}
        nreal = int(len(mid))
        resid = (M @ coef - gex)[:nreal]
        report["solutions"][ph] = {"tdb": tname, "rk_J": rk, "rms_meV": float(np.sqrt(np.mean(resid ** 2)) / EV * 1000), "n_rows": nreal, "x_range": [float(g.x.min()), float(g.x.max())],
                                   "ends_not_computed": missing, "rk_order": order}
        ends_of[ph] = (ends, f"G{tname[:5]}{A}", f"G{tname[:5]}{B}")
        fa, fb = func(f"G{tname[:5]}{A}", ends[A]), func(f"G{tname[:5]}{B}", ends[B])
        body += [f"PHASE {tname} %  1  1.0 !", f"CONSTITUENT {tname} :{A},{B} :  !",
                 f"PARAMETER G({tname},{A};0)  {lo:g} +{fa}; {hi:g} N !", f"PARAMETER G({tname},{B};0)  {lo:g} +{fb}; {hi:g} N !"]
        body += [f"PARAMETER L({tname},{A},{B};{k})  {lo:g} {a_:+.4f}{b_:+.6f}*T; {hi:g} N !" for k, a_, b_ in rk] + [""]

    # ---- compounds
    for ph, spec in (compounds or {}).items():
        tname = spec["name"]
        a, b = spec["site_counts"]
        fa_, fb_ = a / (a + b), b / (a + b)
        x0 = fb_
        g = _rows(df, ph, T_fit)
        g = g[np.isclose(g.x, x0, atol=1e-4)]
        if len(g) < compound_terms:
            raise ValueError(f"compound {ph}: fewer than {compound_terms} stoichiometric rows in {T_fit}")
        kind = spec.get("kind", "stoichiometric")
        Tg = g["T"].to_numpy()
        if reference is not None:
            (eA_, fA_, _), (eB_, _, fB_) = ends_of[reference[0]], ends_of[reference[1]]
            gref = fa_ * basis(eA_[A], Tg) + fb_ * basis(eB_[B], Tg)
            c0, rms = fit_T(Tg, g["G"].to_numpy() * EV - gref, compound_terms)
            funcs.append(f"FUNCTION G{tname[:7]} {lo:g} +{fa_:.8f}*{fA_}+{fb_:.8f}*{fB_}{_expr(c0)}; {hi:g} N !")
            f0 = f"G{tname[:7]}"
            report["compounds"][ph] = {"tdb": tname, "kind": kind, "x0": x0, "formation_coef_J": c0.tolist(), "dH_f_J": float(c0[0]), "dS_f_J_K": float(-c0[1]), "rms_meV": rms / EV * 1000,
                                       "reference": list(reference)}
        else:
            c0, rms = fit_T(Tg, g["G"].to_numpy() * EV, compound_terms)
            f0 = func(f"G{tname[:7]}", c0)
            report["compounds"][ph] = {"tdb": tname, "kind": kind, "x0": x0, "coef_J": c0.tolist(), "rms_meV": rms / EV * 1000}
        if kind == "stoichiometric":
            body += [f"PHASE {tname} %  2  {fa_:.6f}  {fb_:.6f} !", f"CONSTITUENT {tname} :{A} : {B} :  !",
                     f"PARAMETER G({tname},{A}:{B};0)  {lo:g} +{f0}; {hi:g} N !", ""]
            continue
        if kind != "cef":
            raise ValueError(f"compound kind {kind!r}")
        m = (models or {}).get(ph)
        if m is None:
            raise ValueError(f"compound {ph}: kind 'cef' needs a CompoundModel in models")
        if reference is None:
            raise ValueError("kind 'cef' needs `reference` (the far end-members are tied to the pure-element references)")
        Tm = np.asarray(m.T, dtype=float)
        sel = (Tm >= T_fit[0]) & (Tm <= T_fit[1])
        fitab = lambda v: fit_T(Tm[sel], np.asarray(v, dtype=float)[sel] * EV, 2)
        eA, rA = fitab(m.eps["A_on_B"])                 # anti-site free energies a + b T (J/mol per defect)
        eB, rB = fitab(m.eps["B_on_A"])
        wA = fitab(m.w["A_on_B"])[0] if "A_on_B" in getattr(m, "w", {}) else np.zeros(4)      # interaction coefficients (J/mol per x^2)
        wB = fitab(m.w["B_on_A"])[0] if "B_on_A" in getattr(m, "w", {}) else np.zeros(4)
        fA_ = ends_of[reference[0]][1]
        fB_ = ends_of[reference[1]][2]
        P = float(antisite_end_penalty)
        report["compounds"][ph].update({"eps_A_on_B_J": eA[:2].tolist(), "eps_B_on_A_J": eB[:2].tolist(), "eps_rms_meV": [rA / EV * 1000, rB / EV * 1000],
                                        "w_A_on_B_J": wA[:2].tolist(), "w_B_on_A_J": wB[:2].tolist(), "antisite_end_penalty_J": P})
        # Sublattice 2 (B sites, fraction fb_) with A anti-sites, y = y_A, u = 1 - 2y:
        #     G = g0 + y D + y (1 - y) [L0 + L1 u + L2 u^2],   D = G(A:A) - g0
        #       = g0 + (D + a0) y + (a1 - a0) y^2 + (a2 - a1) y^3 - a2 y^4,   a0 = L0 + L1 + L2, a1 = -2 L1 - 4 L2, a2 = 4 L2.
        # Required near stoichiometry: slope s = fb_ eps_d(T) (dilute defect free energy), y^2 coefficient q = w fb_^2 (0 for
        # non-interacting defects), no y^3 term.  Then  a0 = s - D, a1 = a2 = q + s - D,  L2 = a1 / 4, L1 = -a1, L0 = a0 + 0.75 a1,
        # and the energy is  g0 + s y + q y^2 + (D - s - q) y^4.  The far end-member A:A = pure-element reference + penalty is NOT
        # the linear extrapolation of the dilute energy (that undercuts the real phases); the quartic term is a wall set by the
        # penalty (default 500 kJ/mol: about 0.1 meV/atom at y = 0.07, 8 meV/atom at y = 0.2, 75 meV/atom at y = 0.35), the
        # counterpart of the window x0 +- half_width of the hull route (|x - x0| = site fraction x y).  With a soft wall (5 or
        # 50 kJ/mol, cubic) ACE Al4Li9 appeared far from its stoichiometry at 800 K.
        def lpar(n_s, e, w, fref):
            s_ = n_s * e[:2]                                  # s = n_s eps      (a, b of a + b T)
            q_ = n_s ** 2 * w[:2]                             # q = w n_s^2
            # a0 = s - D,  a1 = q + s - D,  with D = fref + P - f0 (functions): coefficients of fref, f0, constant, T
            def ex(cf, cst, lin):                             # cf * (fref - f0) + cst + lin T
                return f"{cf:+.6f}*{fref}{-cf:+.6f}*{f0}{cst:+.4f}{lin:+.6f}*T"
            l2 = ex(-0.25, 0.25 * (q_[0] + s_[0] - P), 0.25 * (q_[1] + s_[1]))                      # a1 / 4
            l1 = ex(1.0, -(q_[0] + s_[0] - P), -(q_[1] + s_[1]))                                    # -a1
            l0 = ex(-1.75, (s_[0] - P) + 0.75 * (q_[0] + s_[0] - P), s_[1] + 0.75 * (q_[1] + s_[1]))   # a0 + 0.75 a1
            return l0, l1, l2
        l0A, l1A, l2A = lpar(fb_, eA, wA, fA_)                # A anti-sites on the B sublattice (sublattice 2), far end A:A = G_A^ref + P
        l0B, l1B, l2B = lpar(fa_, eB, wB, fB_)                # B anti-sites on the A sublattice (sublattice 1), far end B:B = G_B^ref + P
        # odd-order Redlich-Kister terms multiply (y_first - y_second) of the constituents as written (alphabetical): the model uses (1 - 2 y_antisite)
        first = sorted([A, B])[0]
        sgn2 = 1.0 if first == B else -1.0                    # sublattice 2: host B;  (1 - 2 y_A) = y_B - y_A
        sgn1 = 1.0 if first == A else -1.0                    # sublattice 1: host A;  (1 - 2 y_B) = y_A - y_B
        neg = lambda e_: e_.replace("+", "#").replace("-", "+").replace("#", "-")
        c12 = ",".join(sorted([A, B]))
        body += [f"PHASE {tname} %  2  {fa_:.6f}  {fb_:.6f} !", f"CONSTITUENT {tname} :{A},{B} : {A},{B} :  !",
                 f"PARAMETER G({tname},{A}:{B};0)  {lo:g} +{f0}; {hi:g} N !",
                 f"PARAMETER G({tname},{A}:{A};0)  {lo:g} +{fA_}{P:+.4f}; {hi:g} N !",
                 f"PARAMETER G({tname},{B}:{B};0)  {lo:g} +{fB_}{P:+.4f}; {hi:g} N !",
                 f"PARAMETER G({tname},{B}:{A};0)  {lo:g} +{fA_}+{fB_}-{f0}{2 * P:+.4f}; {hi:g} N !",
                 f"PARAMETER L({tname},{A}:{c12};0)  {lo:g} {l0A}; {hi:g} N !",
                 f"PARAMETER L({tname},{A}:{c12};1)  {lo:g} {l1A if sgn2 > 0 else neg(l1A)}; {hi:g} N !",
                 f"PARAMETER L({tname},{A}:{c12};2)  {lo:g} {l2A}; {hi:g} N !",
                 f"PARAMETER L({tname},{c12}:{B};0)  {lo:g} {l0B}; {hi:g} N !",
                 f"PARAMETER L({tname},{c12}:{B};1)  {lo:g} {l1B if sgn1 > 0 else neg(l1B)}; {hi:g} N !",
                 f"PARAMETER L({tname},{c12}:{B};2)  {lo:g} {l2B}; {hi:g} N !", ""]
    text = "\n".join(L + funcs + [""] + body) + "\n"
    if path:
        with open(path, "w") as fh:
            fh.write(text)
    return text, report
