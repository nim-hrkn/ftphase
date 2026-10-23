import numpy as np
import pytest

from ftphase.units import KB_EV, RY_TO_EV, THZ_TO_EV
from ftphase.qha import harmonic_free_energy, harmonic_entropy, fit_eos, vinet, qha_gibbs, read_anphon_thermo
from ftphase.quantum import quantum_minus_classical, wigner_kirkwood_leading, lift_classical_to_quantum


def test_einstein_crystal_quantum_and_classical():
    hw = 0.03  # eV (~7.3 THz)
    T = np.array([1.0, 300.0, 1500.0])
    F = harmonic_free_energy([hw, hw, hw], T)
    exact = 3 * (hw / 2 + KB_EV * T * np.log1p(-np.exp(-hw / (KB_EV * T))))
    assert np.allclose(F, exact)
    Fc = harmonic_free_energy([hw, hw, hw], T, quantum=False)
    assert np.allclose(Fc, 3 * KB_EV * T * np.log(hw / (KB_EV * T)))
    # T=0 -> zero point energy
    assert abs(harmonic_free_energy([hw], 0.0) - hw / 2) < 1e-15
    # entropy consistent with -dF/dT (finite difference)
    dT = 1e-2
    S_fd = -(harmonic_free_energy([hw], 300 + dT) - harmonic_free_energy([hw], 300 - dT)) / (2 * dT)
    assert abs(harmonic_entropy([hw], 300.0) - S_fd) < 1e-9


def test_imaginary_modes_raise_unless_dropped():
    with pytest.raises(ValueError):
        harmonic_free_energy([0.03, -0.01], 300.0)
    F = harmonic_free_energy([0.03, -0.01], 300.0, imaginary="drop")
    assert abs(F - harmonic_free_energy([0.03], 300.0)) < 1e-15


def test_quantum_correction_limits():
    hw = np.array([0.02, 0.03, 0.04])
    # T -> 0: F_cl = kT sum ln(hw/kT) -> 0, so dF -> zero-point energy
    zpe = hw.sum() / 2
    assert abs(quantum_minus_classical(hw, 1.0) - zpe) / zpe < 0.05
    assert abs(quantum_minus_classical(hw, 0.1) - zpe) / zpe < 0.01
    # high T: dF -> Wigner-Kirkwood leading term sum (hw)^2/(24 kT)
    T = 5000.0
    assert abs(quantum_minus_classical(hw, T) - wigner_kirkwood_leading(hw, T)) / wigner_kirkwood_leading(hw, T) < 0.02
    # lift/lower are inverse operations
    G = np.array([-3.0])
    assert np.allclose(lift_classical_to_quantum(G, hw, 800.0) - quantum_minus_classical(hw, 800.0), G)


def test_eos_fit_recovers_parameters():
    V = np.linspace(14, 20, 9)
    E = vinet(V, -3.7, 16.6, 0.5, 4.5)
    f = fit_eos(V, E, eos="vinet")
    assert abs(f.V0 - 16.6) < 1e-6 and abs(f.E0 + 3.7) < 1e-8 and abs(f.B0_eV_A3 - 0.5) < 1e-6 and abs(f.B1 - 4.5) < 1e-4
    fb = fit_eos(V, E, eos="birch_murnaghan")
    assert abs(fb.V0 - 16.6) < 0.05
    with pytest.raises(ValueError):
        fit_eos(V, vinet(V, -3.7, 25.0, 0.5, 4.5))  # minimum outside the range


def test_qha_quadratic_analytic():
    # E0 = K/2 (V-V0)^2, Fvib = c T (V - V0): G(T) = -(cT)^2/(2K), V(T) = V0 - cT/K
    K, V0, c = 0.5, 16.0, -1e-4
    V = np.linspace(14, 18, 9)
    T = np.array([0.0, 300.0, 900.0])
    E0 = 0.5 * K * (V - V0) ** 2
    F = np.array([c * t * (V - V0) for t in T])
    res = qha_gibbs(V, E0, T, F, eos="poly")
    assert np.allclose(res.gibbs, -(c * T) ** 2 / (2 * K), atol=1e-10)
    assert np.allclose(res.volumes, V0 - c * T / K, atol=1e-6)
    # pressure shifts the minimum: dG/dP = V
    P = 1.0
    resP = qha_gibbs(V, E0, T, F, eos="poly", pressure_gpa=P)
    from ftphase.units import GPA_A3_TO_EV
    assert np.allclose(resP.volumes, V0 - (c * T + GPA_A3_TO_EV * P) / K, atol=1e-6)


def test_anphon_reader(anphon_thermo):
    d = read_anphon_thermo(anphon_thermo, n_atoms_in_cell=2)
    assert d["T"][0] == 0.0 and d["F_eV"][0] > 0  # zero point energy
    # F(0) = U(0) and F decreases with T
    assert abs(d["F_eV"][0] - d["U_eV"][0]) < 1e-12
    assert np.all(np.diff(d["F_eV"]) <= 1e-12)
    # S(T) = (U-F)/T consistent with the S column
    i = 10
    assert abs((d["U_eV"][i] - d["F_eV"][i]) / d["T"][i] - d["S_eV_per_K"][i]) < 1e-7


def test_phonopy_free_energy_is_per_input_cell():
    pytest.importorskip("phonopy")
    from ase.build import bulk
    from ase.calculators.emt import EMT
    from ftphase.qha import phonopy_free_energy
    T = [300.0, 900.0]
    prim = bulk("Al", "fcc", a=4.05)
    conv = bulk("Al", "fcc", a=4.05, cubic=True)
    Fp, hwp, wp = phonopy_free_energy(prim, EMT(), np.diag([3, 3, 3]), T, mesh=(12, 12, 12), return_frequencies=True)
    Fc, hwc, wc = phonopy_free_energy(conv, EMT(), np.diag([2, 2, 2]), T, mesh=(12, 12, 12), return_frequencies=True)
    # weights sum to 3N of the input cell
    assert abs(wp.sum() - 3 * len(prim)) < 1e-9 and abs(wc.sum() - 3 * len(conv)) < 1e-9
    # per-atom free energies agree (different supercells -> small differences)
    assert np.allclose(Fp / len(prim), Fc / len(conv), atol=2e-3)
    # the quantum-classical difference at 300 K for Al is a few meV/atom (not sub-meV)
    from ftphase.quantum import quantum_minus_classical
    dF = quantum_minus_classical(hwc, 300.0, weights=wc) / len(conv)
    assert 1e-3 < dF < 1e-2
