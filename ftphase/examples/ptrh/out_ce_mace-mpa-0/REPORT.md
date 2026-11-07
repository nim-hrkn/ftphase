# Pt-Rh CE + canonical MC with mace-mpa-0 (2026-11-07)

Training: 631 fcc orderings (1-8 atoms), relaxed (positions + cell, fmax 2e-3). CE cutoffs [9.0, 6.0, 5.0] A, ARDR, rmse train 0.66 / CV 0.71 meV/atom, 41 nonzero of 41 ECIs.

## 0 K: ordered structures vs the random state (CE)

| structure | x_Rh | E_form (MLIP, relaxed) meV/atom | E_form random (CE) | ordering energy |
|---|---|---|---|---|
| Pt3Rh-D0_22 | 0.25 | -15.7 | -11.5 | -4.2 |
| PtRh-40 | 0.5 | -22.9 | -15.4 | -7.4 |
| PtRh3-D0_22 | 0.75 | -19.0 | -12.5 | -6.5 |

Ground-state line of the training set (x, E_form meV/atom): (0.000, 0.0), (0.125, -8.8), (0.200, -13.9), (0.250, -16.6), (0.375, -22.0), (0.500, -26.8), (0.750, -19.7), (0.833, -13.9), (0.875, -11.0), (1.000, 0.0)

## Order-disorder temperatures (C_v peak of the cooling scan)

| x_Rh | T_c (K) | C_v max (k_B) |
|---|---|---|
| 0.25 | 100 | 0.45 |
| 0.50 | 160 | 1.71 |
| 0.75 | 140 | 1.40 |

MC: 8^3 conventional fcc cells (2048 sites), 40 + 80 sweeps per T, cooling 500 -> 20 K in 20 K steps; the structure is carried between temperatures (hysteresis possible for first-order transitions). Lattice CE: no vibrations, no relaxation energy beyond the training cells.

Reference (Saengdeejing et al. 2026, Table 7): fcc <-> PtRh 258 K (PFP) / 210 K (DFT); fcc <-> PtRh3 235 / 156 K; fcc <-> Pt3Rh 146 K (PFP only); Pohl & Albe MC: PtRh 238 K.
