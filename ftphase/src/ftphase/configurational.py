"""Stage 04A: configurational entropy and free energy.

Implements, per atom unless stated otherwise,

* ideal mixing on one sublattice, eq. (E1)/(E14): s = -k_B sum_i x_i ln x_i;
* the exact counting entropy, eq. (E9): S = k_B ln(N!/prod N_i!);
* multi-sublattice (compound energy formalism) entropy with vacancies,
  eq. (E10)-(E12): s = -k_B sum_s a_s sum_i y_i^(s) ln y_i^(s) with
  a_s = n_s / sum_t n_t (1 - y_Va^(t)) for the per-atom basis;
* configurational free energy from a density of states g(E), eq. (E13):
  F_conf = -k_B T ln sum_E g(E) exp(-E/k_B T), as produced by Wang-Landau
  sampling in icet (mchammer.ensembles.WangLandauEnsemble, Ångqvist et al.,
  Adv. Theory Simul. 2, 1900015 (2019)) or smol (Barroso-Luque et al., JOSS 7,
  4504 (2022)).

The multi-sublattice form follows the compound energy formalism as written in
pycalphad's Model.ideal_mixing_energy (Otis & Liu, J. Open Res. Softw. 5, 1
(2017)), i.e. the same convention a TDB file uses, so that values can later be
compared with pycalphad.

Rules carried over from the project workflow (docs/workflow.html, section 4):
never apply the all-site ideal term to an ordered phase; never add an ideal
term to a free energy that already contains configurational statistics
(MC/TI, liquid TI with UFM reference); record which term was added.
"""

from __future__ import annotations

from math import lgamma
from typing import Dict, Iterable, List, Mapping, Sequence

import numpy as np
from scipy.special import logsumexp

from .units import KB_EV

VACANCY = "Va"


def _xlogx(y):
    y = np.asarray(y, dtype=float)
    out = np.zeros_like(y)
    m = y > 0
    out[m] = y[m] * np.log(y[m])
    return out


def ideal_entropy(x, per="atom"):
    """Ideal mixing entropy of a random single-sublattice solution.

    Parameters
    ----------
    x : float or sequence of floats
        A single number is the mole fraction of B in a binary A_(1-x)B_x,
        eq. (E1).  A sequence is the full composition vector (must sum to 1),
        eq. (E14).
    per : 'atom' (eV/(atom K)) or 'mol' (J/(mol-atoms K))

    Returns
    -------
    float
    """
    xs = np.atleast_1d(np.asarray(x, dtype=float))
    if xs.size == 1:
        xs = np.array([1.0 - xs[0], xs[0]])
    if np.any(xs < -1e-12) or abs(xs.sum() - 1.0) > 1e-8:
        raise ValueError("composition vector must be non-negative and sum to 1")
    s = -KB_EV * float(np.sum(_xlogx(xs)))
    if per == "mol":
        from .units import EV_TO_J_PER_MOL
        return s * EV_TO_J_PER_MOL
    return s


def ideal_mixing_free_energy(x, T, per="atom"):
    """-T s_ideal, i.e. the term added in eq. (E2). Negative for 0<x<1."""
    return -np.asarray(T, dtype=float) * ideal_entropy(x, per=per)


def exact_entropy(counts: Sequence[int], per="atom"):
    """Exact counting entropy, eq. (E9), S/N with S = k_B ln(N!/prod N_i!)."""
    counts = [int(c) for c in counts]
    N = sum(counts)
    if N <= 0:
        raise ValueError("need at least one site")
    lnomega = lgamma(N + 1) - sum(lgamma(c + 1) for c in counts)
    s = KB_EV * lnomega / N
    if per == "mol":
        from .units import EV_TO_J_PER_MOL
        return s * EV_TO_J_PER_MOL
    return s


def sublattice_entropy(
    site_fractions: Sequence[Mapping[str, float]],
    site_counts: Sequence[float],
    basis: str = "atom",
    vacancy: str = VACANCY,
):
    """Configurational entropy of a multi-sublattice phase, eq. (E10)-(E12).

    Parameters
    ----------
    site_fractions : list of dict
        One dict per sublattice mapping species -> site fraction y_i^(s).
        Vacancies are the species ``vacancy`` ('Va' by default).  Each dict
        must sum to 1.
    site_counts : list of float
        Sites per formula unit n_s for each sublattice.
    basis : 'atom' | 'formula' | 'site'
        'atom'   : per real atom, a_s = n_s / sum_t n_t (1 - y_Va^(t))  (E12)
        'formula': per formula unit, a_s = n_s
        'site'   : per lattice site (vacancies included), a_s = n_s / sum n_t

    Returns
    -------
    float : entropy in eV/K per chosen basis.
    """
    if len(site_fractions) != len(site_counts):
        raise ValueError("site_fractions and site_counts must have the same length")
    n = np.asarray(site_counts, dtype=float)
    for yd in site_fractions:
        tot = sum(yd.values())
        if abs(tot - 1.0) > 1e-8:
            raise ValueError(f"site fractions must sum to 1, got {tot}")
        if any(v < -1e-12 for v in yd.values()):
            raise ValueError("negative site fraction")
    if basis == "formula":
        a = n
    elif basis == "site":
        a = n / n.sum()
    elif basis == "atom":
        n_atoms = sum(ns * (1.0 - yd.get(vacancy, 0.0)) for ns, yd in zip(n, site_fractions))
        if n_atoms <= 0:
            raise ValueError("no real atoms")
        a = n / n_atoms
    else:
        raise ValueError("basis must be 'atom', 'formula' or 'site'")
    s = 0.0
    for a_s, yd in zip(a, site_fractions):
        s += a_s * float(np.sum(_xlogx(np.array(list(yd.values()), dtype=float))))
    return -KB_EV * s


