"""Stage 04A, route A of the CE+MC kind: cluster expansion (icet) fitted to MLIP energies and
semi-grand-canonical Monte Carlo (mchammer) on it.

Pieces
  enumerate_training_structures   icet enumeration of orderings on a primitive cell (sizes = atoms per cell)
  relaxed_energies                 MLIP energies per atom of the enumerated cells (positions + cell relaxed, the
                                   occupation stays on the lattice)
  fit_cluster_expansion            ClusterSpace + StructureContainer + trainstation CrossValidationEstimator
  sgc_scan                         SemiGrandCanonicalEnsemble sweep of the chemical-potential difference at fixed T:
                                   <x_B>(dmu) along an 'up' (from pure A) and a 'down' (from pure B) branch
  integrate_isotherm               dG/dx = dmu along each metastable branch -> G_alpha(x), G_beta(x), and the common
                                   tangent (solubility limits), the same construction as examples/agcu_sgcmc/sgcmc.py

Units: eV per atom; dmu = mu_B - mu_A in eV; x = fraction of B.  The configurational free energy obtained this way
contains the short-range order and the cluster interactions, i.e. everything the ideal-mixing + excess route (05 fit)
approximates; the vibrational part is NOT included (the CE is fitted to static energies), so combine it with the
vibrational term of the random cells the same way as in docs/obsolete_workflow.html eq. (E2) when a full G is needed.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

KB_EV = 8.617333262e-5


def enumerate_training_structures(primitive, chemical_symbols: Sequence[Sequence[str]], sizes: Iterable[int], concentration_restrictions: Optional[Dict] = None) -> List:
    """All symmetry-distinct orderings with ``sizes`` atoms per cell (icet enumerate_structures)."""
    from icet.tools import enumerate_structures  # type: ignore

    return list(enumerate_structures(primitive, list(sizes), [list(s) for s in chemical_symbols], concentration_restrictions=concentration_restrictions))


def relaxed_energies(structures: Sequence, calculator, fmax: float = 1e-3, cell: bool = True, steps: int = 500) -> np.ndarray:
    """Energy per atom of each structure after relaxing positions (and the cell shape/volume when ``cell``)."""
    from ase.filters import FrechetCellFilter
    from ase.optimize import BFGS

    out = []
    for s in structures:
        a = s.copy()
        a.calc = calculator
        if len(a) > 1 or cell:
            opt = BFGS(FrechetCellFilter(a) if cell else a, logfile=None)
            opt.run(fmax=fmax, steps=steps)
        out.append(a.get_potential_energy() / len(a))
    return np.asarray(out)


def fit_cluster_expansion(primitive, chemical_symbols, cutoffs: Sequence[float], structures: Sequence, energies_per_atom: Sequence[float],
                          fit_method: str = "ardr", n_splits: int = 10, seed: int = 42, **fit_kwargs):
    """Fit a ClusterExpansion to energies per atom.  Returns (ce, info) with info['rmse_train'],
    info['rmse_validation'] (eV/atom, k-fold CV), info['n_parameters'], info['n_structures']."""
    from icet import ClusterExpansion, ClusterSpace, StructureContainer  # type: ignore
    from trainstation import CrossValidationEstimator  # type: ignore

    cs = ClusterSpace(primitive, cutoffs=list(cutoffs), chemical_symbols=[list(s) for s in chemical_symbols])
    sc = StructureContainer(cs)
    for s, e in zip(structures, energies_per_atom):
        sc.add_structure(s, properties={"energy": float(e)})
    A, y = sc.get_fit_data(key="energy")
    cve = CrossValidationEstimator((A, y), fit_method=fit_method, n_splits=n_splits, seed=seed, **fit_kwargs)
    cve.validate()
    cve.train()
    ce = ClusterExpansion(cs, cve.parameters)
    info = {"rmse_train": float(cve.rmse_train), "rmse_validation": float(cve.rmse_validation), "n_parameters": int(cve.n_parameters),
            "n_nonzero_parameters": int(cve.n_nonzero_parameters), "n_structures": int(len(y)), "fit_method": fit_method, "cutoffs": list(cutoffs)}
    return ce, info


def sgc_scan(ce, supercell, temperature: float, dmus: Sequence[float], species: Tuple[str, str], n_sweeps_eq: int = 20, n_sweeps_av: int = 20,
             direction: str = "up", seed: int = 0, callback=None):
    """Semi-grand-canonical MC on the cluster expansion at one temperature.

    ``direction`` 'up': start from pure A (species[0]) and raise dmu = mu_B - mu_A in the given order;
    'down': start from pure B and lower it (pass dmus already reversed or let the function reverse them).
    Returns a list of dicts (T, dmu, x_B, E_per_atom, accepted fraction).  The structure is carried from one dmu to the
    next, so the metastable branches and their jumps come out like in a direct-potential SGC MC.
    """
    from mchammer.calculators import ClusterExpansionCalculator  # type: ignore
    from mchammer.ensembles import SemiGrandCanonicalEnsemble  # type: ignore

    A_, B_ = species
    s = supercell.copy()
    s.set_chemical_symbols([A_ if direction == "up" else B_] * len(s))
    order = list(dmus) if direction == "up" else list(sorted(dmus, reverse=True))
    calc = ClusterExpansionCalculator(s, ce)
    n = len(s)
    rows = []
    for k, dmu in enumerate(order):
        mc = SemiGrandCanonicalEnsemble(s, calculator=calc, temperature=float(temperature), chemical_potentials={A_: 0.0, B_: float(dmu)}, random_seed=seed + k,
                                        ensemble_data_write_interval=n)
        mc.run((n_sweeps_eq + n_sweeps_av) * n)
        data = mc.data_container.data
        data = data[data["mctrial"] > n_sweeps_eq * n]          # average over the production part only
        xcol = f"{B_}_count"
        x = float(data[xcol].mean()) / n if xcol in data else float(np.mean(np.array(s.get_chemical_symbols()) == B_))
        e = float(data["potential"].mean()) / n
        rows.append({"T": float(temperature), "dmu": float(dmu), "x_B": x, "E_per_atom": e, "acceptance": float(mc.acceptance_ratio) if hasattr(mc, "acceptance_ratio") else np.nan, "direction": direction})
        s = mc.structure
        if callback:
            callback(rows[-1])
    return rows


def integrate_isotherm(up: np.ndarray, down: np.ndarray, min_points: int = 3):
    """From the two SGC branches (arrays of columns dmu, x) build G_alpha(x) and G_beta(x) by dG/dx = dmu and return
    the common tangent.  Branch alpha = 'up' points before the jump (largest x step), beta = 'down' points above its
    jump.  G is relative to pure A; G(pure B) - G(pure A) follows from the Maxwell midpoint of the hysteresis loop.
    Returns dict with x_alpha, x_beta (tangent), dmu_star, jumps and the branch curves (xa, ga, xb, gb)."""
    from .equilibrium import PhaseCurve, equilibrium_at_T

    up = np.asarray(up, dtype=float); down = np.asarray(down, dtype=float)
    up = up[np.argsort(up[:, 0])]; down = down[np.argsort(down[:, 0])]

    def jump(a, frac=0.25):
        """(dmu_before, dmu_after, x_before, x_after) of the transition; consecutive steps larger than ``frac`` of the
        largest one are part of the same jump (a point in the middle of the transition is a two-phase state of the
        finite cell, not a branch point)."""
        dx = np.abs(np.diff(a[:, 1])); i = j = int(np.argmax(dx)); big = frac * dx[i]
        while i > 0 and dx[i - 1] > big:
            i -= 1
        while j < len(dx) - 1 and dx[j + 1] > big:
            j += 1
        return a[i, 0], a[j + 1, 0], a[i, 1], a[j + 1, 1]

    ju, jd = jump(up), jump(down)
    alpha = up[up[:, 0] <= ju[0] + 1e-9]
    beta = down[down[:, 0] >= jd[1] - 1e-9]

    def integrate(a):
        x = a[:, 1]; dmu = a[:, 0]
        order = np.argsort(x); x = x[order]; dmu = dmu[order]
        xu, idx = np.unique(np.round(x, 6), return_inverse=True)
        du = np.array([dmu[idx == k].mean() for k in range(len(xu))])
        g = np.concatenate([[0.0], np.cumsum(0.5 * (du[1:] + du[:-1]) * np.diff(xu))])
        return xu, g

    xa, ga = integrate(alpha); xb, gb = integrate(beta)
    if len(xa) < min_points or len(xb) < min_points:
        return {"x_alpha": np.nan, "x_beta": np.nan, "dmu_star": np.nan, "jump_up": ju, "jump_down": jd, "xa": xa, "ga": ga, "xb": xb, "gb": gb}
    dmu_star = 0.5 * (ju[0] + jd[1])
    xa_lim = np.interp(dmu_star, up[:, 0], up[:, 1]); xb_lim = np.interp(dmu_star, down[:, 0], down[:, 1])
    dG = np.interp(xa_lim, xa, ga) + dmu_star * (xb_lim - xa_lim) - (np.interp(xb_lim, xb, gb) - gb[-1])
    G_alpha = ga; G_beta = (gb - gb[-1]) + dG
    pa = PhaseCurve.from_points("alpha", xa, G_alpha, fit="spline", limited=True)
    pb = PhaseCurve.from_points("beta", xb, G_beta, fit="spline", limited=True)
    eq = equilibrium_at_T([pa, pb], np.nan, min_width=0.005)
    seg = [c for c in eq.coexistence if c.phase_a != c.phase_b]
    xal, xbe = (float(seg[0].x_a), float(seg[0].x_b)) if seg else (np.nan, np.nan)
    return {"x_alpha": xal, "x_beta": xbe, "dmu_star": float(dmu_star), "dG_B_minus_A": float(dG), "jump_up": ju, "jump_down": jd, "xa": xa, "ga": G_alpha, "xb": xb, "gb": G_beta}


def vcsgc_scan(ce, supercell, temperature: float, phis: Sequence[float], species: Tuple[str, str], kappa: float = 200.0, n_sweeps_eq: int = 20,
               n_sweeps_av: int = 20, seed: int = 0, start: str = "random"):
    """Variance-constrained SGC MC (Sadigh & Erhart 2012) on the cluster expansion at one temperature.

    ``phis`` are the constraint parameters for species B (x_B ~ -phi/2; -2.1 .. 0.1 covers 0 <= x_B <= 1).  Unlike the
    SGC ensemble, one phi gives one <x_B> also inside a miscibility gap, and the canonical free-energy derivative is
    dF/dx_B = -k_B T kappa (phi + 2 <x_B>) per atom, so F(x) can be integrated across the gap and the solubility
    limits follow from the common tangent (``solvus_from_vcsgc``).  Each phi is an independent run started from a
    random structure at x_B = -phi/2 (``start='random'``), so the points can be run in parallel.
    Returns a list of dicts (T, phi, x_B, dF_dx, E_per_atom)."""
    from mchammer.calculators import ClusterExpansionCalculator  # type: ignore
    from mchammer.ensembles import VCSGCEnsemble  # type: ignore

    A_, B_ = species
    n = len(supercell)
    rng = np.random.default_rng(seed)
    rows = []
    s_prev = None
    for k, phi in enumerate(phis):
        s = supercell.copy()
        if start == "random" or s_prev is None:
            nB = int(round(min(max(-phi / 2.0, 0.0), 1.0) * n))
            syms = np.array([A_] * n, dtype=object); syms[rng.choice(n, nB, replace=False)] = B_
            s.set_chemical_symbols(list(syms))
        else:
            s = s_prev
        calc = ClusterExpansionCalculator(s, ce)
        mc = VCSGCEnsemble(s, calculator=calc, temperature=float(temperature), phis={B_: float(phi)}, kappa=float(kappa), random_seed=seed + k,
                           ensemble_data_write_interval=n)
        mc.run((n_sweeps_eq + n_sweeps_av) * n)
        data = mc.data_container.data
        data = data[data["mctrial"] > n_sweeps_eq * n]
        x = float(data[f"{B_}_count"].mean()) / n
        dfdx = -KB_EV * float(temperature) * float(kappa) * (float(phi) + 2.0 * x)
        rows.append({"T": float(temperature), "phi": float(phi), "x_B": x, "dF_dx": dfdx, "E_per_atom": float(data["potential"].mean()) / n})
        s_prev = mc.structure
    return rows


def lower_hull_gap(x: np.ndarray, F: np.ndarray, min_width: float = 0.02):
    """Lower convex hull of the points (x, F); returns the widest hull segment that skips interior points as
    (x_left, x_right), or (nan, nan) when every segment is narrower than ``min_width`` (no miscibility gap)."""
    order = np.argsort(x); x = np.asarray(x, float)[order]; F = np.asarray(F, float)[order]
    hull = []                                                              # indices of the lower hull vertices
    for i in range(len(x)):
        while len(hull) >= 2:
            a, b = hull[-2], hull[-1]
            if (x[b] - x[a]) * (F[i] - F[a]) - (F[b] - F[a]) * (x[i] - x[a]) <= 0:   # middle point on or above the chord: drop it
                hull.pop()
            else:
                break
        hull.append(i)
    best = (np.nan, np.nan); w = min_width
    for a, b in zip(hull[:-1], hull[1:]):
        if b > a + 1 and x[b] - x[a] > w:                                   # a real gap skips at least one sampled point
            best, w = (float(x[a]), float(x[b])), x[b] - x[a]
    return best


def solvus_from_vcsgc(rows, n_dilute: int = 4, baseline: Tuple[float, float] = (0.05, 0.15), flat: float = 0.5, min_width: float = 0.05, x_eps: float = 5e-4):
    """Solubility limits from VCSGC points by extrapolating the dilute branches onto the two-phase level.

    Single-phase dilute branch: dF/dx = c + k_B T ln(x/(1-x)) with c constant (impurity energy); its c is measured as
    the mean of dF/dx - k_B T ln(x/(1-x)) over the ``n_dilute`` points nearest each pure element.  Two-phase region (a
    finite cell at fixed phi phase-separates): dF/dx is the nearly flat common-tangent slope, measured as the median of
    dF/dx over ``baseline`` = (x_lo, x_hi) on the A side and (1 - x_hi, 1 - x_lo) on the B side (these windows must lie
    inside the gap).  The solvus is where the branch reaches that level: x/(1-x) = exp((level - c)/k_B T).  Gap test:
    the rise of dF/dx across the baseline window must be below ``flat`` times the ideal single-phase rise
    k_B T ln(x_hi(1-x_lo)/(x_lo(1-x_hi))); otherwise (convex F) NaN.  The finite-cell two-phase level is not unique
    (interfaces tilt it by ~0.1 eV across the gap), which is why the level next to each solvus is used; dmu* is the
    median of dF/dx over the whole gap.  Saturated points (<x> within x_eps of 0 or 1) are dropped.
    Returns dict(x_alpha, x_beta, dmu_star, c_A, c_B, x, F, dF_dx) with F integrated from pure A."""
    T = float(np.median([r["T"] for r in rows])); kT = KB_EV * T
    a = np.array([[r["x_B"], r["dF_dx"]] for r in rows], float)
    a = a[(a[:, 0] > x_eps) & (a[:, 0] < 1 - x_eps)]
    a = a[np.argsort(a[:, 0])]
    xu, idx = np.unique(np.round(a[:, 0], 6), return_inverse=True)
    du = np.array([a[idx == k, 1].mean() for k in range(len(xu))])
    F = np.concatenate([[0.0], np.cumsum(0.5 * (du[1:] + du[:-1]) * np.diff(xu))])
    out = {"x_alpha": np.nan, "x_beta": np.nan, "dmu_star": np.nan, "c_A": np.nan, "c_B": np.nan, "x": xu, "F": F, "dF_dx": du}
    cc = du - kT * np.log(xu / (1 - xu))
    lo, hi = baseline
    ideal_rise = kT * np.log(hi * (1 - lo) / (lo * (1 - hi)))

    def side(sel_dil, sel_base, sign):
        if sel_dil.sum() < 2 or sel_base.sum() < 2:
            return np.nan, np.nan
        c = float(np.mean(cc[sel_dil]))
        xb, db = xu[sel_base], du[sel_base]
        rise = float(np.polyfit(xb, db, 1)[0] * (xb.max() - xb.min()))
        if rise > flat * ideal_rise:
            return np.nan, c
        level = float(np.median(db))
        q = np.exp((level - c) / kT)
        return float(q / (1 + q)), c

    nA = min(n_dilute, len(xu)); nB = min(n_dilute, len(xu))
    selA = np.zeros(len(xu), bool); selA[:nA] = True
    selB = np.zeros(len(xu), bool); selB[len(xu) - nB:] = True
    xa, cA = side(selA, (xu >= lo) & (xu <= hi), +1)
    xb, cB = side(selB, (xu >= 1 - hi) & (xu <= 1 - lo), -1)
    out["c_A"], out["c_B"] = cA, cB
    if np.isfinite(xa) and np.isfinite(xb) and xb - xa < min_width:
        xa = xb = np.nan
    out["x_alpha"], out["x_beta"] = xa, xb
    if np.isfinite(xa) and np.isfinite(xb):
        mid = (xu > xa) & (xu < xb)
        out["dmu_star"] = float(np.median(du[mid])) if mid.any() else np.nan
    return out


def dilute_solvus(ce, supercell, species: Tuple[str, str], temperature: float, dmu_star: float):
    """Ideal dilute-solution estimate of the solubility limits from the CE impurity energies: on the A-rich side
    E_imp(B in A) + k_B T ln x = dmu*_mix, on the B-rich side -E_imp(A in B) - k_B T ln(1 - x) = dmu*_mix, with
    dmu*_mix = dmu* - (e_B - e_A) (the VCSGC/SGC dmu* refers to absolute CE energies).  Returns
    dict(x_alpha, x_beta, E_imp_B_in_A, E_imp_A_in_B, e_A, e_B)."""
    A_, B_ = species
    n = len(supercell)
    def e_of(syms):
        s = supercell.copy(); s.set_chemical_symbols(syms); return float(ce.predict(s))
    eA = e_of([A_] * n); eB = e_of([B_] * n)
    eBA = e_of([B_] + [A_] * (n - 1)) * n - (n - 1) * eA - eB       # B impurity in A, relative to the pure elements
    eAB = e_of([A_] + [B_] * (n - 1)) * n - (n - 1) * eB - eA
    kT = KB_EV * temperature; mu = dmu_star - (eB - eA)
    xa = float(np.exp((mu - eBA) / kT)); xb = float(1.0 - np.exp((-mu - eAB) / kT))
    return {"x_alpha": min(xa, 1.0), "x_beta": max(xb, 0.0), "E_imp_B_in_A": eBA, "E_imp_A_in_B": eAB, "e_A": eA, "e_B": eB, "dmu_star_mix": mu}
