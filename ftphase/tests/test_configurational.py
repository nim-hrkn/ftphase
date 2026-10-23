import numpy as np
import pytest

from ftphase.units import KB_EV, EV_TO_J_PER_MOL
from ftphase.configurational import (
    ideal_entropy, ideal_mixing_free_energy, exact_entropy, sublattice_entropy,
    composition_from_site_fractions, b32_antisite_site_fractions,
    free_energy_from_density_of_states,
)


def test_ideal_binary_matches_workflow_example():
    # docs/workflow.html eq. (E3)-(E8): fcc-Al0.9Li0.1
    s = ideal_entropy(0.1)
    assert abs(s - 2.80135e-5) < 1e-9
    assert abs(ideal_entropy(0.1, per="mol") - 2.70289) < 1e-4
    assert abs(ideal_mixing_free_energy(0.1, 1000.0) + 0.0280135) < 1e-6
    assert ideal_entropy(0.0) == 0.0 and ideal_entropy(1.0) == 0.0


def test_ideal_quaternary_equiatomic_is_kln4():
    # eq. (E15)-(E17)
    s = ideal_entropy([0.25, 0.25, 0.25, 0.25])
    assert abs(s - KB_EV * np.log(4)) < 1e-12
    assert abs(s * EV_TO_J_PER_MOL - 11.52629) < 1e-3


def test_exact_counting_converges_to_stirling():
    # eq. (E9) vs (E1) for a large cell
    N = 100000
    s_exact = exact_entropy([int(0.9 * N), int(0.1 * N)])
    assert abs(s_exact - ideal_entropy(0.1)) / ideal_entropy(0.1) < 1e-3
    # small cell: exact counting is smaller than Stirling (finite-size)
    assert exact_entropy([29, 3]) < ideal_entropy(3 / 32)


def test_sublattice_reduces_to_ideal_for_one_sublattice():
    sf = [{"A": 0.7, "B": 0.3}]
    assert abs(sublattice_entropy(sf, [1.0]) - ideal_entropy(0.3)) < 1e-15
    # two identical sublattices with the same occupation = ideal on all sites
    sf2 = [{"A": 0.7, "B": 0.3}, {"A": 0.7, "B": 0.3}]
    assert abs(sublattice_entropy(sf2, [0.5, 0.5]) - ideal_entropy(0.3)) < 1e-15


def test_b32_antisite_model_is_half_of_all_site_ideal():
    # Al-rich B32: Al on the Li sublattice only -> s = (1/2) * s_ideal(y) with y the
    # fraction of Li on that sublattice; stoichiometric compound -> 0.
    sf, nc = b32_antisite_site_fractions(0.5)
    assert sublattice_entropy(sf, nc) == 0.0
    x = 0.4
    sf, nc = b32_antisite_site_fractions(x)
    y = x / 0.5  # Li fraction on the Li sublattice
    expected = 0.5 * ideal_entropy(y)
    assert abs(sublattice_entropy(sf, nc) - expected) < 1e-15
    # the all-site ideal term that the workshop tutorial used is larger
    assert ideal_entropy(x) > sublattice_entropy(sf, nc)
    # composition is reproduced, eq. (E11)
    comp = composition_from_site_fractions(sf, nc)
    assert abs(comp["B"] - x) < 1e-12


def test_vacancy_basis_and_composition():
    # (A)1 (B,Va)1 with 20% vacancies on the second sublattice
    sf = [{"A": 1.0}, {"B": 0.8, "Va": 0.2}]
    nc = [1.0, 1.0]
    comp = composition_from_site_fractions(sf, nc)
    assert abs(comp["A"] - 1 / 1.8) < 1e-12 and abs(comp["B"] - 0.8 / 1.8) < 1e-12
    s_atom = sublattice_entropy(sf, nc, basis="atom")
    s_formula = sublattice_entropy(sf, nc, basis="formula")
    # per atom = per formula / number of real atoms (1.8), eq. (E12)
    assert abs(s_atom - s_formula / 1.8) < 1e-15
    assert s_formula > 0


def test_density_of_states_two_level():
    # two-level system: g(0)=1, g(eps)=1 -> F = -kT ln(1+exp(-eps/kT))
    eps = 0.05
    T = np.array([100.0, 500.0, 2000.0])
    out = free_energy_from_density_of_states([0.0, eps], [0.0, 0.0], T)
    F_exact = -KB_EV * T * np.log1p(np.exp(-eps / (KB_EV * T)))
    assert np.allclose(out["F"], F_exact, atol=1e-12)
    # high T: S -> kB ln 2
    assert abs(out["S"][-1] - KB_EV * np.log(2)) < 2e-6


def test_invalid_inputs():
    with pytest.raises(ValueError):
        ideal_entropy([0.5, 0.6])
    with pytest.raises(ValueError):
        sublattice_entropy([{"A": 0.5, "B": 0.4}], [1.0])


def test_b2_triple_defect_site_fractions():
    import numpy as np
    from ftphase.configurational import b2_triple_defect_site_fractions, sublattice_entropy, composition_from_site_fractions
    # Al-rich NiAl (x_Ni = 0.48): Ni vacancies only; composition of the model must reproduce x_Ni
    sf, nc = b2_triple_defect_site_fractions(0.48)
    assert sf[0] == {"A": 1.0, "B": 0.0} and abs(sf[1]["Va"] - (1 - 2 * 0.48) / (1 - 0.48)) < 1e-12
    comp = composition_from_site_fractions(sf, nc, vacancy="Va")
    assert abs(comp["B"] - 0.48) < 1e-12
    s = sublattice_entropy(sf, nc, basis="atom", vacancy="Va")
    assert s > 0
    # stoichiometric: no entropy; Ni-rich: anti-site branch
    assert sublattice_entropy(*b2_triple_defect_site_fractions(0.5), basis="atom", vacancy="Va") < 1e-12
    sf2, _ = b2_triple_defect_site_fractions(0.52)
    assert sf2[0]["B"] > 0 and "Va" not in sf2[1]
