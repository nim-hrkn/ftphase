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

    def jump(a):
        dx = np.diff(a[:, 1]); i = int(np.argmax(np.abs(dx))); return a[i, 0], a[i + 1, 0], a[i, 1], a[i + 1, 1]

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
