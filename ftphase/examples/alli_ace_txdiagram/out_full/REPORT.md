# Example 6: ACE Al-Li full-range T-x diagram (classical level, 0 GPa)

Assembled 2026-10-23 08:18:46.  Files: out_full/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.

## Inputs

* solids: QHA of 64-atom icet SQS (fcc x = 0-0.25, bcc x = 0.75-1), B32 16-atom with anti-sites (x = 7/16, 1/2, 9/16), L1_2 Al3Li; quantum QHA lowered to the classical level with F_q-F_cl.
* liquids: calphy reversible scaling 1100 -> 700 K plus (calphy_liquid_more/) 700 -> 650/500 K sweeps and 2 independent repeats per composition, averaged per (x, T); UFM, 3 iterations, LAMMPS KOKKOS/CUDA (x <= 0.5 from example 5, x >= 0.6 new, 0.000, 0.102, 0.199, 0.301, 0.398, 0.500, 0.600, 0.700, 0.800, 0.900, 1.000).
* configurational terms: ideal mixing (fcc, bcc), two-sublattice anti-site model (B32), none (Al3Li).
* fits: cubic polynomial of the excess over the analytic ideal-mixing term (fcc, bcc, liquid), natural spline (B32).

Temperature grid: 650-1100 K (46 points); liquid runs per composition: {0.0: 3, 0.1016: 3, 0.1992: 4, 0.3008: 4, 0.3984: 4, 0.5: 3, 0.6: 3, 0.7: 4, 0.8: 4, 0.9: 4, 1.0: 4}; sigma used in the Monte Carlo (eV/atom): {'Al3Li': 0.002, 'bcc': 0.002, 'Al4Li9': 0.002, 'B32': 0.002, 'fcc': 0.002, 'Al2Li3': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 650 K; coexistences there: Al4Li9(0.692) + liquid(0.776); liquid(0.883) + liquid(0.982)
* highest temperature with fcc + liquid (Al melting bracket on a 10 K grid): 890 K
* invariant reactions (pairs change between T_low and T_high):
  * 670-680 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+liquid', 'B32+fcc', 'liquid+liquid'] -> ['Al2Li3+B32', 'Al2Li3+liquid', 'B32+fcc', 'liquid+liquid']
  * 710-720 K: ['Al2Li3+B32', 'Al2Li3+liquid', 'B32+fcc', 'liquid+liquid'] -> ['B32+fcc', 'B32+liquid', 'liquid+liquid']
  * 750-760 K: ['B32+fcc', 'B32+liquid', 'liquid+liquid'] -> ['B32+fcc', 'B32+liquid']
  * 760-770 K: ['B32+fcc', 'B32+liquid'] -> ['B32+liquid', 'fcc+liquid']
  * 840-850 K: ['B32+liquid', 'fcc+liquid'] -> ['B32+liquid', 'fcc+liquid', 'liquid+liquid']
  * 850-860 K: ['B32+liquid', 'fcc+liquid', 'liquid+liquid'] -> ['fcc+liquid', 'liquid+liquid']
  * 890-900 K: ['fcc+liquid', 'liquid+liquid'] -> ['liquid+liquid']
* two-phase regions at 700 K: fcc(0.075)-B32(0.486); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-liquid(0.723); liquid(0.890)-liquid(0.978)
* two-phase regions at 800 K: fcc(0.095)-liquid(0.266); liquid(0.368)-B32(0.487); B32(0.562)-liquid(0.655)
* two-phase regions at 900 K: liquid(0.472)-liquid(0.480)
* two-phase regions at 1000 K: liquid(0.472)-liquid(0.480)

## Same-phase segments (fit noise, not phase boundaries)

The lower hull of one fitted curve shows a 'gap' where the curve is slightly concave.  Segments that keep the same x in every Monte Carlo sample (std 0 below) come from the curvature of the fit through the sampled points, i.e. from the 1-2 meV/atom statistical noise of the free energies, not from the physics.  Treat them as noise unless they are wide (> 0.1 in x) and survive a denser composition grid.

* liquid+liquid x = 0.470-0.480 (width 0.007) at T = 850-1100 K (26 temperatures)
* liquid+liquid x = 0.880-0.980 (width 0.098) at T = 650-660 K (2 temperatures)
* liquid+liquid x = 0.890-0.980 (width 0.087) at T = 670-700 K (3 temperatures)
* liquid+liquid x = 0.900-0.970 (width 0.072) at T = 690-720 K (3 temperatures)
* liquid+liquid x = 0.910-0.970 (width 0.056) at T = 730-730 K (1 temperatures)
* liquid+liquid x = 0.920-0.960 (width 0.042) at T = 740-740 K (1 temperatures)
* liquid+liquid x = 0.930-0.950 (width 0.021) at T = 750-750 K (1 temperatures)

## Error bands (Monte Carlo, sigma = 2 meV/atom solids, 1.4 meV/atom liquid, 30 samples)

* 690 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (found in 3/30 samples)
* 690 K Al2Li3+liquid: x_a = 0.600 +/- 0.000, x_b = 0.740 +/- 0.013 (found in 16/30 samples)
* 690 K Al3Li+B32: x_a = 0.250 +/- 0.000, x_b = 0.486 +/- 0.000 (found in 1/30 samples)
* 690 K Al4Li9+liquid: x_a = 0.692 +/- 0.000, x_b = 0.746 +/- 0.013 (found in 7/30 samples)
* 690 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (found in 19/30 samples)
* 690 K B32+Al4Li9: x_a = 0.562 +/- 0.000, x_b = 0.692 +/- 0.000 (found in 4/30 samples)
* 690 K B32+liquid: x_a = 0.562 +/- 0.000, x_b = 0.736 +/- 0.007 (found in 7/30 samples)
* 690 K fcc+Al3Li: x_a = 0.044 +/- 0.000, x_b = 0.250 +/- 0.000 (found in 1/30 samples)
* 690 K fcc+B32: x_a = 0.069 +/- 0.018, x_b = 0.486 +/- 0.001 (found in 29/30 samples)
* 690 K liquid+liquid: x_a = 0.898 +/- 0.000, x_b = 0.974 +/- 0.000 (found in 30/30 samples)
* 770 K Al2Li3+liquid: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.008 (found in 2/30 samples)
* 770 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (found in 2/30 samples)
* 770 K B32+liquid: x_a = 0.562 +/- 0.000, x_b = 0.683 +/- 0.012 (found in 28/30 samples)
* 770 K fcc+B32: x_a = 0.155 +/- 0.029, x_b = 0.482 +/- 0.002 (found in 16/30 samples)
* 770 K fcc+liquid: x_a = 0.117 +/- 0.038, x_b = 0.282 +/- 0.035 (found in 14/30 samples)
* 770 K liquid+B32: x_a = 0.324 +/- 0.019, x_b = 0.483 +/- 0.002 (found in 14/30 samples)
* 850 K B32+liquid: x_a = 0.562 +/- 0.000, x_b = 0.605 +/- 0.020 (found in 20/30 samples)
* 850 K fcc+liquid: x_a = 0.046 +/- 0.024, x_b = 0.137 +/- 0.061 (found in 29/30 samples)
* 850 K liquid+B32: x_a = 0.450 +/- 0.024, x_b = 0.501 +/- 0.006 (found in 20/30 samples)
* 850 K liquid+liquid: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (found in 13/30 samples)

## Configurational noise: 64-atom SQS (this run) vs mean of two 32-atom random cells (example 5), fcc at 800 K

* x = 0.0625: G_SQS64 - G_random32 = -0.92 meV/atom (random-cell half spread 0.00 meV/atom)
* x = 0.1250: G_SQS64 - G_random32 = -0.92 meV/atom (random-cell half spread 0.58 meV/atom)
* x = 0.1875: G_SQS64 - G_random32 = +0.45 meV/atom (random-cell half spread 1.71 meV/atom)
* x = 0.2500: G_SQS64 - G_random32 = -2.89 meV/atom (random-cell half spread 0.29 meV/atom)

## Caveats

* Li-rich intermetallics included as point phases: Al2Li3, Al4Li9 (Materials Project CIFs, structures/README.md); phases appearing in the diagram: Al2Li3, Al4Li9, B32, fcc, liquid
* Nothing below 650 K is shown: the grid keeps only temperatures where the liquid has both pure ends and at least 6 compositions (QHA solids exist down to 0 K). Lowest liquid temperature per x: 0.000 K=650, 0.102 K=800, 0.199 K=650, 0.301 K=650, 0.398 K=500, 0.500 K=700, 0.600 K=700, 0.700 K=500, 0.800 K=500, 0.900 K=500, 1.000 K=500.
* Example 5 found ACE temperatures about 100 K below experiment with the right composition features; compare the eutectic here with 873 K / x = 0.30.
* Table check warnings: mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum) (the quantum/classical mix is intended: every phase is on the classical level after the correction).
