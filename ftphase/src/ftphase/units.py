"""Physical constants and unit conversions (CODATA 2018, as used by ASE/scipy).

Equation references: (A1) 1 eV/atom = 96485.33 J/mol-atoms, (A2) Pv term.
"""

from __future__ import annotations

import numpy as np

KB_EV = 8.617333262e-5          # Boltzmann constant, eV/K
R_J = 8.314462618                # gas constant, J/(mol K)
EV_TO_J_PER_MOL = 96485.33212    # (A1) eV/atom -> J/mol-atoms
RY_TO_EV = 13.605693122994       # Rydberg -> eV
THZ_TO_EV = 4.135667696e-3       # h * 1 THz in eV
CM1_TO_EV = 1.239841984e-4       # hc * 1 cm^-1 in eV
GPA_A3_TO_EV = 0.006241509074    # (A2) 1 GPa * 1 A^3 in eV
KJ_PER_MOL_TO_EV = 1000.0 / EV_TO_J_PER_MOL


def ev_per_atom_to_j_per_mol(x):
    """(A1)"""
    return np.asarray(x, dtype=float) * EV_TO_J_PER_MOL


def j_per_mol_to_ev_per_atom(x):
    return np.asarray(x, dtype=float) / EV_TO_J_PER_MOL


def pv_term_ev(pressure_gpa, volume_a3_per_atom):
    """(A2) Pv in eV/atom from P in GPa and v in A^3/atom."""
    return GPA_A3_TO_EV * np.asarray(pressure_gpa, dtype=float) * np.asarray(volume_a3_per_atom, dtype=float)


def thz_to_ev(f):
    return np.asarray(f, dtype=float) * THZ_TO_EV


def ry_to_ev(e):
    return np.asarray(e, dtype=float) * RY_TO_EV
