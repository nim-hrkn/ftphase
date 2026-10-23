# Example 6: ACE Al-Li full-range T-x diagram (classical level, 0 GPa)

Assembled 2026-10-22 20:53:42.  Files: out_full/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.

## Inputs

* solids: QHA of 64-atom icet SQS (fcc x = 0-0.25, bcc x = 0.75-1), B32 16-atom with anti-sites (x = 7/16, 1/2, 9/16), L1_2 Al3Li; quantum QHA lowered to the classical level with F_q-F_cl.
* liquids: calphy reversible scaling 1100 -> 700 K, UFM, 3 iterations, LAMMPS KOKKOS/CUDA (x <= 0.5 from example 5, x >= 0.6 new, 0.000, 0.102, 0.199, 0.301, 0.398, 0.500, 0.600, 0.700, 0.800, 0.900, 1.000).
* configurational terms: ideal mixing (fcc, bcc), two-sublattice anti-site model (B32), none (Al3Li).
* fits: cubic polynomial of the excess over the analytic ideal-mixing term (fcc, bcc, liquid), natural spline (B32).

Temperature grid: 700-1100 K (41 points); liquid runs per composition: {0.0: 1, 0.1016: 1, 0.1992: 1, 0.3008: 1, 0.3984: 1, 0.5: 1, 0.6: 1, 0.7: 1, 0.8: 1, 0.9: 1, 1.0: 1}; sigma used in the Monte Carlo (eV/atom): {'bcc': 0.002, 'Al4Li9': 0.002, 'Al3Li': 0.002, 'fcc': 0.002, 'B32': 0.002, 'Al2Li3': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 700 K; coexistences there: B32(0.562) + liquid(0.718); liquid(0.895) + liquid(0.976)
* highest temperature with fcc + liquid (Al melting bracket on a 10 K grid): 850 K
* invariant reactions (pairs change between T_low and T_high):
  * 750-760 K: ['B32+fcc', 'B32+liquid', 'liquid+liquid'] -> ['B32+fcc', 'B32+liquid']
  * 760-770 K: ['B32+fcc', 'B32+liquid'] -> ['B32+liquid', 'fcc+liquid']
  * 840-850 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']
  * 850-860 K: ['fcc+liquid', 'liquid+liquid'] -> ['liquid+liquid']
* two-phase regions at 700 K: fcc(0.102)-B32(0.485); B32(0.562)-liquid(0.718); liquid(0.895)-liquid(0.976)
* two-phase regions at 800 K: fcc(0.109)-liquid(0.276); liquid(0.371)-B32(0.485); B32(0.562)-liquid(0.655)
* two-phase regions at 900 K: liquid(0.472)-liquid(0.480)
* two-phase regions at 1000 K: liquid(0.472)-liquid(0.480)

## Same-phase segments (fit noise, not phase boundaries)

The lower hull of one fitted curve shows a 'gap' where the curve is slightly concave.  Segments that keep the same x in every Monte Carlo sample (std 0 below) come from the curvature of the fit through the sampled points, i.e. from the 1-2 meV/atom statistical noise of the free energies, not from the physics.  Treat them as noise unless they are wide (> 0.1 in x) and survive a denser composition grid.

* liquid+liquid x = 0.470-0.480 (width 0.007) at T = 850-1100 K (26 temperatures)
* liquid+liquid x = 0.900-0.970 (width 0.072) at T = 710-710 K (1 temperatures)
* liquid+liquid x = 0.900-0.980 (width 0.080) at T = 700-700 K (1 temperatures)
* liquid+liquid x = 0.910-0.960 (width 0.053) at T = 730-730 K (1 temperatures)
* liquid+liquid x = 0.910-0.970 (width 0.064) at T = 720-720 K (1 temperatures)
* liquid+liquid x = 0.920-0.960 (width 0.038) at T = 740-740 K (1 temperatures)
* liquid+liquid x = 0.930-0.950 (width 0.011) at T = 750-750 K (1 temperatures)

## Error bands (Monte Carlo, sigma = 2 meV/atom solids, 1.4 meV/atom liquid, 30 samples)

* 720 K Al2Li3+liquid: x_a = 0.600 +/- 0.000, x_b = 0.713 +/- 0.016 (found in 9/30 samples)
* 720 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (found in 9/30 samples)
* 720 K B32+liquid: x_a = 0.562 +/- 0.000, x_b = 0.711 +/- 0.009 (found in 21/30 samples)
* 720 K fcc+B32: x_a = 0.110 +/- 0.009, x_b = 0.484 +/- 0.001 (found in 30/30 samples)
* 720 K liquid+liquid: x_a = 0.905 +/- 0.000, x_b = 0.969 +/- 0.000 (found in 30/30 samples)
* 800 K B32+liquid: x_a = 0.562 +/- 0.004, x_b = 0.654 +/- 0.024 (found in 30/30 samples)
* 800 K fcc+B32: x_a = 0.143 +/- 0.000, x_b = 0.478 +/- 0.000 (found in 1/30 samples)
* 800 K fcc+liquid: x_a = 0.112 +/- 0.011, x_b = 0.277 +/- 0.032 (found in 29/30 samples)
* 800 K liquid+B32: x_a = 0.372 +/- 0.032, x_b = 0.485 +/- 0.006 (found in 29/30 samples)
* 900 K fcc+liquid: x_a = 0.074 +/- 0.000, x_b = 0.088 +/- 0.000 (found in 1/30 samples)
* 900 K liquid+fcc: x_a = 0.049 +/- 0.000, x_b = 0.058 +/- 0.000 (found in 1/30 samples)
* 900 K liquid+liquid: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (found in 30/30 samples)

## Configurational noise: 64-atom SQS (this run) vs mean of two 32-atom random cells (example 5), fcc at 800 K

* x = 0.0625: G_SQS64 - G_random32 = -0.78 meV/atom (random-cell half spread 0.00 meV/atom)
* x = 0.1250: G_SQS64 - G_random32 = -0.78 meV/atom (random-cell half spread 0.58 meV/atom)
* x = 0.1875: G_SQS64 - G_random32 = +0.58 meV/atom (random-cell half spread 1.71 meV/atom)
* x = 0.2500: G_SQS64 - G_random32 = -2.75 meV/atom (random-cell half spread 0.29 meV/atom)

## Caveats

* Li-rich intermetallics included as point phases: Al2Li3, Al4Li9 (Materials Project CIFs, structures/README.md); phases appearing in the diagram: B32, fcc, liquid
* Nothing below 700 K is computed (QHA solids exist down to 0 K, liquids only 700-1100 K).
* Example 5 found ACE temperatures about 100 K below experiment with the right composition features; compare the eutectic here with 873 K / x = 0.30.
* Table check warnings: mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum) (the quantum/classical mix is intended: every phase is on the classical level after the correction).
