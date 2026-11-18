"""Ordered compounds without prior knowledge of their kind (line compound or phase with a composition range).

Every compound A_a B_b gets the same description and its width is read from the lower hull afterwards:

  1. four point defects (A on B site, B on A site, vacancy on A, vacancy on B), each on its cheapest symmetry-inequivalent site
  2. defect free energies  eps_d(T) = N_def g_def(T) - N_perf g_perf(T)  from the free energy of the defect cell (static
     energies are not enough: the vibrational part changes an anti-site pair by 0.1-0.2 eV between 0 K and 700 K in ACE Al-Li)
  3. the same in several cell sizes until eps_d(T) stops changing (:func:`size_convergence`)
  4. cells with several constitutional anti-sites -> interaction coefficient w_side(T) (:func:`interaction_coefficient`)
  5. G(x, T) = Wagner-Schottky(eps_d(T)) + w_side(T) (x - x0)^2   (:class:`CompoundModel`), put into the hull with all other
     phases (:func:`with_compound_models`); the composition range on the hull is the width (:func:`widths_from_regions`)

Conventions: x = fraction of B; ``site_counts`` = (a, b) sites of the A and the B sublattice; defect keys as in
:func:`ftphase.configurational.wagner_schottky_free_energy` ('A_on_B' = an A atom on a B site, 'B_on_A', 'Va_on_A', 'Va_on_B');
energies in eV, 'raw' (the added / removed atom is not referenced: terms linear in x cancel in the common tangent as long as
all phases use the same absolute free energies).  The interaction term assumes that the composition shift is carried by
anti-sites (concentration per site = |x - x0|); a vacancy-compensated side needs its own relation and is not covered.
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


@dataclass
class CompoundModel:
    """G(x, T) of one compound from its defect free energies (and, optionally, the interaction coefficients of the two sides)."""

    name: str
    x0: float
    site_counts: Sequence[int]
    T: Sequence[float]
    eps: Mapping[str, Sequence[float]]                       # defect key -> eps_d on the grid T
    w: Mapping[str, Sequence[float]] = field(default_factory=dict)   # 'A_on_B' / 'B_on_A' -> w on the grid T (absent: 0)
    half_width: float = 0.03

    def energies(self, T: float) -> Dict[str, float]:
        return {k: float(np.interp(T, self.T, v)) for k, v in self.eps.items()}

    def interaction(self, T: float) -> Dict[str, float]:
        return {k: float(np.interp(T, self.T, v)) for k, v in self.w.items()}

    def values(self, xs, T: float, g0: float = 0.0) -> np.ndarray:
        """G(x, T) per atom with G(x0) = g0 (the free energy of the perfect compound, thermal defects included in the shape)."""
        from .configurational import wagner_schottky_curve

        xs = np.asarray(xs, dtype=float)
        e = self.energies(T)
        g = np.asarray(wagner_schottky_curve(xs, T, tuple(self.site_counts), e, g0_atom=0.0), dtype=float)
        gref = float(wagner_schottky_curve(np.array([self.x0]), T, tuple(self.site_counts), e, g0_atom=0.0)[0])
        wi = self.interaction(T)
        d = xs - self.x0
        g = g + np.where(d < 0, wi.get("A_on_B", 0.0), wi.get("B_on_A", 0.0)) * d ** 2
        return g0 + g - gref

    def phase(self, T: float, g0: float, n: int = 121, n_sample: int = 801):
        """A limited-range :class:`ftphase.equilibrium.PhaseCurve` over x0 +- half_width."""
        from .equilibrium import PhaseCurve

        xs = np.linspace(max(self.x0 - self.half_width, 1e-6), min(self.x0 + self.half_width, 1 - 1e-6), n)
        return PhaseCurve.from_points(self.name, xs, self.values(xs, T, g0), fit="spline", limited=True, n_sample=n_sample)


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
                         "at_window_edge": bool(xs) and (lo < m.x0 - m.half_width + edge_tol or hi > m.x0 + m.half_width - edge_tol)})
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
