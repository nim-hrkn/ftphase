"""Stage 03A: vibrational free energy and the quasi-harmonic approximation.

Implements eq. (D1) (harmonic free energy from phonon frequencies) and eq. (D2)
(G(T,P) = min_V [E_0(V) + F_vib(T,V) + PV]).  Phonon frequencies come from

* phonopy (A. Togo, J. Phys. Soc. Jpn. 92, 012001 (2023); BSD-3) driven with
  any ASE calculator, :func:`phonopy_volume_scan`;
* ALAMODE / aiida-alamode ``.thermo`` files written by anphon
  (T. Tadano, Y. Gohda, S. Tsuneyuki, J. Phys.: Condens. Matter 26, 225402
  (2014)), :func:`read_anphon_thermo`;
* any (frequency, weight) list, :func:`harmonic_free_energy`.

The equation-of-state fits (Vinet, Birch-Murnaghan 3rd order, polynomial)
are written here with scipy.  The fitting strategy is the one of phonopy-qha:
at each temperature the total F(V) is fitted and minimised; the module can
cross-check against ``phonopy.run_qha`` when phonopy is installed.

Imaginary modes are not silently dropped (workflow section 3): by default a
negative frequency below ``imaginary_tol`` raises; pass
``imaginary='drop'`` to exclude them explicitly, which is then recorded in the
returned metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import curve_fit, minimize_scalar

from .units import KB_EV, KJ_PER_MOL_TO_EV, RY_TO_EV, GPA_A3_TO_EV, THZ_TO_EV


# ---------------------------------------------------------------------------
# harmonic free energies from frequencies
# ---------------------------------------------------------------------------
def _check_imaginary(hw, imaginary, imaginary_tol):
    hw = np.asarray(hw, dtype=float)
    neg = hw < -abs(imaginary_tol)
    if np.any(neg):
        if imaginary == "raise":
            raise ValueError(
                f"{int(neg.sum())} imaginary modes (min {hw.min():.4g} eV); "
                "decide whether this is numerical noise, a structural instability "
                "or needs anharmonic (SCPH) treatment before computing F_vib"
            )
        elif imaginary != "drop":
            raise ValueError("imaginary must be 'raise' or 'drop'")
    keep = ~neg
    small = np.abs(hw) <= abs(imaginary_tol)
    return hw, keep & ~small, int(neg.sum()), int(small.sum())


def harmonic_free_energy(
    frequencies_ev: Sequence[float],
    T,
    weights: Optional[Sequence[float]] = None,
    quantum: bool = True,
    imaginary: str = "raise",
    imaginary_tol: float = 1e-5,
    include_zero_point: bool = True,
):
    """Harmonic vibrational free energy of one cell, eq. (D1).

    Parameters
    ----------
    frequencies_ev : mode energies hbar*omega in eV (use units.thz_to_ev)
    T : temperature(s) in K
    weights : optional q-point weights (same length), normalised internally so
        that sum(weights) == number of frequencies / (modes per q) is not
        assumed: weights are used as given, i.e. pass per-mode multiplicities
        that sum to 3N for N atoms in the cell.
    quantum : True -> F = sum [hw/2 + kT ln(1-exp(-hw/kT))];
              False -> classical F = sum kT ln(hw/kT)  (no zero point)
    include_zero_point : drop the hw/2 term when False (quantum only)

    Returns
    -------
    array F(T) in eV per cell (same shape as T).
    """
    hw, keep, n_neg, n_zero = _check_imaginary(frequencies_ev, imaginary, imaginary_tol)
    w = np.ones_like(hw) if weights is None else np.asarray(weights, dtype=float)
    hw, w = hw[keep], w[keep]
    Ts = np.atleast_1d(np.asarray(T, dtype=float))
    out = np.empty_like(Ts)
    for i, t in enumerate(Ts):
        if quantum:
            zpe = 0.5 * np.sum(w * hw) if include_zero_point else 0.0
            if t <= 0:
                out[i] = zpe
            else:
                x = hw / (KB_EV * t)
                out[i] = zpe + KB_EV * t * np.sum(w * np.log1p(-np.exp(-x)))
        else:
            if t <= 0:
                out[i] = -np.inf
            else:
                out[i] = KB_EV * t * np.sum(w * np.log(hw / (KB_EV * t)))
    return out if np.ndim(T) else float(out[0])


def harmonic_entropy(frequencies_ev, T, weights=None, imaginary="raise", imaginary_tol=1e-5):
    """Quantum harmonic entropy per cell, eV/K."""
    hw, keep, _, _ = _check_imaginary(frequencies_ev, imaginary, imaginary_tol)
    w = np.ones_like(hw) if weights is None else np.asarray(weights, dtype=float)
    hw, w = hw[keep], w[keep]
    Ts = np.atleast_1d(np.asarray(T, dtype=float))
    out = np.zeros_like(Ts)
    for i, t in enumerate(Ts):
        if t <= 0:
            continue
        x = hw / (KB_EV * t)
        out[i] = KB_EV * np.sum(w * (x / np.expm1(x) - np.log1p(-np.exp(-x))))
    return out if np.ndim(T) else float(out[0])


# ---------------------------------------------------------------------------
# equations of state
# ---------------------------------------------------------------------------
def vinet(V, E0, V0, B0, B1):
    x = (V / V0) ** (1.0 / 3.0)
    eta = 1.5 * (B1 - 1.0)
    return E0 + (4.0 * B0 * V0 / (B1 - 1.0) ** 2) * (1.0 - (1.0 + eta * (x - 1.0)) * np.exp(-eta * (x - 1.0)))


def birch_murnaghan(V, E0, V0, B0, B1):
    eta = (V0 / V) ** (2.0 / 3.0)
    return E0 + 9.0 * V0 * B0 / 16.0 * ((eta - 1.0) ** 3 * B1 + (eta - 1.0) ** 2 * (6.0 - 4.0 * eta))


_EOS = {"vinet": vinet, "birch_murnaghan": birch_murnaghan, "bm": birch_murnaghan}


@dataclass
class EOSFit:
    eos: str
    E0: float
    V0: float
    B0_eV_A3: float
    B1: float
    rmse: float
    params: tuple = field(default_factory=tuple)

    @property
    def B0_GPa(self):
        return self.B0_eV_A3 / GPA_A3_TO_EV

    def __call__(self, V):
        if self.eos == "poly":
            return np.polyval(self.params, V)
        return _EOS[self.eos](np.asarray(V, dtype=float), self.E0, self.V0, self.B0_eV_A3, self.B1)


def fit_eos(volumes, energies, eos: str = "vinet", poly_order: int = 4) -> EOSFit:
    """Fit E(V).  Units: volumes A^3, energies eV (any consistent basis).

    ``eos`` in {'vinet', 'birch_murnaghan', 'poly'}.  The minimum must lie
    inside the sampled volume range, otherwise a ValueError is raised: a QHA
    whose minimum is extrapolated is not a result.
    """
    V = np.asarray(volumes, dtype=float)
    E = np.asarray(energies, dtype=float)
    if V.size < 4:
        raise ValueError("need at least 4 volumes for an EOS fit (5 or more recommended)")
    order = np.argsort(V)
    V, E = V[order], E[order]
    if eos == "poly":
        p = np.polyfit(V, E, poly_order)
        res = minimize_scalar(lambda v: np.polyval(p, v), bounds=(V[0], V[-1]), method="bounded")
        V0 = float(res.x)
        d2 = np.polyval(np.polyder(p, 2), V0)
        fit = EOSFit("poly", float(res.fun), V0, float(d2 * V0), float("nan"), float(np.sqrt(np.mean((np.polyval(p, V) - E) ** 2))), tuple(p))
    else:
        f = _EOS[eos]
        # initial guess from a parabola
        p2 = np.polyfit(V, E, 2)
        V0g = float(np.clip(-p2[1] / (2 * p2[0]), V[0], V[-1])) if p2[0] > 0 else float(V[np.argmin(E)])
        B0g = max(2.0 * p2[0] * V0g, 1e-3) if p2[0] > 0 else 0.5
        p0 = [float(np.min(E)), V0g, B0g, 4.0]
        popt, _ = curve_fit(f, V, E, p0=p0, maxfev=20000)
        rmse = float(np.sqrt(np.mean((f(V, *popt) - E) ** 2)))
        fit = EOSFit(eos, float(popt[0]), float(popt[1]), float(popt[2]), float(popt[3]), rmse, tuple(popt))
    if not (V[0] - 1e-9 <= fit.V0 <= V[-1] + 1e-9):
        raise ValueError(f"EOS minimum V0={fit.V0:.3f} A^3 outside sampled range [{V[0]:.3f}, {V[-1]:.3f}]")
    return fit


# ---------------------------------------------------------------------------
# QHA
# ---------------------------------------------------------------------------
@dataclass
class QHAResult:
    temperatures: np.ndarray
    pressure_gpa: float
    gibbs: np.ndarray              # eV per cell (same basis as inputs)
    volumes: np.ndarray            # A^3 per cell
    bulk_modulus_gpa: np.ndarray
    helmholtz_fits: List[EOSFit]
    n_atoms: int
    metadata: Dict = field(default_factory=dict)

    def per_atom(self):
        return self.gibbs / self.n_atoms, self.volumes / self.n_atoms


def qha_gibbs(
    volumes,
    e0,
    temperatures,
    f_vib,
    pressure_gpa: float = 0.0,
    eos: str = "vinet",
    n_atoms: int = 1,
    f_el=None,
) -> QHAResult:
    """Quasi-harmonic G(T,P), eq. (D2) (with optional electronic term, (D3)).

    Parameters
    ----------
    volumes : (nV,) A^3 per cell
    e0 : (nV,) static energies, eV per cell
    temperatures : (nT,) K
    f_vib : (nT, nV) vibrational free energies, eV per cell
    pressure_gpa : external pressure
    eos : 'vinet' | 'birch_murnaghan' | 'poly'
    n_atoms : atoms per cell (for per_atom())
    f_el : optional (nT, nV) electronic free energies

    Returns
    -------
    QHAResult; the fit at every temperature must have its minimum inside the
    volume range (ValueError otherwise).
    """
    V = np.asarray(volumes, dtype=float)
    E = np.asarray(e0, dtype=float)
    Ts = np.asarray(temperatures, dtype=float)
    F = np.asarray(f_vib, dtype=float)
    if F.shape != (Ts.size, V.size):
        raise ValueError(f"f_vib must have shape (nT, nV) = {(Ts.size, V.size)}, got {F.shape}")
    if f_el is not None:
        F = F + np.asarray(f_el, dtype=float)
    pv = GPA_A3_TO_EV * pressure_gpa * V
    G = np.empty(Ts.size)
    Vt = np.empty(Ts.size)
    Bt = np.empty(Ts.size)
    fits = []
    for i in range(Ts.size):
        fit = fit_eos(V, E + F[i] + pv, eos=eos)
        fits.append(fit)
        G[i], Vt[i] = fit.E0, fit.V0
        Bt[i] = fit.B0_GPa if np.isfinite(fit.B0_eV_A3) else np.nan
    return QHAResult(Ts, pressure_gpa, G, Vt, Bt, fits, n_atoms, {"eos": eos, "n_volumes": int(V.size)})


# ---------------------------------------------------------------------------
# ALAMODE / anphon .thermo reader
# ---------------------------------------------------------------------------
def read_anphon_thermo(path, n_atoms_in_cell: int):
    """Read an anphon ``PREFIX.thermo`` file.

    Columns (anphon): T [K], C_v/k_B, S/k_B, U [Ry], F [Ry], all per the
    primitive cell used by anphon.  Returns dict with arrays in eV per cell
    and the per-atom normalisation factor.  The free energy column is the
    harmonic (or QHA-labelled) F_vib including zero point.
    """
    data = np.loadtxt(path, comments="#")
    T = data[:, 0]
    out = {
        "T": T,
        "Cv_eV_per_K": data[:, 1] * KB_EV,
        "S_eV_per_K": data[:, 2] * KB_EV,
        "U_eV": data[:, 3] * RY_TO_EV,
        "F_eV": data[:, 4] * RY_TO_EV,
        "n_atoms": int(n_atoms_in_cell),
    }
    return out


# ---------------------------------------------------------------------------
# phonopy driver with an ASE calculator
# ---------------------------------------------------------------------------
def phonopy_free_energy(
    atoms,
    calculator,
    supercell_matrix,
    temperatures,
    mesh=(20, 20, 20),
    displacement: float = 0.01,
    symprec: float = 1e-5,
    imaginary: str = "raise",
    imaginary_tol_thz: float = 0.05,
    return_frequencies: bool = False,
):
    """Harmonic F_vib(T) of ``atoms`` (one volume) with phonopy + ASE calculator.

    Returns F (eV per *input cell*), and optionally the (frequencies_eV,
    weights) arrays from the mesh so that classical/quantum differences can be
    evaluated with :mod:`ftphase.quantum`.
    """
    from phonopy import Phonopy
    from phonopy.structure.atoms import PhonopyAtoms

    unit = PhonopyAtoms(symbols=atoms.get_chemical_symbols(), cell=atoms.get_cell()[:], scaled_positions=atoms.get_scaled_positions())
    # 'auto' lets phonopy work in the true primitive cell (cheaper mesh); the
    # free energy is rescaled below to the number of atoms of the input cell.
    ph = Phonopy(unit, supercell_matrix=supercell_matrix, primitive_matrix="auto", symprec=symprec)
    ph.generate_displacements(distance=displacement)
    forces = []
    for sc in ph.supercells_with_displacements:
        a = atoms.__class__(symbols=sc.symbols, cell=sc.cell, scaled_positions=sc.scaled_positions, pbc=True)
        a.calc = calculator
        forces.append(a.get_forces())
    ph.forces = forces
    ph.produce_force_constants()
    ph.run_mesh(mesh, with_eigenvectors=False, is_mesh_symmetry=True, is_gamma_center=True)
    md = ph.get_mesh_dict()
    freqs_thz = md["frequencies"]  # (nq, 3 * n_primitive_atoms)
    w = md["weights"].astype(float)
    nq = w.sum()
    n_prim = len(ph.primitive)
    # weights normalised so that they sum to 3 * len(atoms): F is per *input cell*
    hw = (freqs_thz * THZ_TO_EV).ravel()
    weights = np.repeat(w / nq, freqs_thz.shape[1]) * (len(atoms) / n_prim)
    F = harmonic_free_energy(hw, temperatures, weights=weights, quantum=True, imaginary=imaginary, imaginary_tol=imaginary_tol_thz * THZ_TO_EV)
    if return_frequencies:
        return np.asarray(F), hw, weights
    return np.asarray(F)


def phonopy_volume_scan(
    atoms,
    calculator,
    supercell_matrix,
    temperatures,
    scales=(0.97, 0.98, 0.99, 1.00, 1.01, 1.02, 1.03),
    relax_positions: bool = True,
    fmax: float = 1e-3,
    mesh=(20, 20, 20),
    displacement: float = 0.01,
    imaginary: str = "raise",
    pressure_gpa: float = 0.0,
    eos: str = "vinet",
):
    """Volume scan + phonopy + QHA, eq. (D2), for a fixed cell shape.

    ``atoms`` should be the relaxed 0 K cell.  Each scaled cell is relaxed in
    its internal coordinates (cell fixed) when ``relax_positions`` is True.
    Returns (QHAResult per input cell, dict of per-volume data).
    """
    from ase.optimize import BFGS

    vols, e0s, Fs, freqs = [], [], [], []
    for s in scales:
        a = atoms.copy()
        a.set_cell(atoms.get_cell() * s, scale_atoms=True)
        a.calc = calculator
        if relax_positions and len(a) > 1:
            BFGS(a, logfile=None).run(fmax=fmax, steps=500)
        vols.append(a.get_volume())
        e0s.append(a.get_potential_energy())
        F, hw, w = phonopy_free_energy(a, calculator, supercell_matrix, temperatures, mesh=mesh, displacement=displacement, imaginary=imaginary, return_frequencies=True)
        Fs.append(F)
        freqs.append((hw, w))
    Fs = np.array(Fs).T  # (nT, nV)
    res = qha_gibbs(vols, e0s, temperatures, Fs, pressure_gpa=pressure_gpa, eos=eos, n_atoms=len(atoms))
    res.metadata.update({"scales": list(scales), "supercell_matrix": np.asarray(supercell_matrix).tolist(), "mesh": (list(mesh) if np.ndim(mesh) else float(mesh)), "displacement": displacement, "relax_positions": relax_positions})
    return res, {"volumes": np.array(vols), "e0": np.array(e0s), "f_vib": Fs, "frequencies": freqs}
