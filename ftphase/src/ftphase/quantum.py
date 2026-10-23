"""Stage 04B: making quantum solids and classical liquids comparable.

calphy's thermodynamic integration (Einstein crystal / Uhlenbeck-Ford
references, Menon et al., Phys. Rev. Mater. 5, 103801 (2021)) is classical:
no zero-point energy, classical heat capacity 3k_B.  phonon/QHA free energies
are quantum.  Mixing both in one convex hull shifts the solid relative to the
liquid by the difference between the quantum and classical harmonic free
energies, which at high temperature tends to the Wigner-Kirkwood leading term
sum hbar^2 omega^2 / (24 (k_B T)^2) * k_B T per mode but at the temperatures of
interest for light elements (Li, Al) is still several meV/atom.

This module provides the first-order correction

    dF(T) = F_harm,quantum(T) - F_harm,classical(T)

from the same phonon frequencies, so that either the classical TI result can
be lifted to the quantum level (``classical + dF``) or the QHA result lowered
to the classical level (``quantum - dF``).  Which direction was used must be
recorded in the ``method`` column of the free-energy table.  The correction
is harmonic and therefore approximate; it does not cover quantum effects in
the liquid.
"""

from __future__ import annotations

import numpy as np

from .qha import harmonic_free_energy


def quantum_minus_classical(frequencies_ev, T, weights=None, imaginary="raise", imaginary_tol=1e-5):
    """dF(T) = F_q - F_cl per cell in eV; positive at low T (zero point)."""
    Fq = harmonic_free_energy(frequencies_ev, T, weights, quantum=True, imaginary=imaginary, imaginary_tol=imaginary_tol)
    Fc = harmonic_free_energy(frequencies_ev, T, weights, quantum=False, imaginary=imaginary, imaginary_tol=imaginary_tol)
    return np.asarray(Fq) - np.asarray(Fc)


def lift_classical_to_quantum(G_classical, frequencies_ev, T, weights=None, n_atoms=1):
    """G_classical (per atom) + dF/n_atoms."""
    return np.asarray(G_classical, dtype=float) + quantum_minus_classical(frequencies_ev, T, weights) / n_atoms


def lower_quantum_to_classical(G_quantum, frequencies_ev, T, weights=None, n_atoms=1):
    return np.asarray(G_quantum, dtype=float) - quantum_minus_classical(frequencies_ev, T, weights) / n_atoms


def wigner_kirkwood_leading(frequencies_ev, T, weights=None):
    """High-T expansion check: dF ~ sum w (hw)^2 / (24 k_B T) per cell."""
    from .units import KB_EV

    hw = np.asarray(frequencies_ev, dtype=float)
    w = np.ones_like(hw) if weights is None else np.asarray(weights, dtype=float)
    Ts = np.asarray(T, dtype=float)
    return np.sum(w * hw**2) / (24.0 * KB_EV * Ts)
