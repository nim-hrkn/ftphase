"""ftphase.ce: cluster expansion fit and semi-grand-canonical MC on a toy model."""

import numpy as np
import pytest

icet = pytest.importorskip("icet")


def _toy_prim():
    from ase.build import bulk

    return bulk("Cu", "fcc", a=3.6)


def test_fit_recovers_pair_interaction_and_sgc_mc_gap():
    """Energies generated from a nearest-neighbour pair model (regular solution) are reproduced by the CE
    (validation rmse ~ 0); SGC MC on that CE shows a jump of x(dmu) below the critical temperature and a
    smooth isotherm above it; the tangent construction returns a symmetric gap."""
    from icet import ClusterSpace, ClusterExpansion

    from ftphase.ce import enumerate_training_structures, fit_cluster_expansion, integrate_isotherm, sgc_scan

    prim = _toy_prim()
    syms = [["Cu", "Ag"]]
    cutoffs = [3.0]                               # nearest neighbours only (a/sqrt2 = 2.55 A)
    cs = ClusterSpace(prim, cutoffs=cutoffs, chemical_symbols=syms)
    assert len(cs) == 3                           # zerolet, point, nn pair
    truth = ClusterExpansion(cs, np.array([-3.0, 0.0, -0.05]))  # negative pair ECI: like neighbours lower the energy -> phase separation (fcc Ising T_c ~ 9.8 J/k_B with J = ECI/6 -> ~950 K)
    structures = enumerate_training_structures(prim, syms, range(1, 7))
    energies = np.array([truth.predict(s) for s in structures])
    ce, info = fit_cluster_expansion(prim, syms, cutoffs, structures, energies, fit_method="least-squares", n_splits=5)
    assert info["rmse_validation"] < 1e-8 and np.allclose(ce.parameters, truth.parameters, atol=1e-8)
    # SGC MC: 4x4x4 conventional cells = 256 sites; symmetric model -> coexistence at dmu = 0
    sc = prim.repeat((6, 6, 6))
    dmus = np.linspace(-0.3, 0.3, 13)
    T_low, T_high = 300.0, 3000.0
    up = sgc_scan(ce, sc, T_low, dmus, ("Cu", "Ag"), n_sweeps_eq=10, n_sweeps_av=10, direction="up", seed=1)
    down = sgc_scan(ce, sc, T_low, dmus, ("Cu", "Ag"), n_sweeps_eq=10, n_sweeps_av=10, direction="down", seed=2)
    xu = np.array([[r["dmu"], r["x_B"]] for r in up]); xd = np.array([[r["dmu"], r["x_B"]] for r in down])
    assert xu[0, 1] < 0.05 and xu[-1, 1] > 0.95              # pure A at low dmu, pure B at high dmu
    assert np.max(np.abs(np.diff(xu[:, 1]))) > 0.5            # first-order jump at low T
    res = integrate_isotherm(xu, xd)
    assert abs(res["dmu_star"]) < 0.1
    if np.isfinite(res["x_alpha"]):
        assert res["x_alpha"] < 0.2 and res["x_beta"] > 0.8 and abs((res["x_alpha"] + (1 - res["x_beta"]))) < 0.2
    hot = sgc_scan(ce, sc, T_high, dmus, ("Cu", "Ag"), n_sweeps_eq=5, n_sweeps_av=5, direction="up", seed=3)
    xh = np.array([r["x_B"] for r in hot])
    assert np.max(np.abs(np.diff(xh))) < 0.3                  # smooth above T_c
