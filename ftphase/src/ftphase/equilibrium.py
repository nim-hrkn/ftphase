"""Stage 06: lower convex hull of all phases at one (T, P) and common tangents.

Implements eq. (H1)-(H5) of docs/workflow.html for a binary system:

* every phase contributes points (x, g) to the lower convex hull in the
  (x, g) plane: a solution phase as a dense sampling of its fitted g(x)
  within its validity interval (limited-range phases are *not* extrapolated,
  workflow section 7), a point phase (line compound) as a single point;
* hull edges joining two different phases, or the same phase across a gap in
  its sampling (miscibility gap), are coexistence segments; they are refined
  by solving the common-tangent condition eq. (H3)

      g_a'(x_a) = g_b'(x_b) = (g_b(x_b) - g_a(x_a)) / (x_b - x_a)

  (for a point phase only the second equality applies);
* chemical potentials, eq. (H4), and lever rule, eq. (H5), are provided.

The 2-D lower hull is the monotone-chain algorithm (Andrew 1979); the
common-tangent refinement generalises ``find_common_tangent`` of the pyiron
potentials-workshop-2022 ``phase_diagram/helpers.py`` (S. Menon et al.,
https://github.com/pyiron/potentials-workshop-2022, BSD-3) from two cubic
polynomials to arbitrary callables with derivatives, including point phases.
``pymatgen.analysis.phase_diagram`` (Ong et al. 2008) does the same hull for
0 K formation energies with compositions as points; it is used in
:mod:`ftphase.validate` for the 0 K cross-check.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

from .units import KB_EV
from scipy.interpolate import CubicSpline, UnivariateSpline
from scipy.optimize import fsolve


# ---------------------------------------------------------------------------
# phase descriptions
# ---------------------------------------------------------------------------
@dataclass
class PhaseCurve:
    """A solution phase g(x) on [x_min, x_max] (eV/atom)."""

    name: str
    g: Callable[[np.ndarray], np.ndarray]
    dg: Callable[[np.ndarray], np.ndarray]
    x_min: float = 0.0
    x_max: float = 1.0
    n_sample: int = 401
    limited: bool = False
    rmse: float = 0.0          # fit residual (eV/atom) of from_points; 0 for interpolating fits

    @classmethod
    def from_points(cls, name, x, g, fit: str = "spline", x_min=None, x_max=None, poly_order: int = 4, smoothing: float = 0.0, n_sample: int = 401, limited: bool = False, weights=None, ideal_T: Optional[float] = None, entropy_fn: Optional[Callable[[float], float]] = None, entropy_T: Optional[float] = None, branch_x: Optional[float] = None):
        """Build from sampled (x, g).

        ``entropy_fn`` + ``entropy_T``: generalisation of ``ideal_T`` for an
        ordered phase with a sublattice model: entropy_fn(x) is the
        configurational entropy per atom (eV/K, e.g. from
        configurational.sublattice_entropy with the phase's site model); the
        term -T s(x) is subtracted before fitting and added back analytically,
        so that only the smooth defect-energy part is fitted.  ``branch_x``
        (the stoichiometric composition) splits the 'poly' fit into two
        independent branches (anti-sites on one side, vacancies or the other
        anti-site on the other), each including the stoichiometric point.
        ``ideal_T``: if given (K), the analytic ideal-mixing term
        -T s_ideal(x) = k_B T [x ln x + (1-x) ln(1-x)] is subtracted from the
        samples before fitting and added back analytically, so that 'poly',
        'smooth' or 'rk' fit only the smooth excess part and the x ln x
        singularity at the end points is kept exactly ('rk' + ideal_T is the
        CALPHAD substitutional-solution model: ideal mixing + Redlich-Kister).  Use it for a random solution (the
        ideal term was added by assemble.add_configurational_term) and for a
        calphy liquid (whose TI free energy already contains the mixing
        entropy).  Ignored for 'spline'.

        fit = 'spline' (natural cubic spline through the points, exact),
              'smooth' (UnivariateSpline with smoothing factor ``smoothing``),
              'poly'   (least-squares polynomial of ``poly_order``, as in the
                        pyiron workshop tutorial and calphy's default),
              'rk'     (Redlich-Kister: g = (1-x)gA + x gB + kT-free excess
                        x(1-x) sum L_k (1-2x)^k, with poly_order = number of L
                        terms; only the excess part is fitted so that the end
                        points are reproduced exactly; requires x=0 and x=1
                        in the data).
        """
        x = np.asarray(x, dtype=float)
        g = np.asarray(g, dtype=float)
        o = np.argsort(x)
        x, g = x[o], g[o]
        if len(x) < 2:
            raise ValueError("a solution phase needs at least two compositions; use PointPhase")
        lo = float(x[0] if x_min is None else x_min)
        hi = float(x[-1] if x_max is None else x_max)
        base = dbase = None
        if entropy_fn is not None and entropy_T is not None and fit in ("poly", "smooth"):
            Tk = float(entropy_T)
            xs_ = np.linspace(lo, hi, 2001)
            tab = np.array([float(entropy_fn(float(v))) for v in xs_])

            def base(v, xs_=xs_, tab=tab, Tk=Tk):
                return -Tk * np.interp(np.asarray(v, dtype=float), xs_, tab)

            def dbase(v, xs_=xs_, tab=tab, Tk=Tk):
                return -Tk * np.interp(np.asarray(v, dtype=float), xs_, np.gradient(tab, xs_))

            g = g - base(x)
        elif ideal_T is not None and fit in ("poly", "smooth", "rk"):
            kT = KB_EV * float(ideal_T)

            def base(v, kT=kT):
                v = np.clip(np.asarray(v, dtype=float), 1e-12, 1 - 1e-12)
                return kT * (v * np.log(v) + (1 - v) * np.log(1 - v))

            def dbase(v, kT=kT):
                v = np.clip(np.asarray(v, dtype=float), 1e-12, 1 - 1e-12)
                return kT * np.log(v / (1 - v))

            g = g - base(x)
        if fit == "spline":
            cs = CubicSpline(x, g, bc_type="natural")
            f, df = cs, cs.derivative()
        elif fit == "smooth":
            k = min(3, len(x) - 1)
            us = UnivariateSpline(x, g, k=k, s=smoothing, w=weights)
            f, df = us, us.derivative()
        elif fit == "poly" and branch_x is not None and (x < branch_x - 1e-9).any() and (x > branch_x + 1e-9).any():
            # two polynomial branches meeting at branch_x (both include the points at branch_x)
            left = x <= branch_x + 1e-9; right = x >= branch_x - 1e-9
            kl = min(poly_order, left.sum() - 1); kr = min(poly_order, right.sum() - 1)
            pl = np.polyfit(x[left], g[left], kl, w=None if weights is None else np.asarray(weights)[left])
            pr = np.polyfit(x[right], g[right], kr, w=None if weights is None else np.asarray(weights)[right])
            dpl, dpr = np.polyder(pl), np.polyder(pr)

            def f(v, pl=pl, pr=pr, bx=branch_x):
                v = np.asarray(v, dtype=float)
                return np.where(v < bx, np.polyval(pl, v), np.polyval(pr, v))

            def df(v, dpl=dpl, dpr=dpr, bx=branch_x):
                v = np.asarray(v, dtype=float)
                return np.where(v < bx, np.polyval(dpl, v), np.polyval(dpr, v))
        elif fit == "poly":
            k = min(poly_order, len(x) - 1)
            p = np.polyfit(x, g, k, w=weights)
            dp = np.polyder(p)
            f, df = (lambda v, p=p: np.polyval(p, v)), (lambda v, dp=dp: np.polyval(dp, v))
        elif fit == "rk":
            if not (np.isclose(x[0], 0.0) and np.isclose(x[-1], 1.0)):
                raise ValueError("Redlich-Kister fit needs the pure end points x=0 and x=1")
            gA, gB = g[0], g[-1]
            ex = g - ((1 - x) * gA + x * gB)
            inner = (x > 1e-9) & (x < 1 - 1e-9)
            nL = max(1, poly_order)
            A = np.array([[xi * (1 - xi) * (1 - 2 * xi) ** k for k in range(nL)] for xi in x[inner]])
            L, *_ = np.linalg.lstsq(A, ex[inner], rcond=None)

            def f(v, gA=gA, gB=gB, L=L):
                v = np.asarray(v, dtype=float)
                return (1 - v) * gA + v * gB + v * (1 - v) * sum(Lk * (1 - 2 * v) ** k for k, Lk in enumerate(L))

            def df(v, gA=gA, gB=gB, L=L):
                v = np.asarray(v, dtype=float)
                s = sum(Lk * (1 - 2 * v) ** k for k, Lk in enumerate(L))
                ds = sum(-2 * k * Lk * (1 - 2 * v) ** (k - 1) for k, Lk in enumerate(L) if k > 0)
                return gB - gA + (1 - 2 * v) * s + v * (1 - v) * ds
        else:
            raise ValueError("fit must be spline/smooth/poly/rk")
        rmse = float(np.sqrt(np.mean((np.asarray(f(x), dtype=float) - g) ** 2)))
        if base is not None:
            f0, df0 = f, df
            f = lambda v, f0=f0, base=base: np.asarray(f0(v), dtype=float) + base(v)      # noqa: E731
            df = lambda v, df0=df0, dbase=dbase: np.asarray(df0(v), dtype=float) + dbase(v)  # noqa: E731
        return cls(name, f, df, lo, hi, n_sample, limited, rmse)

    def sample(self):
        xs = np.linspace(self.x_min, self.x_max, self.n_sample)
        return xs, np.asarray(self.g(xs), dtype=float)


@dataclass
class PointPhase:
    """A fixed-composition phase (line compound) at x0 with g0 (eV/atom)."""

    name: str
    x0: float
    g0: float


Phase = Union[PhaseCurve, PointPhase]


# ---------------------------------------------------------------------------
# lower hull
# ---------------------------------------------------------------------------
def lower_hull_2d(points: np.ndarray) -> np.ndarray:
    """Indices of the lower convex hull of 2-D points (x ascending). Andrew's monotone chain."""
    pts = np.asarray(points, dtype=float)
    order = np.lexsort((pts[:, 1], pts[:, 0]))
    # points with (numerically) the same x: keep only the lowest g
    keep = []
    for i in order:
        if keep and abs(pts[i, 0] - pts[keep[-1], 0]) < 1e-12:
            continue  # same x, higher (or equal) g because of the lexsort
        keep.append(i)
    order = keep
    hull: List[int] = []
    for i in order:
        while len(hull) >= 2:
            o, a = pts[hull[-2]], pts[hull[-1]]
            b = pts[i]
            cross = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
            if cross <= 1e-15:  # a is not strictly below the chord o-b -> drop
                hull.pop()
            else:
                break
        hull.append(int(i))
    # remove duplicate x at the same point
    return np.array(hull, dtype=int)


@dataclass
class Coexistence:
    phase_a: str
    x_a: float
    phase_b: str
    x_b: float
    g_a: float = np.nan
    g_b: float = np.nan
    refined: bool = False
    note: str = ""

    @property
    def mu(self) -> Tuple[float, float]:
        """Chemical potentials (mu_A, mu_B) on the tangent, eq. (H4)."""
        slope = (self.g_b - self.g_a) / (self.x_b - self.x_a)
        muA = self.g_a - self.x_a * slope
        muB = self.g_a + (1 - self.x_a) * slope
        return muA, muB

    def lever(self, x_bar: float) -> Tuple[float, float]:
        """Phase fractions (f_a, f_b) at overall composition x_bar, eq. (H5)."""
        fb = (x_bar - self.x_a) / (self.x_b - self.x_a)
        return 1.0 - fb, fb


@dataclass
class EquilibriumResult:
    T: float
    coexistence: List[Coexistence]
    hull_points: np.ndarray            # (n, 2) x, g on the hull
    hull_phases: List[str]
    single_phase: List[Tuple[str, float, float]]  # (phase, x_lo, x_hi) stable single-phase ranges

    def phases_at(self, x_bar: float):
        """Stable phase(s) and fractions at overall composition x_bar."""
        for c in self.coexistence:
            if c.x_a - 1e-12 <= x_bar <= c.x_b + 1e-12:
                fa, fb = c.lever(x_bar)
                return [(c.phase_a, fa), (c.phase_b, fb)]
        for ph, lo, hi in self.single_phase:
            if lo - 1e-12 <= x_bar <= hi + 1e-12:
                return [(ph, 1.0)]
        return []


def _refine_pair(pa: Phase, xa: float, pb: Phase, xb: float) -> Tuple[float, float, bool]:
    """Solve eq. (H3) for the pair, starting from the hull estimate."""
    a_curve, b_curve = isinstance(pa, PhaseCurve), isinstance(pb, PhaseCurve)
    if not a_curve and not b_curve:
        return xa, xb, True

    def clamp(p: PhaseCurve, v):
        return float(np.clip(v, p.x_min, p.x_max))

    if a_curve and b_curve:
        def eqs(v):
            x1, x2 = v
            d = x2 - x1 if abs(x2 - x1) > 1e-12 else 1e-12
            return [pa.dg(x1) - pb.dg(x2), (pb.g(x2) - pa.g(x1)) / d - pa.dg(x1)]
        sol, info, ier, _ = fsolve(eqs, [xa, xb], full_output=True)
        x1, x2 = float(sol[0]), float(sol[1])
        ok = ier == 1 and pa.x_min - 1e-9 <= x1 <= pa.x_max + 1e-9 and pb.x_min - 1e-9 <= x2 <= pb.x_max + 1e-9 and x1 < x2
        return (x1, x2, True) if ok else (xa, xb, False)
    # one point phase
    if a_curve:
        curve, xc, xp, gp = pa, xa, pb.x0, pb.g0
    else:
        curve, xc, xp, gp = pb, xb, pa.x0, pa.g0

    def eq(v):
        x1 = v[0]
        d = xp - x1 if abs(xp - x1) > 1e-12 else 1e-12
        return [(gp - curve.g(x1)) / d - curve.dg(x1)]
    sol, info, ier, _ = fsolve(eq, [xc], full_output=True)
    x1 = float(sol[0])
    ok = ier == 1 and curve.x_min - 1e-9 <= x1 <= curve.x_max + 1e-9
    if not ok:
        return xa, xb, False
    return (x1, xp, True) if a_curve else (xp, x1, True)


def lower_hull(phases: Sequence[Phase]) -> Tuple[np.ndarray, List[str], np.ndarray]:
    """All sampled points and their lower hull. Returns (points, labels, hull_idx)."""
    pts, labels, local = [], [], []
    for p in phases:
        if isinstance(p, PointPhase):
            pts.append((p.x0, p.g0)); labels.append(p.name); local.append(-1)
        else:
            xs, gs = p.sample()
            for i, (x, g) in enumerate(zip(xs, gs)):
                pts.append((x, g)); labels.append(p.name); local.append(i)
    pts = np.array(pts, dtype=float)
    if not np.all(np.isfinite(pts)):
        raise ValueError("non-finite free energies in hull input")
    idx = lower_hull_2d(pts)
    return pts, labels, idx


def equilibrium_at_T(phases: Sequence[Phase], T: float = np.nan, refine: bool = True, gap_tol: float = 1.5, min_width: float = 1e-6) -> EquilibriumResult:
    """Lower convex hull + common tangents of all phases at one temperature.

    ``gap_tol``: two consecutive hull points of the same solution phase are a
    miscibility gap when their x spacing exceeds gap_tol * (sampling step).
    ``min_width``: segments narrower than this (e.g. a point phase sitting
    exactly on a curve's end point) are discarded.
    """
    byname: Dict[str, Phase] = {p.name: p for p in phases}
    pts, labels, idx = lower_hull(phases)
    hull_x = pts[idx, 0]
    hull_g = pts[idx, 1]
    hull_lab = [labels[i] for i in idx]
    coex: List[Coexistence] = []
    for k in range(len(idx) - 1):
        la, lb = hull_lab[k], hull_lab[k + 1]
        xa, xb = hull_x[k], hull_x[k + 1]
        pa, pb = byname[la], byname[lb]
        is_gap = False
        if la == lb:
            if isinstance(pa, PhaseCurve):
                step = (pa.x_max - pa.x_min) / max(pa.n_sample - 1, 1)
                is_gap = (xb - xa) > gap_tol * step
            if not is_gap:
                continue
        if xb - xa < min_width:
            continue
        c = Coexistence(la, float(xa), lb, float(xb), float(hull_g[k]), float(hull_g[k + 1]), False, "miscibility gap" if is_gap else "")
        if refine:
            x1, x2, ok = _refine_pair(pa, xa, pb, xb)
            if ok and x2 - x1 >= min_width:
                c.x_a, c.x_b, c.refined = x1, x2, True
                c.g_a = float(pa.g(x1)) if isinstance(pa, PhaseCurve) else pa.g0
                c.g_b = float(pb.g(x2)) if isinstance(pb, PhaseCurve) else pb.g0
        coex.append(c)
    # single-phase ranges: pieces of the hull between coexistence segments
    single: List[Tuple[str, float, float]] = []
    cuts = sorted([(c.x_a, c.x_b) for c in coex])
    xlo = float(hull_x[0])
    for (a, b) in cuts + [(float(hull_x[-1]), float(hull_x[-1]))]:
        if a - xlo > min_width:
            # which phase is on the hull in (xlo, a)?
            mid = 0.5 * (xlo + a)
            j = int(np.searchsorted(hull_x, mid))
            lab = hull_lab[min(max(j - 1, 0), len(hull_lab) - 1)]
            single.append((lab, xlo, a))
        xlo = b
    # point phases that are on the hull count as zero-width single-phase ranges
    for p in phases:
        if isinstance(p, PointPhase) and any(abs(hull_x - p.x0) < 1e-12) and p.name in hull_lab:
            if not any(s[0] == p.name for s in single):
                single.append((p.name, p.x0, p.x0))
    single.sort(key=lambda s: s[1])
    return EquilibriumResult(T, coex, np.column_stack([hull_x, hull_g]), hull_lab, single)


# ---------------------------------------------------------------------------
# analytic reference: symmetric regular solution (for tests and sanity checks)
# ---------------------------------------------------------------------------
def regular_solution_binodal(omega: float, T: float) -> Optional[Tuple[float, float]]:
    """Binodal compositions of g = Omega x(1-x) + kT[x ln x + (1-x) ln(1-x)].

    Returns (x1, 1-x1) or None above the critical temperature T_c = Omega/(2 k_B).
    The equation solved is ln(x/(1-x)) = Omega (2x-1)/(k_B T).
    """
    from .units import KB_EV
    from scipy.optimize import brentq

    Tc = omega / (2 * KB_EV)
    if T >= Tc:
        return None
    f = lambda x: np.log(x / (1 - x)) - omega * (2 * x - 1) / (KB_EV * T)
    x1 = brentq(f, 1e-12, 0.5 - 1e-12)
    return x1, 1 - x1
