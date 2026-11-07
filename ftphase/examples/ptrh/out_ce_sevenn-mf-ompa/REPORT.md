# Pt-Rh CE + canonical MC with sevenn-mf-ompa (2026-11-07)

Training: 631 fcc orderings (1-8 atoms), relaxed (positions + cell, fmax 2e-3). CE cutoffs [9.0, 6.0, 5.0] A, least-squares, rmse train 0.46 / CV 0.50 meV/atom, 41 nonzero of 41 ECIs.

## 0 K: ordered structures vs the random state (CE)

| structure | x_Rh | E_form (MLIP, relaxed) meV/atom | E_form random (CE) | ordering energy |
|---|---|---|---|---|
| Pt3Rh-D0_22 | 0.25 | -17.9 | -12.7 | -5.2 |
| PtRh-40 | 0.5 | -26.4 | -19.3 | -7.1 |
| PtRh3-D0_22 | 0.75 | -22.6 | -16.4 | -6.2 |

Ground-state line of the training set (x, E_form meV/atom): (0.000, 0.0), (0.250, -18.5), (0.500, -31.2), (0.625, -27.9), (0.714, -24.9), (0.750, -23.6), (0.833, -16.6), (0.875, -12.6), (1.000, 0.0)

## Order-disorder temperatures (C_v peak of the cooling scan)

| x_Rh | T_c (K) | C_v max (k_B) |
|---|---|---|
| 0.25 | 120 | 0.49 |
| 0.50 | 180 | 9.14 |
| 0.75 | 120 | 0.61 |

MC: 8^3 conventional fcc cells (2048 sites), 40 + 80 sweeps per T, cooling 500 -> 20 K in 20 K steps; the structure is carried between temperatures (hysteresis possible for first-order transitions). Lattice CE: no vibrations, no relaxation energy beyond the training cells.

Reference (Saengdeejing et al. 2026, Table 7): fcc <-> PtRh 258 K (PFP) / 210 K (DFT); fcc <-> PtRh3 235 / 156 K; fcc <-> Pt3Rh 146 K (PFP only); Pohl & Albe MC: PtRh 238 K.
