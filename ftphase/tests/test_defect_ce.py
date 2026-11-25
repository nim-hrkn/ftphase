"""ftphase.defect_ce: cluster expansion of the defects of one compound + Monte Carlo, on a synthetic B2 lattice model."""
import numpy as np
import pytest

icet = pytest.importorskip("icet")
pytest.importorskip("mchammer")

from ase import Atoms  # noqa: E402

from ftphase import defect_ce as dc  # noqa: E402

KB = 8.617333262e-5


def _b2(rep):
    return Atoms("AlNi", scaled_positions=[(0, 0, 0), (0.5, 0.5, 0.5)], cell=[2.88] * 3, pbc=True).repeat(rep)


def _cells(sc, plan, A="Al", B="Ni"):
    out = []
    for tag, la, lb in plan:
        at = sc.copy()
        for i in la:
            at[i].symbol = B
        for i in lb:
            at[i].symbol = A
        at.info["tag"] = tag; out.append(at)
    return out


def _model(cutoffs, seed=3):
    """A known Hamiltonian: random ECIs (per site) on the cluster space with ``cutoffs``.  (icet reduces B2 with both species allowed
    on both sites to its parent bcc lattice: one point term, the B2 order is a configuration.)"""
    from icet import ClusterExpansion, ClusterSpace
    cs = ClusterSpace(_b2((1, 1, 1)), cutoffs=cutoffs, chemical_symbols=[["Al", "Ni"]] * 2)
    return ClusterExpansion(cs, np.random.default_rng(seed).normal(0.0, 0.02, len(cs)))


def _ordering_model(half=0.40, field=0.01):
    """Point term + nearest-neighbour pair term only, scaled so that one anti-site costs ``half`` eV on average: B2 is the ground state
    and anti-sites of the same kind (same sublattice, never nearest neighbours) do not interact."""
    from icet import ClusterExpansion, ClusterSpace
    cs = ClusterSpace(_b2((1, 1, 1)), cutoffs=[3.0], chemical_symbols=[["Al", "Ni"]] * 2); assert len(cs) == 4
    small = _b2((2, 2, 2)); N = len(small); flip = small.copy(); flip[0].symbol = "Ni"
    unit = ClusterExpansion(cs, [0.0, 0.0, 1.0, 0.0]); h0 = N * (unit.predict(flip) - unit.predict(small))
    return ClusterExpansion(cs, [0.0, field, half / h0, 0.0])


def test_training_plan_samples_every_site_and_is_reproducible():
    sc = _b2((3, 3, 3)); plan = dc.training_plan(sc, "Al", "Ni", blocks=(3, 3, 3)); tags = [t for t, _, _ in plan]
    assert tags[0] == "perfect" and len(tags) == len(set(tags))
    assert {"single_B_on_A", "single_A_on_B"} <= set(tags) and any(t.startswith("pair_BA_AB") for t in tags) and any(t.startswith("regular_") for t in tags)
    sym = np.array(sc.get_chemical_symbols())
    for _, la, lb in plan:                                   # A sites become B, B sites become A, never the other way
        assert all(sym[i] == "Al" for i in la) and all(sym[i] == "Ni" for i in lb)
    assert plan == dc.training_plan(sc, "Al", "Ni", blocks=(3, 3, 3))


def test_structure_check_flags_a_change_of_shape_but_not_of_volume():
    sc = _b2((2, 2, 2)); vol = sc.copy(); vol.set_cell(sc.cell[:] * 1.03, scale_atoms=True)
    r = dc.structure_check(sc, vol, sc.cell[:]); assert not r["left_parent"] and r["strain_max"] < 1e-8
    tet = sc.copy(); tet.set_cell(sc.cell[:] @ np.diag([1.05, 1.05, 0.90]), scale_atoms=True)      # tetragonal distortion, c/a = 0.86
    r = dc.structure_check(sc, tet, sc.cell[:]); assert r["left_parent"] and r["strain_max"] > 0.02
    moved = sc.copy(); moved.positions[0] += (0.1, 0.0, 0.0)
    r = dc.structure_check(sc, moved, sc.cell[:]); assert not r["left_parent"] and r["disp_rms_A"] == pytest.approx(0.1 / np.sqrt(len(sc)), rel=1e-6)


