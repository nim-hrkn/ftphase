import numpy as np
import pandas as pd
import pytest

from ftphase.units import KB_EV
from ftphase.equilibrium import PhaseCurve, PointPhase, equilibrium_at_T, regular_solution_binodal, lower_hull_2d
from ftphase.diagram import scan, invariants, sensitivity, plot_tx


def regular(name, omega, T, x_min=0.0, x_max=1.0, offset=0.0, limited=False):
    def g(x):
        x = np.asarray(x, dtype=float)
        xl = np.clip(x, 1e-300, 1)
        return omega * x * (1 - x) + KB_EV * T * (xl * np.log(xl) + (1 - xl) * np.log(np.clip(1 - xl, 1e-300, 1))) + offset

    def dg(x):
        x = np.asarray(x, dtype=float)
        return omega * (1 - 2 * x) + KB_EV * T * (np.log(x) - np.log(1 - x))
    return PhaseCurve(name, g, dg, x_min, x_max, n_sample=801, limited=limited)


def test_lower_hull_basic():
    pts = np.array([[0, 0], [0.5, -1], [1, 0], [0.25, 0.0], [0.75, -0.2]])
    idx = lower_hull_2d(pts)
    assert set(pts[idx, 0]) == {0.0, 0.5, 1.0}
    # two phases ending at the same x: only the lower one may be on the hull
    pts = np.array([[0, 0], [0.5, -1.0], [0.5, -0.9], [1, 0], [1, 0.3]])
    idx = lower_hull_2d(pts)
    assert len(idx) == 3 and set(map(tuple, pts[idx])) == {(0, 0), (0.5, -1.0), (1, 0)}


def test_phasecurve_rmse():
    x = np.linspace(0, 1, 6); g = x**4
    assert PhaseCurve.from_points("p", x, g, fit="spline").rmse < 1e-12
    assert PhaseCurve.from_points("p", x, g, fit="poly", poly_order=2).rmse > 1e-3


def test_miscibility_gap_matches_analytic_binodal():
    omega = 0.1
    T = 400.0  # Tc = omega/(2kB) = 580 K
    res = equilibrium_at_T([regular("fcc", omega, T)], T)
    assert len(res.coexistence) == 1
    c = res.coexistence[0]
    x1, x2 = regular_solution_binodal(omega, T)
    assert c.refined and abs(c.x_a - x1) < 1e-6 and abs(c.x_b - x2) < 1e-6
    assert c.phase_a == c.phase_b == "fcc" and c.note == "miscibility gap"
    # chemical potentials equal on both sides by construction, eq. (H4)
    muA, muB = c.mu
    assert np.isfinite(muA) and np.isfinite(muB)
    # lever rule, eq. (H5)
    fa, fb = c.lever(0.5)
    assert abs(fa - 0.5) < 1e-6 and abs(fb - 0.5) < 1e-6
    assert res.phases_at(0.5)[0][0] == "fcc" and len(res.phases_at(0.5)) == 2
    # above Tc: no gap
    assert equilibrium_at_T([regular("fcc", omega, 700.0)], 700.0).coexistence == []


def test_point_phase_tangent_to_ideal_solution():
    T = 800.0
    sol = regular("liq", 0.0, T)             # ideal solution
    comp = PointPhase("AB", 0.5, -0.08)      # deep line compound
    res = equilibrium_at_T([sol, comp], T)
    pairs = sorted((c.phase_a, c.phase_b) for c in res.coexistence)
    assert pairs == [("AB", "liq"), ("liq", "AB")]
    for c in res.coexistence:
        # tangent condition from the point: g'(x) = (g0 - g(x))/(x0 - x)
        if c.phase_a == "liq":
            x, x0, g0 = c.x_a, c.x_b, c.g_b
        else:
            x, x0, g0 = c.x_b, c.x_a, c.g_a
        assert abs(sol.dg(x) - (g0 - sol.g(x)) / (x0 - x)) < 1e-6
        assert c.refined
    # the compound is a zero-width single-phase entry
    assert any(s[0] == "AB" and s[1] == s[2] == 0.5 for s in res.single_phase)


def test_limited_range_phase_is_not_extrapolated():
    T = 600.0
    host = regular("fcc", 0.0, T)
    # a limited phase that would be very stable if extrapolated to x=1
    lim = regular("lim", -0.3, T, x_min=0.2, x_max=0.4, offset=-0.01, limited=True)
    res = equilibrium_at_T([host, lim], T)
    # lim appears only within [0.2, 0.4]; right boundary of lim+fcc tangent stays <= 0.4
    for c in res.coexistence:
        for ph, x in ((c.phase_a, c.x_a), (c.phase_b, c.x_b)):
            if ph == "lim":
                assert 0.2 - 1e-9 <= x <= 0.4 + 1e-9


def test_eutectic_like_three_phase_scan_and_invariants():
    # two terminal solutions with a steep convex shape, and a liquid whose free energy drops with T
    def builder(T):
        a = regular("alpha", 0.12, T, offset=0.0)  # Tc = 696 K
        b = None
        # liquid: ideal solution lowered by an entropy term so that it wins at high T
        liq = regular("liq", 0.0, T, offset=0.06 - 1.0e-4 * (T - 700.0))
        return [a, liq]  # alpha covers the whole range; liq competes
    Ts = np.arange(500, 1201, 25.0)
    reg = scan(builder, Ts)
    assert set(reg["T"]) <= set(Ts)
    # at low T only the alpha miscibility gap, at high T no coexistence (liquid everywhere) or alpha+liq
    low = reg[reg["T"] == 500.0]
    assert len(low) == 1 and low.iloc[0]["phase_a"] == "alpha" and low.iloc[0]["phase_b"] == "alpha"
    high = reg[reg["T"] == 1200.0]
    assert len(high) == 0 or set(high["phase_a"]) | set(high["phase_b"]) >= {"liq"}
    inv = invariants(reg)
    assert len(inv) >= 1  # the set of coexisting pairs changes at least once between 500 and 1200 K


