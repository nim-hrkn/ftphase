"""Stage 01: candidate phases and MLIP validation at 0 K.

* :func:`relax` relaxes positions and (optionally) the cell with ASE
  (FrechetCellFilter + BFGS), and reports whether the space group changed,
  so that a structure that transformed is not registered under its original
  name (workflow section 1).
* :func:`formation_energies` and :func:`hull_0K` build the 0 K convex hull of
  a binary from per-atom energies, with the same monotone-chain routine used
  at finite T (:mod:`ftphase.equilibrium`), and cross-check against
  pymatgen's PhaseDiagram (S. P. Ong et al., Comput. Mater. Sci. 68, 314
  (2013)) when installed.
* :func:`compare_ground_states` flags known ground states that are not on
  the MLIP hull (and by how much) instead of replacing them silently.
* :func:`eos_scan` is the E(V) scan (Vinet fit) that doubles as the E_0(V)
  input of the QHA.
* :func:`melting_check_inputs` writes a calphy ``melting_temperature`` input
  for a pure element so that the MLIP's melting point can be compared with
  experiment (calphy mode of Menon et al. 2021).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from ase import Atoms

from .equilibrium import lower_hull_2d
from .qha import fit_eos, EOSFit


@dataclass
class RelaxResult:
    atoms: Atoms
    energy_per_atom: float
    volume_per_atom: float
    spacegroup_before: str
    spacegroup_after: str
    converged: bool
    steps: int

    @property
    def transformed(self) -> bool:
        return self.spacegroup_before != self.spacegroup_after


def _spacegroup(atoms: Atoms, symprec: float) -> str:
    try:
        import spglib

        cell = (atoms.get_cell()[:], atoms.get_scaled_positions(), atoms.get_atomic_numbers())
        return spglib.get_spacegroup(cell, symprec=symprec) or "?"
    except Exception:
        return "?"


def relax(atoms: Atoms, calculator, fmax: float = 1e-3, steps: int = 1000, cell: bool = True, hydrostatic: bool = False, symprec: float = 1e-3) -> RelaxResult:
    from ase.filters import FrechetCellFilter
    from ase.optimize import BFGS

    a = atoms.copy()
    a.calc = calculator
    sg0 = _spacegroup(a, symprec)
    target = FrechetCellFilter(a, hydrostatic_strain=hydrostatic) if cell else a
    opt = BFGS(target, logfile=None)
    conv = opt.run(fmax=fmax, steps=steps)
    return RelaxResult(a, a.get_potential_energy() / len(a), a.get_volume() / len(a), sg0, _spacegroup(a, symprec), bool(conv), opt.get_number_of_steps())


def formation_energies(x: Sequence[float], e: Sequence[float]) -> np.ndarray:
    """e_f(x) = e(x) - [(1-x) e(0) + x e(1)] using the lowest energy at x=0 and x=1."""
    x = np.asarray(x, dtype=float)
    e = np.asarray(e, dtype=float)
    eA = e[np.isclose(x, 0.0)].min()
    eB = e[np.isclose(x, 1.0)].min()
    return e - ((1 - x) * eA + x * eB)


def hull_0K(names: Sequence[str], x: Sequence[float], e: Sequence[float]) -> pd.DataFrame:
    """0 K lower convex hull.  Returns a DataFrame with columns
    name, x, e, e_form, on_hull, e_above_hull (eV/atom)."""
    x = np.asarray(x, dtype=float)
    e = np.asarray(e, dtype=float)
    ef = formation_energies(x, e)
    pts = np.column_stack([x, ef])
    idx = lower_hull_2d(pts)
    hx, he = pts[idx, 0], pts[idx, 1]
    above = ef - np.interp(x, hx, he)
    on = np.zeros(len(x), dtype=bool)
    on[idx] = True
    # ties: anything within 1e-9 of the hull counts as on it
    on |= np.abs(above) < 1e-9
    return pd.DataFrame({"name": list(names), "x": x, "e": e, "e_form": ef, "on_hull": on, "e_above_hull": np.maximum(above, 0.0)}).sort_values("x").reset_index(drop=True)


def hull_0K_pymatgen(names, elements: Tuple[str, str], x, e, n_atoms: Optional[Sequence[int]] = None):
    """Cross-check with pymatgen.analysis.phase_diagram.PhaseDiagram; returns e_above_hull per entry."""
    from pymatgen.analysis.phase_diagram import PDEntry, PhaseDiagram
    from pymatgen.core import Composition

    A, B = elements
    entries = []
    for nm, xi, ei in zip(names, x, e):
        comp = Composition({A: 1 - xi, B: xi}) if 0 < xi < 1 else Composition({A: 1.0} if xi == 0 else {B: 1.0})
        entries.append(PDEntry(comp, ei * 1.0, name=nm))  # energies per atom with 1-atom compositions
    pd_ = PhaseDiagram(entries)
    return np.array([pd_.get_e_above_hull(en) for en in entries])


def compare_ground_states(hull: pd.DataFrame, known_ground_states: Sequence[str], tol: float = 1e-3) -> pd.DataFrame:
    """Which known ground states does the MLIP reproduce?  Never drop a known
    phase from the candidate list because of this table; report it."""
    rows = []
    for nm in known_ground_states:
        r = hull[hull["name"] == nm]
        if r.empty:
            rows.append({"name": nm, "status": "not computed", "e_above_hull": np.nan})
            continue
        eah = float(r["e_above_hull"].iloc[0])
        rows.append({"name": nm, "status": "on hull" if eah <= tol else "above hull", "e_above_hull": eah})
    extra = hull[hull["on_hull"] & ~hull["name"].isin(known_ground_states) & (hull["x"] > 0) & (hull["x"] < 1)]
    for r in extra.itertuples():
        rows.append({"name": r.name, "status": "MLIP ground state not in known list", "e_above_hull": 0.0})
    return pd.DataFrame(rows)


def eos_scan(atoms: Atoms, calculator, scales=(0.94, 0.96, 0.98, 1.0, 1.02, 1.04, 1.06), eos: str = "vinet", relax_positions: bool = False, fmax: float = 1e-3) -> Tuple[EOSFit, np.ndarray, np.ndarray]:
    """E(V) scan with isotropic scaling.  Returns (fit per atom, volumes/atom, energies/atom)."""
    from ase.optimize import BFGS

    V, E = [], []
    for s in scales:
        a = atoms.copy()
        a.set_cell(atoms.get_cell() * s, scale_atoms=True)
        a.calc = calculator
        if relax_positions and len(a) > 1:
            BFGS(a, logfile=None).run(fmax=fmax, steps=500)
        V.append(a.get_volume() / len(a))
        E.append(a.get_potential_energy() / len(a))
    V, E = np.array(V), np.array(E)
    return fit_eos(V, E, eos=eos), V, E


def melting_check_inputs(path, element: str, mass: float, lattice: str, lattice_constant: float, pair_style: str, pair_coeff: str, temperature_guess: float, queue: Optional[Dict] = None, repeat=(5, 5, 5), n_equilibration_steps: int = 10000, n_switching_steps: int = 25000, tmin: Optional[float] = None, tmax: Optional[float] = None):
    """Write a calphy ``melting_temperature`` input (calphy >= 2 format)."""
    import yaml

    calc = {
        "mode": "melting_temperature",
        "element": [element],
        "mass": [mass],
        "lattice": lattice,
        "lattice_constant": lattice_constant,
        "repeat": list(repeat),
        "pressure": 0,
        "temperature": temperature_guess,
        "pair_style": pair_style,
        "pair_coeff": pair_coeff,
        "n_equilibration_steps": n_equilibration_steps,
        "n_switching_steps": n_switching_steps,
        "n_iterations": 1,
    }
    if tmin is not None and tmax is not None:
        calc["melting_temperature"] = {"guess": temperature_guess, "step": max(10.0, (tmax - tmin) / 10.0)}
    if queue:
        calc["queue"] = queue
    with open(path, "w") as f:
        yaml.safe_dump({"calculations": [calc]}, f, sort_keys=False)
    return str(path)