def test_fit_recovers_a_known_pair_model_and_refuses_an_undetermined_one():
    sc = _b2((3, 3, 3)); cells = _cells(sc, dc.training_plan(sc, "Al", "Ni", rpair=3.0, rshell=3.0, n_random=(3, 4, 6, 8), blocks=(3, 3, 3)))
    truth = _model([3.0]); y = np.array([truth.predict(c) for c in cells])
    fit = dc.fit_expansion(cells, np.c_[y, 2 * y], ("Al", "Ni"), cutoffs=([3.0],), methods=("least-squares",))
    assert fit.method == "least-squares" and fit.cutoffs == [3.0] and fit.usable(0) and fit.usable(1)
    assert np.allclose(fit.rmse_train, 0.0, atol=1e-9) and np.allclose(fit.rmse_cv, 0.0, atol=1e-8)
    test = _cells(sc, [("t", [0, 4, 10, 20], [1, 3, 31])])[0]
    assert fit.expansion(0).predict(test) == pytest.approx(truth.predict(test), abs=1e-9) and fit.expansion(1).predict(test) == pytest.approx(2 * truth.predict(test), abs=1e-9)
    assert fit.x_range[0] < 0.5 < fit.x_range[1]
    # only the perfect cell and single anti-sites: every pair term is a combination of the point terms -> not determined
    few = [c for c in cells if c.info["tag"] in ("perfect", "single_B_on_A", "single_A_on_B")]
    with pytest.raises(ValueError, match="rank deficient"):
        dc.fit_expansion(few, [truth.predict(c) for c in few], ("Al", "Ni"), cutoffs=([3.0],))


def test_sgc_scan_and_branch_integration_reproduce_independent_anti_sites():
    """Nearest-neighbour ordering model: anti-sites of one kind are independent two-level systems, so x(mu) and G(x) - G(x0) are known."""
    ce = _ordering_model(); small = _b2((2, 2, 2)); N = len(small); T = 900.0
    one = lambda la, lb: N * (ce.predict(_cells(small, [("t", la, lb)])[0]) - ce.predict(small))
    g_ba, g_ab = one([0], []), one([], [1]); mid, half = dc.plateau(g_ba, g_ab); assert half == pytest.approx(0.40, abs=1e-9) and abs(mid) > 1e-3
    big = _b2((5, 5, 5)); scan = dc.sgc_scan(ce, big, T, mid, half, n_steps=8, extent=0.5, n_eq=20, n_av=60)
    p = lambda mu: 1.0 / (1.0 + np.exp((g_ba - mu) / (KB * T))); q = lambda mu: 1.0 / (1.0 + np.exp((g_ab + mu) / (KB * T)))
    x_exact = lambda mu: 0.5 * (p(mu) + 1.0 - q(mu))
    assert len(scan) == 16 and scan.antisite_fraction.max() < 0.1
    assert np.allclose(scan.x, x_exact(scan.dmu.to_numpy()), atol=0.006)
    x, g = dc.branch_free_energy(scan, 0.5)
    assert len(x) >= 12 and x.min() < 0.5 < x.max() and x.max() - x.min() > 0.03
    mu = np.linspace(mid - 0.5 * half, mid + 0.5 * half, 4001); xe = x_exact(mu); ge = np.concatenate([[0.0], np.cumsum(0.5 * (mu[1:] + mu[:-1]) * np.diff(xe))])
    ge -= np.interp(0.5, xe, ge)
    assert np.allclose(g, np.interp(x, xe, ge), atol=1.5e-3)       # eV per site; statistical noise of the short run
    assert g[np.argmin(abs(x - 0.5))] == pytest.approx(0.0, abs=1e-3)
    bad = scan.copy(); bad["antisite_fraction"] = 0.9               # a scan that leaves the compound at once gives no curve
    assert dc.branch_free_energy(bad, 0.5)[0].size == 0


