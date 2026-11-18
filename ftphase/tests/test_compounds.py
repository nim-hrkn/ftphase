"""ftphase.compounds: one description for every compound, width read from the hull."""
import numpy as np
import pytest

from ftphase.compounds import CompoundModel, classify, defect_free_energy, interaction_coefficient, size_convergence, widths_from_regions, with_compound_models
from ftphase.configurational import wagner_schottky_curve
from ftphase.equilibrium import PhaseCurve, PointPhase


def test_interaction_coefficient_recovers_a_quadratic_term():
    N, eps, w = 108, 1.5, -3.0
    k = np.array([2, 4, 6, 8, 2, 4])
    dG = k * eps + w * k ** 2 / N
    assert interaction_coefficient(dG, k, eps, N) == pytest.approx(w)
    assert interaction_coefficient(k * eps, k, eps, N) == pytest.approx(0.0, abs=1e-12)


def test_size_convergence_and_defect_free_energy():
    ok, d, sizes = size_convergence({32: 0.446, 108: 0.432, 256: 0.4315}, tol=0.02)
    assert ok and d == pytest.approx(0.0005) and sizes == [32, 108, 256]
    assert not size_convergence({16: 0.80, 128: 0.85}, tol=0.02)[0]
    assert defect_free_energy([-10.0, -10.5], [-11.0, -11.4]) == pytest.approx([1.0, 0.9])


def _model(w=None, half=0.03):
    T = [300.0, 900.0]
    eps = {"A_on_B": [-1.15, -1.30], "B_on_A": [1.62, 1.66], "Va_on_A": [4.2, 4.3], "Va_on_B": [2.7, 2.8]}
    return CompoundModel("A3B", 0.25, (3, 1), T, eps, w or {}, half_width=half)


def test_compound_model_reduces_to_wagner_schottky_and_adds_the_interaction():
    m = _model(); xs = np.linspace(0.23, 0.27, 9); T = 600.0
    e = m.energies(T)
    assert e["A_on_B"] == pytest.approx(-1.225)
    assert m.values(xs, T, g0=-3.0) == pytest.approx(wagner_schottky_curve(xs, T, (3, 1), e, g0_atom=-3.0))
    assert m.values(np.array([0.25]), T, g0=-3.0)[0] <= -3.0            # thermal defects can only lower G at stoichiometry
    mw = _model(w={"A_on_B": [-2.0, -2.0], "B_on_A": [4.0, 4.0]})
    d = mw.values(xs, T, g0=-3.0) - m.values(xs, T, g0=-3.0)
    assert d[0] == pytest.approx(-2.0 * 0.02 ** 2) and d[-1] == pytest.approx(4.0 * 0.02 ** 2) and d[4] == pytest.approx(0.0)


def test_width_is_read_from_the_hull_not_from_the_input():
    """The same builder gives a line compound when the defects are expensive and a range phase when they are cheap."""
    from ftphase.diagram import scan

    T = [300.0, 900.0]

    def model(pair):          # anti-site pair energy 'pair' split symmetrically around the tangent slope 0
        return CompoundModel("AB", 0.5, (1, 1), T, {"A_on_B": [pair / 2] * 2, "B_on_A": [pair / 2] * 2, "Va_on_A": [5.0] * 2, "Va_on_B": [5.0] * 2}, half_width=0.06)

    def base(Tk):             # two terminal 'solutions' as steep parabolas, the compound as a point 50 meV below the line joining them
        xa = np.linspace(0.0, 0.2, 41); xb = np.linspace(0.8, 1.0, 41)
        return [PhaseCurve.from_points("alpha", xa, 2.0 * xa ** 2, fit="spline"), PhaseCurve.from_points("beta", xb, 2.0 * (1 - xb) ** 2, fit="spline"), PointPhase("AB", 0.5, -0.05)]

    out = {}
    for label, pair in (("expensive", 3.0), ("cheap", 0.25)):
        mods = {"AB": model(pair)}
        reg = scan(with_compound_models(base, mods), np.array([800.0]), min_width=1e-4)
        w = widths_from_regions(reg, mods)
        out[label] = (float(w.width.iloc[0]), classify(w)["AB"])
    assert out["expensive"][0] < 0.005 and out["expensive"][1] == "line compound"
    assert out["cheap"][0] > 0.02 and out["cheap"][1].startswith("range phase")


def test_constitutional_defect_is_read_from_the_energies():
    """Triple-defect type (B2 NiAl-like, B = Ni): the A-rich side is carried by vacancies on the B sublattice when the A anti-site is
    expensive, by A anti-sites when it is cheap; the B-rich side by B anti-sites."""
    T = [300.0, 2000.0]
    g0 = -4.0          # eV/atom of the perfect compound; chemical potentials mu_A = -3.4, mu_B = -4.6 (mu_A + mu_B = 2 g0)
    def model(a_on_b):
        # raw energies (fixed number of sites): anti-site A_on_B = e_f + mu_A - mu_B, vacancy on B = e_f - mu_B, etc.
        return CompoundModel("AB", 0.5, (1, 1), T, {"A_on_B": [a_on_b + 1.2] * 2, "B_on_A": [0.8 - 1.2] * 2, "Va_on_A": [2.3 + 3.4] * 2, "Va_on_B": [0.9 + 4.6] * 2})
    assert model(3.0).constitutional_defects(1500.0, g0) == {"A_rich": "Va_on_B", "B_rich": "B_on_A"}
    assert model(0.4).constitutional_defects(1500.0, g0) == {"A_rich": "A_on_B", "B_rich": "B_on_A"}
    assert model(3.0).constitutional_defects(1500.0, 0.0)["A_rich"] == "A_on_B"      # with a wrong g0 the vacancy is mis-weighted (the error fixed on 2026-11-19)
    m = model(3.0)
    assert m.defect_concentration("A_on_B", [0.48])[0] == pytest.approx(0.02)
    c = m.defect_concentration("Va_on_B", [0.48])[0]           # x = (0.5 - c) / (1 - c)
    assert (0.5 - c) / (1 - c) == pytest.approx(0.48)
    c = m.defect_concentration("Va_on_A", [0.52])[0]           # x = 0.5 / (1 - c)
    assert 0.5 / (1 - c) == pytest.approx(0.52)
