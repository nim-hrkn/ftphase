"""Ordered compounds without prior knowledge of their kind (line compound or phase with a composition range).

Every compound A_a B_b gets the same description and its width is read from the lower hull afterwards:

  1. four point defects (A on B site, B on A site, vacancy on A, vacancy on B), each on its cheapest symmetry-inequivalent site
  2. defect free energies  eps_d(T) = N_def g_def(T) - N_perf g_perf(T)  from the free energy of the defect cell (static
     energies are not enough: the vibrational part changes an anti-site pair by 0.1-0.2 eV between 0 K and 700 K in ACE Al-Li)
  3. the same in several cell sizes until eps_d(T) stops changing (:func:`size_convergence`)
  4. cells with several constitutional anti-sites -> interaction coefficient w_side(T) (:func:`interaction_coefficient`)
  5. G(x, T) = Wagner-Schottky(eps_d(T)) + w2_side(T) c^2 + w3_side(T) c^3  (c = concentration of the constitutional defect;
     :func:`interaction_polynomial`, :class:`CompoundModel`), put into the hull with all other
     phases (:func:`with_compound_models`); the composition range on the hull is the width (:func:`widths_from_regions`)

Conventions: x = fraction of B; ``site_counts`` = (a, b) sites of the A and the B sublattice; defect keys as in
:func:`ftphase.configurational.wagner_schottky_free_energy` ('A_on_B' = an A atom on a B site, 'B_on_A', 'Va_on_A', 'Va_on_B');
energies in eV, 'raw' (the added / removed atom is not referenced: terms linear in x cancel in the common tangent as long as
all phases use the same absolute free energies).  Which defect carries the composition shift on each side (anti-site or
vacancy, e.g. Ni vacancies on the Al-rich side of B2 NiAl) is not an input either: :meth:`CompoundModel.constitutional_defects`
reads it from the defect free energies, and the interaction term w c^2 uses the concentration c of that defect per site
(anti-site: |x - x0|; vacancy on the B sublattice: (b' - x) / (1 - x); vacancy on the A sublattice: 1 - b' / x).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Mapping, Optional, Sequence

import numpy as np

SIDE_DEFECT = {"A_rich": "A_on_B", "B_rich": "B_on_A"}     # x < x0: A on B sites; x > x0: B on A sites


def defect_free_energy(G_defect_cell, G_perfect_cell):
    """eps_d(T) = total free energy of the cell with one defect minus that of the perfect cell with the same number of sites."""
    return np.asarray(G_defect_cell, dtype=float) - np.asarray(G_perfect_cell, dtype=float)


def size_convergence(eps_by_size: Mapping[int, float], tol: float = 0.02):
    """(converged, |difference of the two largest cells|, sizes).  ``eps_by_size`` maps the number of sites to eps_d (or to a
    composition-conserving combination such as the anti-site pair) at one temperature."""
    sizes = sorted(eps_by_size)
    if len(sizes) < 2:
        return False, float("nan"), sizes
    d = abs(float(eps_by_size[sizes[-1]]) - float(eps_by_size[sizes[-2]]))
    return bool(d <= tol), d, sizes


def interaction_coefficient(dG, k, eps: float, n_sites: int) -> float:
    """Least-squares w of  dG_i = k_i eps + w k_i^2 / N  over cells with k_i defects of one kind in N sites
    (eV per site per unit concentration squared; w < 0: the defects attract, the phase widens)."""
    dG = np.asarray(dG, dtype=float)
    k = np.asarray(k, dtype=float)
    r = dG - k * float(eps)
    return float(n_sites * np.sum(k ** 2 * r) / np.sum(k ** 4))


def interaction_polynomial(dG, k, eps: float, n_sites: int):
    """(w2, w3) of  dG_i = k_i eps + N (w2 c_i^2 + w3 c_i^3),  c_i = k_i / N, fitted to the excess PER DEFECT (dG_i / k_i - eps), so
    that cells with few and with many defects weigh alike.  One quadratic term fitted to the total excess is dominated by the cells
    with many defects and missed the Al-rich side of B32 and Al4Li9 (ACE) by 5-11 meV/atom at 4-8 defects per ~100 sites; the cubic
    term removes that.  With fewer than three different k only w2 is fitted (w3 = 0)."""
    dG = np.asarray(dG, dtype=float)
    k = np.asarray(k, dtype=float)
    c = k / float(n_sites)
    y = dG / k - float(eps)
    if len(np.unique(k)) < 3:
        return float(np.sum(c * y) / np.sum(c ** 2)), 0.0
    A = np.array([c, c ** 2]).T
    (w2, w3), *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(w2), float(w3)


@dataclass
class CompoundModel:
    """G(x, T) of one compound from its defect free energies (and, optionally, the interaction coefficients of the two sides)."""

    name: str
    x0: float
    site_counts: Sequence[int]
    T: Sequence[float]
    eps: Mapping[str, Sequence[float]]                       # defect key -> eps_d on the grid T
    w: Mapping[str, Sequence[float]] = field(default_factory=dict)   # defect key -> w on the grid T (absent: 0)
    half_width: object = 0.03                                        # float, or (A-rich side, B-rich side): never wider than the sampled compositions
    side_defects: Optional[Mapping[str, str]] = None                # {'A_rich': key, 'B_rich': key}; None: read from the energies
    w3: Mapping[str, Sequence[float]] = field(default_factory=dict)  # defect key -> cubic interaction coefficient on the grid T (absent: 0)

    def defect_concentration(self, key: str, xs) -> np.ndarray:
        """Concentration per lattice site of the defect ``key`` that alone carries the composition x."""
        xs = np.asarray(xs, dtype=float)
        bp = self.site_counts[1] / float(sum(self.site_counts))
        if key in ("A_on_B", "B_on_A"):
            return np.abs(xs - self.x0)
        if key == "Va_on_B":                                         # B-poor side: x = (b' - c) / (1 - c)
            return np.clip((bp - xs) / (1.0 - xs), 0.0, None)
        if key == "Va_on_A":                                         # A-poor side: x = b' / (1 - c)
            return np.clip(1.0 - bp / xs, 0.0, None)
        raise ValueError(key)

    def constitutional_defects(self, T: float, g0: float = 0.0, dx: float = 0.01) -> Dict[str, str]:
        """Which defect carries the composition shift on the A-rich (x < x0) and on the B-rich side: the one whose removal from
        the model raises G(x0 -+ dx, T) most (anti-site or vacancy; decided by the defect free energies, not by the user).
        ``g0`` = free energy per atom of the perfect compound (needed to weigh vacancies against anti-sites)."""
        from .configurational import wagner_schottky_curve

        e = self.energies(T)
        out = {}
        for side, xq, cands in (("A_rich", self.x0 - dx, ("A_on_B", "Va_on_B")), ("B_rich", self.x0 + dx, ("B_on_A", "Va_on_A"))):
            best, gain = cands[0], -np.inf
            for c in cands:
                e2 = dict(e)
                e2[c] = e[c] + 20.0
                g = float(wagner_schottky_curve(np.array([xq]), T, tuple(self.site_counts), e2, g0_atom=float(g0))[0])
                if g > gain:
                    best, gain = c, g
            out[side] = best
        return out

    @property
    def window(self):
        """(x_low, x_high) of the composition window; the interaction polynomial is a fit and must not be used beyond the cells it was
        fitted to (a cubic term extrapolated outside made Al3Li spuriously stable at the window edge)."""
        lo, hi = (self.half_width if isinstance(self.half_width, (tuple, list)) else (self.half_width, self.half_width))
        return max(self.x0 - float(lo), 1e-6), min(self.x0 + float(hi), 1 - 1e-6)

    def energies(self, T: float) -> Dict[str, float]:
        return {k: float(np.interp(T, self.T, v)) for k, v in self.eps.items()}

    def interaction(self, T: float) -> Dict[str, float]:
        return {k: float(np.interp(T, self.T, v)) for k, v in self.w.items()}

    def values(self, xs, T: float, g0: float) -> np.ndarray:
        """G(x, T) per atom; ``g0`` = free energy per atom of the PERFECT compound (the stoichiometric cell of the table).
        g0 must be the true value, not 0 with a shift afterwards: a vacancy changes the number of atoms, so its cost per atom is
        eps_Va + g0 and a wrong g0 mis-weights every vacancy (anti-sites are not affected).  Thermal defects lower G(x0) below g0."""
        from .configurational import wagner_schottky_curve

        xs = np.asarray(xs, dtype=float)
        e = self.energies(T)
        g = np.asarray(wagner_schottky_curve(xs, T, tuple(self.site_counts), e, g0_atom=float(g0)), dtype=float)
        wi = self.interaction(T)
        if wi:
            sd = self.side_defects or self.constitutional_defects(T, g0)
            lo, hi = sd["A_rich"], sd["B_rich"]
            d = xs - self.x0
            w3 = {k: float(np.interp(T, self.T, v)) for k, v in self.w3.items()}
            cl, ch = self.defect_concentration(lo, xs), self.defect_concentration(hi, xs)
            g = g + np.where(d < 0, wi.get(lo, 0.0) * cl ** 2 + w3.get(lo, 0.0) * cl ** 3, wi.get(hi, 0.0) * ch ** 2 + w3.get(hi, 0.0) * ch ** 3)
        return g

    def phase(self, T: float, g0: float, n: int = 121, n_sample: int = 801):
        """A limited-range :class:`ftphase.equilibrium.PhaseCurve` over x0 +- half_width."""
        from .equilibrium import PhaseCurve

        xs = np.unique(np.concatenate([np.linspace(*self.window, n), [self.x0]]))
        g = self.values(xs, T, g0)
        ok = np.isfinite(g) & (np.abs(g - g0) < 5.0)        # a side without an allowed defect is infeasible (the model returns a huge number): leave it out
        if ok.sum() < 4:
            raise ValueError(f"{self.name}: no feasible composition around x0 = {self.x0:.4f} with the defects {sorted(self.eps)}")
        return PhaseCurve.from_points(self.name, xs[ok], g[ok], fit="spline", limited=True, n_sample=n_sample)


def with_compound_models(builder: Callable, models: Mapping[str, CompoundModel]) -> Callable:
    """Wrap a phase builder (T -> list of phases): every point phase that has a model is replaced by its G(x, T) curve, so that
    no compound is declared a point or a range phase in the input."""

    def build(T):
        out = []
        for p in builder(T):
            m = models.get(getattr(p, "name", None))
            out.append(m.phase(T, p.g0) if (m is not None and hasattr(p, "x0")) else p)
        return out

    return build


def widths_from_regions(regions, models: Mapping[str, CompoundModel], edge_tol: float = 0.002):
    """Per temperature and compound: the composition range on the hull (from the two-phase regions it takes part in), whether the
    compound is stable, and whether the range touches the edge of the window x0 +- half_width (then the width is a lower bound
    and the model has to be extended: more defects per cell, a wider window)."""
    import pandas as pd

    rows = []
    for T, r in regions.groupby("T"):
        for name, m in models.items():
            xs = [c.x_a for c in r.itertuples() if c.phase_a == name] + [c.x_b for c in r.itertuples() if c.phase_b == name]
            lo, hi = (min(xs), max(xs)) if xs else (np.nan, np.nan)
            rows.append({"T": float(T), "phase": name, "stable": bool(xs), "x_min": lo, "x_max": hi, "width": hi - lo,
                         "at_window_edge": bool(xs) and (lo < m.window[0] + edge_tol or hi > m.window[1] - edge_tol)})
    return pd.DataFrame(rows)


def classify(widths, line_tol: float = 0.005):
    """{'phase': 'line compound' | 'range phase' | 'range phase (lower bound: window edge)' | 'not stable'} from the largest width
    over the temperatures at which the phase is on the hull."""
    out = {}
    for name, g in widths.groupby("phase"):
        g = g[g.stable]
        if g.empty:
            out[name] = "not stable"
        elif g.at_window_edge.any():
            out[name] = "range phase (lower bound: window edge)"
        else:
            out[name] = "range phase" if float(g.width.max()) > line_tol else "line compound"
    return out
