"""ftphase.tdb: the database written from a free-energy table reproduces the table when read back with pycalphad."""
import numpy as np
import pytest

from ftphase.compounds import CompoundModel
from ftphase.records import FreeEnergyTable
from ftphase.tdb import EV, R, fit_T, write_tdb

KB = 8.617333262e-5


def _table():
    rows = []
    Ts = np.arange(300.0, 1001.0, 50.0)
    gA = lambda T: -3.70 - 2.0e-4 * T - 1.0e-7 * T ** 2
    gB = lambda T: -1.90 - 3.0e-4 * T - 2.0e-7 * T ** 2
    for T in Ts:
        for x in np.linspace(0, 1, 11):
            ideal = KB * T * (x * np.log(x) + (1 - x) * np.log(1 - x)) if 0 < x < 1 else 0.0
            gex = x * (1 - x) * ((-0.30 + 1.0e-4 * T) + (0.05) * (1 - 2 * x))
            rows.append({"phase": "fcc", "kind": "solution", "x": x, "T": T, "P_GPa": 0.0, "G": (1 - x) * gA(T) + x * gB(T) + gex + ideal, "G_err": 0.0, "V": 16.0,
                         "model": "toy", "reference_state": "absolute", "method": "analytic", "config_entropy": "ideal", "quantum": "classical", "n_atoms": 32, "source": "test"})
        rows.append({"phase": "A3B", "kind": "point", "x": 0.25, "T": T, "P_GPa": 0.0, "G": 0.75 * gA(T) + 0.25 * gB(T) - 0.12 + 2.0e-5 * T, "G_err": 0.0, "V": 16.0,
                     "model": "toy", "reference_state": "absolute", "method": "analytic", "config_entropy": "none", "quantum": "classical", "n_atoms": 4, "source": "test"})
    return FreeEnergyTable.from_rows(rows, {}), gA, gB


def test_fit_T_recovers_coefficients():
    T = np.linspace(300, 1000, 30)
    c, rms = fit_T(T, 5.0 - 2.0 * T + 0.3 * T * np.log(T) - 1e-3 * T ** 2, 4)
    assert c == pytest.approx([5.0, -2.0, 0.3, -1e-3], rel=1e-6) and rms < 1e-6


def test_written_tdb_reproduces_the_table():
    pycalphad = pytest.importorskip("pycalphad")
    from pycalphad import Database, calculate

    tab, gA, gB = _table()
    T = [300.0, 1000.0]
    model = CompoundModel("A3B", 0.25, (3, 1), T, {"A_on_B": [-1.15, -1.30], "B_on_A": [1.62, 1.66], "Va_on_A": [4.2, 4.3], "Va_on_B": [2.7, 2.8]})
    text, rep = write_tdb(tab, ("Al", "Li"), {"fcc": "FCC_A1"}, {"A3B": {"name": "AL3LI", "site_counts": (3, 1), "kind": "cef"}}, T_fit=(300, 1000), terms=4,
                          rk_order=1, compound_terms=2, models={"A3B": model}, reference=("fcc", "fcc"))
    assert rep["solutions"]["fcc"]["rms_meV"] < 1e-3
    rk = rep["solutions"]["fcc"]["rk_J"]
    assert rk[0][1] == pytest.approx(-0.30 * EV, rel=1e-4) and rk[0][2] == pytest.approx(1.0e-4 * EV, rel=1e-3) and rk[1][1] == pytest.approx(0.05 * EV, rel=1e-3)
    assert rep["compounds"]["A3B"]["dH_f_J"] == pytest.approx((-0.12 - 0.75 * 0.25 * (-0.30 + 0.05 * 0.5) * 0) * EV, rel=1e-6)      # formation vs the pure-element references: -0.12 eV, -2e-5 eV/K
    assert rep["compounds"]["A3B"]["dS_f_J_K"] == pytest.approx(-2.0e-5 * EV, rel=1e-6)
    db = Database(text)
    assert set(db.phases) == {"FCC_A1", "AL3LI"}
    # solution: G(x = 0.3, 700 K)
    x, Tk = 0.3, 700.0
    ref = ((1 - x) * gA(Tk) + x * gB(Tk) + x * (1 - x) * ((-0.30 + 1.0e-4 * Tk) + 0.05 * (1 - 2 * x)) + KB * Tk * (x * np.log(x) + (1 - x) * np.log(1 - x))) * EV
    res = calculate(db, ["AL", "LI", "VA"], "FCC_A1", T=Tk, P=101325, N=1, points=np.array([[1 - x, x]]))
    assert float(res.GM.values.ravel()[0]) == pytest.approx(ref, abs=2.0)
    # compound: perfect A:B = g0; dilute anti-sites reproduce the defect free energies (slope) with no quadratic energy term
    g0 = (0.75 * gA(Tk) + 0.25 * gB(Tk) - 0.12 + 2.0e-5 * Tk) * EV
    eA = np.interp(Tk, T, [-1.15, -1.30]) * EV
    eB = np.interp(Tk, T, [1.62, 1.66]) * EV
    ys = np.array([0.0, 0.01, 0.02])
    ptsA = np.array([[1.0, 0.0, y, 1 - y] for y in ys])       # y(A,B | A,B): A anti-sites on the B sublattice (fraction 0.25)
    ptsB = np.array([[1 - y, y, 0.0, 1.0] for y in ys])       # B anti-sites on the A sublattice (fraction 0.75)
    for pts, n_s, e in ((ptsA, 0.25, eA), (ptsB, 0.75, eB)):
        gm = calculate(db, ["AL", "LI", "VA"], "AL3LI", T=Tk, P=101325, N=1, points=pts).GM.values.ravel()
        ideal = np.array([R * Tk * n_s * (y * np.log(y) + (1 - y) * np.log(1 - y)) if y > 0 else 0.0 for y in ys])
        en = gm - ideal                                        # energy part
        assert float(en[0]) == pytest.approx(g0, abs=2.0)
        assert float(en[1] - en[0]) == pytest.approx(n_s * e * 0.01, rel=2e-3)          # dilute slope = site fraction x eps_d
        assert float(en[2] - 2 * en[1] + en[0]) == pytest.approx(0.0, abs=abs(n_s * e) * 2e-5)   # no y^2 (and no y^3) term for non-interacting defects: only the quartic wall
    far = calculate(db, ["AL", "LI", "VA"], "AL3LI", T=Tk, P=101325, N=1, points=np.array([[1.0, 0.0, 1.0, 0.0]])).GM.values.ravel()[0]
    assert float(far) == pytest.approx(gA(Tk) * EV + 500000.0, abs=2.0)                  # far end A:A = reference + penalty