def composition_from_site_fractions(
    site_fractions: Sequence[Mapping[str, float]],
    site_counts: Sequence[float],
    vacancy: str = VACANCY,
) -> Dict[str, float]:
    """Atomic composition from site fractions, eq. (E11); vacancies excluded."""
    n = np.asarray(site_counts, dtype=float)
    tot = {}
    for ns, yd in zip(n, site_fractions):
        for sp, y in yd.items():
            if sp == vacancy:
                continue
            tot[sp] = tot.get(sp, 0.0) + ns * y
    natoms = sum(tot.values())
    return {sp: v / natoms for sp, v in tot.items()}


def sublattice_mixing_free_energy(site_fractions, site_counts, T, basis="atom", vacancy=VACANCY):
    """-T s_conf for the multi-sublattice model (eV per basis)."""
    return -np.asarray(T, dtype=float) * sublattice_entropy(site_fractions, site_counts, basis, vacancy)


def b32_antisite_site_fractions(x_B: float, stoich_x: float = 0.5):
    """Helper for an AB ordered phase (e.g. B32 AlLi) made off-stoichiometric
    by anti-site atoms only.  Returns (site_fractions, site_counts) for a
    two-sublattice model (A)(B) with n_s = 1/2 each, so that the overall
    B fraction equals ``x_B``.  For x_B < 1/2, A sits on the B sublattice;
    for x_B > 1/2, B on the A sublattice.  No vacancies.
    """
    if not 0.0 <= x_B <= 1.0:
        raise ValueError("x_B must be in [0,1]")
    if x_B <= stoich_x:
        yB_on_B = x_B / stoich_x  # fraction of B sublattice occupied by B
        sf = [{"A": 1.0, "B": 0.0}, {"A": 1.0 - yB_on_B, "B": yB_on_B}]
    else:
        yA_on_A = (1.0 - x_B) / (1.0 - stoich_x)
        sf = [{"A": yA_on_A, "B": 1.0 - yA_on_A}, {"A": 0.0, "B": 1.0}]
    return sf, [stoich_x, 1.0 - stoich_x]


def b2_triple_defect_site_fractions(x_B: float, stoich_x: float = 0.5):
    """Site fractions of an AB (B2-type) phase with the *triple-defect* constitution
    (e.g. NiAl with B = Ni): B-rich side by B anti-sites on the A sublattice, A-rich
    side by vacancies on the B sublattice (no A anti-sites).  Returns
    (site_fractions, site_counts) for :func:`sublattice_entropy` with
    ``vacancy='Va'`` and ``basis='atom'``; the vacancy fraction y_Va on the B
    sublattice follows from x_B = (1 - y_Va) / (2 - y_Va).
    """
    if not 0.0 < x_B < 1.0:
        raise ValueError("x_B must be in (0,1)")
    if x_B >= stoich_x:
        return b32_antisite_site_fractions(x_B, stoich_x)
    y_va = (1.0 - 2.0 * x_B) / (1.0 - x_B)          # vacancies on the B sublattice
    sf = [{"A": 1.0, "B": 0.0}, {"B": 1.0 - y_va, "Va": y_va}]
    return sf, [stoich_x, 1.0 - stoich_x]


def free_energy_from_density_of_states(energies, ln_dos, T, per_atoms: int = 1):
    """Configurational free energy and entropy from a density of states, eq. (E13).

    Parameters
    ----------
    energies : array (eV, total for the sampled cell)
    ln_dos : array, ln g(E) (any additive constant is irrelevant for S and
        for F up to k_B T * const; pass the normalised ln g if absolute F is
        needed, e.g. with ln sum g = N ln 2 for a binary spin system)
    T : float or array of temperatures (K)
    per_atoms : divide results by this number of atoms

    Returns
    -------
    dict with 'F' (eV/atom), 'S' (eV/(atom K)), 'U' (eV/atom), arrays over T.
    Note: F here contains the configurational energy <E>; do not add E_0 again.
    """
    E = np.asarray(energies, dtype=float)
    lng = np.asarray(ln_dos, dtype=float)
    Ts = np.atleast_1d(np.asarray(T, dtype=float))
    F = np.empty_like(Ts)
    U = np.empty_like(Ts)
    for i, t in enumerate(Ts):
        if t <= 0:
            F[i] = U[i] = E.min()
            continue
        beta = 1.0 / (KB_EV * t)
        lnZ = logsumexp(lng - beta * E)
        w = np.exp(lng - beta * E - lnZ)
        F[i] = -KB_EV * t * lnZ
        U[i] = float(np.sum(w * E))
    S = np.where(Ts > 0, (U - F) / np.where(Ts > 0, Ts, 1.0), 0.0)
    return {"T": Ts, "F": F / per_atoms, "S": S / per_atoms, "U": U / per_atoms}


def wang_landau_free_energy_icet(data_container, T, per_atoms: int = 1, fill_factor_limit=None):
    """Convenience adapter for icet Wang-Landau output.

    ``data_container`` is the ``mchammer.DataContainer`` (or a list of them,
    for a binned run) of a ``WangLandauEnsemble``.  Uses
    ``mchammer.get_density_of_states_wl`` (icet >= 2) and then eq. (E13).
    Requires icet.
    """
    from mchammer import get_density_of_states_wl  # type: ignore

    dcs = data_container if isinstance(data_container, (list, tuple)) else [data_container]
    df, _ = get_density_of_states_wl(dcs, fill_factor_limit=fill_factor_limit)
    return free_energy_from_density_of_states(df["energy"].to_numpy(), np.log(df["density"].to_numpy()), T, per_atoms)