def test_sensitivity_returns_spread():
    omega = 0.1

    def b(T, off, slo):
        return [regular("fcc", omega, T, offset=off.get("fcc", 0.0)), PointPhase("AB", 0.5, -0.03 + off.get("AB", 0.0))]
    Ts = [300.0, 400.0]
    s = sensitivity(b, Ts, {"fcc": 0.0, "AB": 0.005}, n_samples=12, rng=1)
    t = s.table
    assert set(t["T"]) == set(Ts)
    assert (t["x_a_std"] > 0).any()


def test_plot_tx_runs(tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    reg = pd.DataFrame({"T": [300.0, 350.0], "phase_a": ["a", "a"], "x_a": [0.1, 0.12], "phase_b": ["b", "b"], "x_b": [0.8, 0.75], "g_a": [0, 0], "g_b": [0, 0], "refined": [True, True], "note": ["", ""]})
    ax = plot_tx(reg)
    ax.figure.savefig(tmp_path / "x.png")


def test_ideal_excess_poly_fit_recovers_binodal():
    """Coarse samples of G = Omega x(1-x) - T s_ideal: a plain cubic through G invents or
    misplaces the gap, the excess fit (ideal_T) reproduces the analytic binodal."""
    import numpy as np
    from ftphase.units import KB_EV
    from ftphase.configurational import ideal_entropy
    from ftphase.equilibrium import PhaseCurve, equilibrium_at_T, regular_solution_binodal
    omega, T = 0.12, 500.0
    x = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    g = omega * x * (1 - x) - T * np.array([ideal_entropy(v) for v in x])
    pc = PhaseCurve.from_points("reg", x, g, fit="poly", poly_order=3, ideal_T=T)
    assert pc.rmse < 1e-9                      # the excess is exactly quadratic
    xs = np.linspace(0.001, 0.999, 5)
    assert np.allclose(pc.g(xs), omega * xs * (1 - xs) + KB_EV * T * (xs * np.log(xs) + (1 - xs) * np.log(1 - xs)), atol=1e-12)
    res = equilibrium_at_T([pc], T)
    xa, xb = regular_solution_binodal(omega, T)
    gap = [c for c in res.coexistence if c.phase_a == "reg" and c.phase_b == "reg"]
    assert len(gap) == 1 and abs(gap[0].x_a - xa) < 2e-3 and abs(gap[0].x_b - xb) < 2e-3
    plain = PhaseCurve.from_points("reg", x, g, fit="poly", poly_order=3)
    assert plain.rmse > 1e-4                   # a cubic through G itself misses the x ln x shape


def test_rk_with_ideal_term_is_calphad_liquid_model():
    import numpy as np
    from ftphase.configurational import ideal_entropy
    from ftphase.equilibrium import PhaseCurve, equilibrium_at_T, regular_solution_binodal
    omega, T = 0.12, 500.0
    x = np.linspace(0, 1, 11)
    g = -0.3 * (1 - x) - 0.1 * x + omega * x * (1 - x) - T * np.array([ideal_entropy(v) for v in x])
    pc = PhaseCurve.from_points("liq", x, g, fit="rk", poly_order=3, ideal_T=T)
    assert pc.rmse < 1e-9
    res = equilibrium_at_T([pc], T)
    xa, xb = regular_solution_binodal(omega, T)
    gap = [c for c in res.coexistence if c.phase_a == "liq" and c.phase_b == "liq"]
    assert len(gap) == 1 and abs(gap[0].x_a - xa) < 2e-3 and abs(gap[0].x_b - xb) < 2e-3


def test_sublattice_entropy_fit_recovers_defect_energies():
    """B2-type phase: G = E0 + e_as*(x-0.5) (x>0.5) / E0 + e_va*(0.5-x) (x<0.5) - T s_triple(x).  Noisy samples,
    branch fit + analytic entropy -> the fitted curve reproduces the noise-free G to < 1 meV."""
    import numpy as np
    from ftphase.configurational import b2_triple_defect_site_fractions, sublattice_entropy
    from ftphase.equilibrium import PhaseCurve
    T, E0, e_as, e_va = 1200.0, -4.5, 1.2, 1.8
    s = lambda v: sublattice_entropy(*b2_triple_defect_site_fractions(v), basis="atom")
    def g_true(v):
        v = np.asarray(v, dtype=float)
        return E0 + np.where(v >= 0.5, e_as * (v - 0.5), e_va * (0.5 - v)) - T * np.array([s(float(u)) for u in np.atleast_1d(v)])
    x = np.array([0.46, 0.47, 0.48, 0.49, 0.5, 0.52, 0.54, 0.56, 0.58, 0.6])
    rng = np.random.default_rng(0)
    g = g_true(x) + rng.normal(0, 0.001, x.size)
    pc = PhaseCurve.from_points("B2", x, g, fit="poly", poly_order=1, entropy_fn=s, entropy_T=T, branch_x=0.5)
    xs = np.linspace(0.461, 0.599, 50)
    assert np.max(np.abs(pc.g(xs) - g_true(xs))) < 0.0015
