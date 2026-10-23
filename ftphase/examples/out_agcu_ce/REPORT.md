# Ag-Cu fcc miscibility gap: cluster expansion (icet, EAM-trained) + MC vs direct-potential SGC MC vs ideal + RK

## Cluster expansion (631 enumerated fcc orderings with 1-8 atoms, EAM Williams-Mishin-Hamilton 2006, positions + cell relaxed)

| cutoffs (pair, triplet, quadruplet; A) | ECIs (nonzero/total) | rmse train | rmse 10-fold CV (meV/atom) |
|---|---|---|---|
| p11t7q5 [11.0, 7.0, 5.0] | 32/58 | 8.08 | 8.99 |
| p13t7 [13.0, 7.0] | 27/51 | 8.21 | 8.96 |
| p7t5 [7.0, 5.0] | 12/15 | 10.42 | 10.63 |
| p9t6 [9.0, 6.0] | 18/25 | 9.13 | 9.55 |
| p9t6q4 [9.0, 6.0, 4.0] | 18/28 | 9.16 | 9.58 |

Formation energies of the training set are 0-134 meV/atom (all positive); the CV error of about 10 meV/atom (any cutoff) is the lattice-CE limit for this 13 % size-mismatch pair with relaxed energies. VCSGC used `p13t7`; the SGC pass used p7t5.

## Solvus (fcc miscibility gap), x_Cu

| T (K) | CE+VCSGC x_alpha | CE dilute x_alpha | CE+SGC x_alpha | direct MC x_alpha | RK x_alpha | CE+VCSGC x_beta | CE dilute x_beta | CE+SGC x_beta | direct MC x_beta | RK x_beta | dmu* VCSGC / direct (eV) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800 | 0.023 | 0.020 | 0.122 | 0.027 | 0.042 | 0.964 | 0.961 | 0.844 | 0.990 | 0.987 | -0.643 / -0.660 |
| 900 | 0.028 | 0.027 | 0.071 | 0.050 | 0.045 | 0.968 | 0.936 | 0.999 | 0.972 | 0.978 | -0.653 / -0.660 |
| 1000 | 0.031 | 0.033 | 0.141 | 0.126 | 0.078 | 0.959 | 0.901 | 0.999 | 0.914 | 0.955 | -0.667 / -0.650 |

* CE+VCSGC: variance-constrained SGC (kappa = 200, 171 phi points per T, 20 + 20 sweeps, 2048 sites, independent random starts), dF/dx = -k_B T kappa (phi + 2<x>); inside the gap the 2048-site cell is two-phase and dF/dx follows the common-tangent slope, but not exactly flat (it varies by about 0.1 eV across the gap: the interface free energy of the precipitate changes with its size and shape), so the solvus is where the ideal dilute branch c + k_B T ln(x/(1-x)), with c fitted to the 4 points nearest the pure element, reaches the two-phase level measured just inside the gap (median of dF/dx over 0.05 < x < 0.15 and 0.85 < x < 0.95; ftphase.ce.solvus_from_vcsgc); dmu* is the median of dF/dx over the gap.
* CE dilute: ideal dilute solution with the CE impurity energies (Cu in Ag 0.293 eV, Ag in Cu 0.200 eV, 2048-site cells) and the VCSGC dmu*: x_alpha = exp((dmu*_mix - E_imp)/k_B T).
* CE+SGC: the first pass (agcu_ce_mc.py), branch integration with the repaired jump detection; the lattice CE shows no hysteresis, so the alpha branch ends at the coexistence dmu and the last pre-jump point of a 2048-site SGC run is already a two-phase state (first-pass table: 0.122 / 0.341 / 0.141).
* direct MC: LAMMPS fix atom/swap SGC on the EAM (agcu_sgcmc/), 2048 atoms with MD, branch integration.  RK: random 32-atom cells + ideal mixing + calphy/QHA vibrations (example 9).
* CE+MC (both ensembles) is static: no vibrational contribution, lattice-mapped relaxed energies; the CE truncation error (10 meV/atom) is larger than k_B T x ln x differences that set a dilute solvus, so the CE route is not expected to reproduce the direct-potential gap for Ag-Cu.