def test_harvest_returns_configurations_beyond_the_thresholds():
    ce = _ordering_model(); small = _b2((3, 3, 3)); N = len(small)
    one = lambda la, lb: N * (ce.predict(_cells(small, [("t", la, lb)])[0]) - ce.predict(small))
    mid, half = dc.plateau(one([0], []), one([], [1]))
    got = dc.harvest(ce, small, 1500.0, mid, half, thresholds=(0.05, 0.15), n_steps=10, chunks=3)
    assert 1 <= len(got) <= 4 and all(h.info["antisite_fraction"] >= 0.05 and np.isfinite(h.info["predicted"]) for h in got)
    again = dc.harvest(ce, small, 1500.0, mid, half, thresholds=(0.05, 0.15), n_steps=10, chunks=3, known=got)
    assert len(again) == 0                                         # same seeds, same path: nothing new


def test_run_does_the_whole_chain_and_agrees_with_the_closed_form():
    """compute = the known ordering model at two 'temperatures' (the second column twice as stiff); no relaxation data."""
    ce = _ordering_model(); small = _b2((3, 3, 3)); N = len(small); calls = []
    def compute(at):
        calls.append(1); e = N * ce.predict(at); return {"values": [e, e]}
    kw = dict(blocks=(3, 3, 3), rpair=3.0, cutoffs=([3.0],), methods=("least-squares",), mc_supercell=_b2((4, 4, 4)), max_iterations=1,
              plan_kwargs={"rshell": 3.0, "n_random": (3, 4, 6, 8)}, scan_kwargs={"n_steps": 8, "extent": 0.5, "n_eq": 20, "n_av": 40}, harvest_kwargs={"thresholds": (0.05,), "n_steps": 6, "chunks": 2})
    res = dc.run(small, ("Al", "Ni"), compute, [900.0, 1200.0], **kw)
    assert res.x0 == 0.5 and res.fit.cutoffs == [3.0] and all(res.usable.values()) and np.allclose(res.fit.rmse_cv, 0.0, atol=1e-8)
    assert res.history and not res.excluded["left_parent"] and not res.excluded["rejected"]
    x, g = res.curves[900.0]; assert x.min() < 0.5 < x.max() and len(x) >= 10
    one = lambda la, lb: N * (ce.predict(_cells(small, [("t", la, lb)])[0]) - ce.predict(small)); g_ba, g_ab = one([0], []), one([], [1]); mid, half = dc.plateau(g_ba, g_ab)
    mu = np.linspace(mid - 0.5 * half, mid + 0.5 * half, 4001); xe = 0.5 * (1 / (1 + np.exp((g_ba - mu) / (KB * 900.0))) + 1 - 1 / (1 + np.exp((g_ab + mu) / (KB * 900.0))))
    ge = np.concatenate([[0.0], np.cumsum(0.5 * (mu[1:] + mu[:-1]) * np.diff(xe))]); ge -= np.interp(0.5, xe, ge)
    assert np.allclose(g, np.interp(x, xe, ge), atol=2e-3)
    v = res.values(900.0, [0.5, x.max() + 0.1], g0=-1.0); assert v[0] == pytest.approx(-1.0, abs=2e-3) and np.isnan(v[1])
    n1 = len(calls); res2 = dc.run(small, ("Al", "Ni"), compute, [900.0, 1200.0], cache=res.cells, **kw)        # resumed: nothing is computed again
    assert len(calls) == n1 and np.allclose(res2.curves[900.0][1], g)
    # a rejected cell and a cell that left the parent structure are excluded from the fit
    def compute2(at):
        e = N * ce.predict(at); rel = at.copy(); k = int(np.sum(np.array(at.get_chemical_symbols()) != np.array(small.get_chemical_symbols())))
        if k == 8:
            rel.set_cell(at.cell[:] @ np.diag([1.05, 1.05, 0.9]), scale_atoms=True)
        return {"values": [e, e], "relaxed": rel, "ok": k != 6}
    res3 = dc.run(small, ("Al", "Ni"), compute2, [900.0, 1200.0], **{**kw, "max_iterations": 0})
    nd = lambda t: len(res3.cells[t]["values"]) and int(round(abs(res3.cells[t]["x"] - 0.5) * N)) if not t.startswith("mixed") else sum(int(v) for v in t.split("_")[1:3])
    assert res3.excluded["left_parent"] and all(nd(t) == 8 for t in res3.excluded["left_parent"]) and res3.excluded["rejected"] and all(nd(t) == 6 for t in res3.excluded["rejected"])
    assert not set(res3.excluded["left_parent"]) & set(res3.excluded["rejected"]) and all(res3.usable.values())
