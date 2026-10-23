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

Rules carried over from the project workflow (docs/obsolete_workflow.html, section 4):
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


# --------------------------------------------------------------------------- thermal defects
DEFECT_KEYS = ("B_on_A", "Va_on_A", "A_on_B", "Va_on_B")


def wagner_schottky_free_energy(x_B, T, site_counts, defect_energies, g0_atom=0.0, vacancy=VACANCY, return_fractions=False):
    """Two-sublattice ordered phase A_a B_b with *thermal* point defects (Wagner-Schottky type).

    Defects: B anti-sites and vacancies on the A sublattice, A anti-sites and vacancies on the B
    sublattice, with (effective) formation free energies ``defect_energies`` = {'B_on_A': e,
    'Va_on_A': e, 'A_on_B': e, 'Va_on_B': e} in eV per defect, defined as the energy change of
    a crystal with a fixed number of lattice sites (raw supercell differences; a vacancy removes
    one atom, an anti-site swaps the species).  Missing keys mean the defect is not allowed.
    ``site_counts`` = (a, b) sites per formula unit; ``g0_atom`` the free energy per atom of the
    perfect crystal.  The site fractions minimise

        G/atom = [ (a+b) g0_atom + a (y_BA e_BA + y_VaA e_VaA) + b (y_AB e_AB + y_VaB e_VaB)
                   - T S_conf(y) ] / [ a (1 - y_VaA) + b (1 - y_VaB) ]

    under the composition constraint x_B(y) = x_B (eq. (E11), linear in the y's: one defect
    fraction is eliminated analytically and the remaining ones are optimised in log space; with
    two allowed defects this is a bounded one-dimensional minimisation), with S_conf from the
    sublattice ideal-mixing form (eq. (E10)).  At T -> 0 this reduces to the constitutional
    defects (the cheaper of the allowed defects on each side of stoichiometry); at finite T
    defect pairs (anti-site pairs, triple defects, Schottky pairs) appear also at stoichiometry,
    so G(x) has no cusp there.  Non-interacting (dilute) defects.

    Returns G per atom (eV) or, with ``return_fractions``, (G, site_fractions) where
    site_fractions = [{'A':..,'B':..,'Va':..}, {'A':..,'B':..,'Va':..}].
    """
    from scipy.optimize import minimize, minimize_scalar

    a, b = float(site_counts[0]), float(site_counts[1])
    T = float(T)
    kT = KB_EV * T
    e = {k: float(defect_energies[k]) for k in DEFECT_KEYS if k in defect_energies and defect_energies[k] is not None and np.isfinite(defect_energies[k])}
    if not e:
        raise ValueError("no allowed defects")
    x_B = float(x_B)
    x0 = b / (a + b)
    # composition constraint  a y_BA + b (1 - y_AB - y_VaB) - x [a (1 - y_VaA) + b (1 - y_VaB)] = 0, linear in y:
    #   c0 + sum_k c_k y_k = 0  with  c0 = b - x (a + b)
    coef = {"B_on_A": a, "Va_on_A": a * x_B, "A_on_B": -b, "Va_on_B": -b + b * x_B}
    c0 = b - x_B * (a + b)
    # slack defect (eliminated analytically): the constitutional defect of this side if allowed
    order = (["B_on_A", "Va_on_B", "A_on_B", "Va_on_A"] if x_B >= x0 else ["A_on_B", "Va_on_A", "B_on_A", "Va_on_B"])
    slack = next(k for k in order if k in e)
    free = [k for k in e if k != slack]

    def all_fractions(y_free):
        y = dict(zip(free, y_free))
        y[slack] = -(c0 + sum(coef[k] * y[k] for k in free)) / coef[slack]
        return y

    def gibbs_from(y):
        yBA, yVaA, yAB, yVaB = (y.get("B_on_A", 0.0), y.get("Va_on_A", 0.0), y.get("A_on_B", 0.0), y.get("Va_on_B", 0.0))
        sA = np.array([1.0 - yBA - yVaA, yBA, yVaA]); sB = np.array([1.0 - yAB - yVaB, yAB, yVaB])
        if (sA < 0).any() or (sB < 0).any():
            return 1e6                      # infeasible (the slack fraction left [0, 1]); finite so the scalar search stays well-defined
        nat = a * (1.0 - yVaA) + b * (1.0 - yVaB)
        E = (a + b) * g0_atom + a * (yBA * e.get("B_on_A", 0.0) + yVaA * e.get("Va_on_A", 0.0)) + b * (yAB * e.get("A_on_B", 0.0) + yVaB * e.get("Va_on_B", 0.0))
        S = -KB_EV * (a * float(np.sum(_xlogx(sA))) + b * float(np.sum(_xlogx(sB))))
        return (E - T * S) / nat

    if not free:
        y = all_fractions([])
        G = gibbs_from(y)
    else:
        def f(z):
            return gibbs_from(all_fractions(np.exp(z)))

        lo, hi = np.log(1e-16), np.log(0.5)
        if len(free) == 1:
            # scan for a bracket, then refine (the function is smooth and has a single minimum in z)
            zz = np.linspace(lo, hi, 161)
            vals = np.array([f(np.array([z])) for z in zz])
            i = int(np.nanargmin(vals))
            zl, zh = zz[max(i - 1, 0)], zz[min(i + 1, len(zz) - 1)]
            r = minimize_scalar(lambda z: f(np.array([z])), bounds=(zl, zh), method="bounded", options={"xatol": 1e-12, "maxiter": 500})
            z_best = np.array([r.x]) if r.fun <= vals[i] else np.array([zz[i]])
        else:
            best = None
            for z_init in (np.full(len(free), np.log(1e-6)), np.full(len(free), np.log(1e-3)), np.full(len(free), np.log(1e-10))):
                r = minimize(f, z_init, method="L-BFGS-B", bounds=[(lo, hi)] * len(free), options={"ftol": 1e-15, "gtol": 1e-12, "maxiter": 1000})
                if best is None or r.fun < best.fun:
                    best = r
            z_best = best.x
        y = all_fractions(np.exp(z_best))
        G = gibbs_from(y)
    if not np.isfinite(G):
        raise RuntimeError(f"Wagner-Schottky minimisation failed at x={x_B}, T={T}")
    if not return_fractions:
        return float(G)
    yBA, yVaA, yAB, yVaB = (y.get("B_on_A", 0.0), y.get("Va_on_A", 0.0), y.get("A_on_B", 0.0), y.get("Va_on_B", 0.0))
    sf = [{"A": 1.0 - yBA - yVaA, "B": yBA, vacancy: yVaA}, {"A": yAB, "B": 1.0 - yAB - yVaB, vacancy: yVaB}]
    return float(G), sf


