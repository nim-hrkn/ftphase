# Example 6: ACE Al-Li full-range T-x diagram (classical level, 0 GPa)

Assembled 2026-10-22 17:22:28.  Files: out_full/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.

## Inputs

* solids: QHA of 64-atom icet SQS (fcc x = 0-0.25, bcc x = 0.75-1), B32 16-atom with anti-sites (x = 7/16, 1/2, 9/16), L1_2 Al3Li; quantum QHA lowered to the classical level with F_q-F_cl.
* liquids: calphy reversible scaling 1100 -> 700 K, UFM, 3 iterations, LAMMPS KOKKOS/CUDA (x <= 0.5 from example 5, x >= 0.6 new, 0.000, 0.102, 0.199, 0.301, 0.398, 0.500, 0.600, 0.700, 0.800, 0.900, 1.000).
* configurational terms: ideal mixing (fcc, bcc), two-sublattice anti-site model (B32), none (Al3Li).
* fits: cubic polynomial of the excess over the analytic ideal-mixing term (fcc, bcc, liquid), natural spline (B32).

## Key numbers

* lowest temperature with liquid on the grid: 700 K; coexistences there: B32(0.562) + liquid(0.765)
* highest temperature with fcc + liquid (Al melting bracket on a 10 K grid): 850 K
* invariant reactions (pairs change between T_low and T_high):
  * 730-740 K: ['B32+fcc', 'B32+liquid'] -> ['B32+liquid', 'fcc+liquid']
  * 850-860 K: ['B32+liquid', 'fcc+liquid'] -> ['B32+liquid']
  * 870-880 K: ['B32+liquid'] -> ['B32+liquid', 'liquid+liquid']
  * 880-890 K: ['B32+liquid', 'liquid+liquid'] -> ['liquid+liquid']
* two-phase regions at 700 K: fcc(0.102)-B32(0.485); B32(0.562)-liquid(0.765)
* two-phase regions at 800 K: fcc(0.083)-liquid(0.184); liquid(0.320)-B32(0.486); B32(0.562)-liquid(0.708)
* two-phase regions at 900 K: liquid(0.472)-liquid(0.480)
* two-phase regions at 1000 K: liquid(0.472)-liquid(0.480)

## Error bands (Monte Carlo, sigma = 2 meV/atom solids, 1.4 meV/atom liquid, 30 samples)

* 720 K B32+liquid: x_a = 0.562 +/- 0.000, x_b = 0.755 +/- 0.009 (found in 30/30 samples)
* 720 K fcc+B32: x_a = 0.111 +/- 0.008, x_b = 0.484 +/- 0.001 (found in 27/30 samples)
* 720 K fcc+liquid: x_a = 0.090 +/- 0.012, x_b = 0.220 +/- 0.021 (found in 3/30 samples)
* 720 K liquid+B32: x_a = 0.249 +/- 0.010, x_b = 0.483 +/- 0.001 (found in 3/30 samples)
* 800 K B32+liquid: x_a = 0.562 +/- 0.000, x_b = 0.707 +/- 0.012 (found in 30/30 samples)
* 800 K fcc+liquid: x_a = 0.083 +/- 0.015, x_b = 0.183 +/- 0.037 (found in 30/30 samples)
* 800 K liquid+B32: x_a = 0.321 +/- 0.018, x_b = 0.487 +/- 0.003 (found in 30/30 samples)
* 900 K B32+liquid: x_a = 0.562 +/- 0.000, x_b = 0.608 +/- 0.014 (found in 4/30 samples)
* 900 K liquid+B32: x_a = 0.498 +/- 0.027, x_b = 0.528 +/- 0.014 (found in 4/30 samples)
* 900 K liquid+liquid: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (found in 29/30 samples)

## Configurational noise: 64-atom SQS (this run) vs mean of two 32-atom random cells (example 5), fcc at 800 K

* x = 0.0625: G_SQS64 - G_random32 = -0.78 meV/atom (random-cell half spread 0.00 meV/atom)
* x = 0.1250: G_SQS64 - G_random32 = -0.78 meV/atom (random-cell half spread 0.58 meV/atom)
* x = 0.1875: G_SQS64 - G_random32 = +0.58 meV/atom (random-cell half spread 1.71 meV/atom)
* x = 0.2500: G_SQS64 - G_random32 = -2.75 meV/atom (random-cell half spread 0.29 meV/atom)

## Caveats

* Li-rich intermetallics Al2Li3 and Al4Li9 are not included; the Li side is B32 + bcc + liquid only.
* Nothing below 700 K is computed (QHA solids exist down to 0 K, liquids only 700-1100 K).
* Example 5 found ACE temperatures about 100 K below experiment with the right composition features; compare the eutectic here with 873 K / x = 0.30.
* Table check warnings: mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum) (the quantum/classical mix is intended: every phase is on the classical level after the correction).