def wagner_schottky_curve(xs, T, site_counts, defect_energies, g0_atom=0.0):
    """Vectorised :func:`wagner_schottky_free_energy` over compositions (eV/atom)."""
    return np.array([wagner_schottky_free_energy(float(x), T, site_counts, defect_energies, g0_atom) for x in np.asarray(xs, dtype=float)])


def defect_energies_from_cells(x_B, G_atom, n_atoms, site_counts, n_sites=None, tol=1e-6):
    """Effective defect (free) energies of a two-sublattice A_a B_b phase from sampled defect cells.

    Each cell is described by its composition ``x_B``, free energy per atom ``G_atom`` and atom
    count ``n_atoms``.  All cells must derive from the same supercell of ``n_sites`` lattice
    sites (default: the largest n_atoms; the stoichiometric cell has no vacancies).  A cell with
    n_atoms < n_sites holds vacancies (on the B sublattice when it is B-poor, else on A); a cell
    with n_atoms == n_sites and x off stoichiometry holds anti-sites (B on A when B-rich).  The
    raw defect energy of a cell is (G_atom n_atoms - g0 n_sites) / n_defects and the energy of a
    defect type is the least-squares average over its cells (through the origin), so cells with
    several defects contribute their mean interaction.  Returns
    (defect_energies dict for :func:`wagner_schottky_free_energy`, g0_atom, n_sites, table)
    where table lists (x, n_atoms, defect type, n_defects, raw energy per defect).
    """
    x = np.asarray(x_B, dtype=float); G = np.asarray(G_atom, dtype=float); n = np.asarray(n_atoms, dtype=float)
    a, b = float(site_counts[0]), float(site_counts[1])
    x0 = b / (a + b)
    n_sites = float(np.max(n)) if n_sites is None else float(n_sites)
    stoich = np.where((np.abs(x - x0) < tol) & (np.abs(n - n_sites) < 0.5))[0]
    if stoich.size == 0:
        raise ValueError("no stoichiometric cell (x = b/(a+b), no vacancies) among the rows")
    g0 = float(np.mean(G[stoich]))
    nB_ideal = x0 * n_sites
    rows, num, den = [], {}, {}
    for xi, gi, ni in zip(x, G, n):
        n_vac = int(round(n_sites - ni))
        nB = xi * ni
        if n_vac == 0 and abs(xi - x0) < tol:
            continue
        if n_vac > 0:
            key = "Va_on_B" if nB < nB_ideal - 0.5 * tol * n_sites else "Va_on_A"
            n_def = n_vac
        else:
            key = "B_on_A" if nB > nB_ideal else "A_on_B"
            n_def = int(round(abs(nB - nB_ideal)))
        if n_def <= 0:
            continue
        raw = (gi * ni - g0 * n_sites) / n_def
        rows.append({"x": float(xi), "n_atoms": float(ni), "defect": key, "n_defects": n_def, "energy_per_defect": float(raw)})
        num[key] = num.get(key, 0.0) + raw * n_def * n_def       # least squares of (G n - g0 N) = e * n_def
        den[key] = den.get(key, 0.0) + n_def * n_def
    energies = {k: num[k] / den[k] for k in num}
    return energies, g0, n_sites, rows
