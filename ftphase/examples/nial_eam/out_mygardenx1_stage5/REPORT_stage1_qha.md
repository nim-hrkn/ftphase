# Example 7: Ni-Al T-x diagram, Purja Pun & Mishin 2009 EAM (classical level, 0 GPa)

Assembled 2026-10-22 22:18:07 on mygardenx1.  Files: out/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.

## Inputs

* potential: potentials/nial/Mishin-Ni-Al-2009.eam.alloy (NIST, Purja Pun & Mishin, Philos. Mag. 89, 3245 (2009)).
* solids: QHA of 64-atom SQS (fcc(Al) x = 0-0.03, fcc(Ni) x = 0.75-1), B2 54-atom cells with Ni anti-sites (Ni-rich) and Ni vacancies (Al-rich), L1_2 108-atom cells with anti-sites, Ni2Al3 and NiAl3 point phases; quantum QHA lowered to the classical level.
* liquids: calphy reversible scaling 2000 K -> T_stop(x), UFM, 3 iterations, 3 independent runs per composition averaged; compositions 0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00.
* configurational terms: ideal mixing (fcc), triple-defect sublattice model (B2: anti-sites + vacancies), two-sublattice anti-site model (L1_2).
* fits: liquid = ideal mixing + 4-term Redlich-Kister; fcc = polynomial excess over ideal mixing; B2, L1_2 = natural spline.

Temperature grid 950-2000 K (106 points); liquid runs per composition {0.0: 3, 0.1016: 3, 0.1992: 3, 0.3008: 3, 0.3984: 3, 0.5: 3, 0.6016: 3, 0.6992: 2, 0.8008: 2, 0.8984: 3, 1.0: 3}; sigma in the Monte Carlo (eV/atom) {'NiAl3': 0.002, 'Ni2Al3': 0.002, 'fccAl': 0.002, 'B2': 0.002, 'L12': 0.002, 'fccNi': 0.002, 'liquid': 0.0014}

## Key numbers (experiment: NiAl congruent 1911 K, B2 range ~0.45-0.60; Ni3Al peritectic 1668 K; eutectic L -> Ni3Al + (Ni) 1658 K x~0.76; Al-rich eutectic 913 K; Al 933.5 K; Ni 1728 K)

* B2 + liquid up to 1860.0 K; lowest temperature with liquid on the grid 950.0 K
* B2 composition range [x_Ni lower, upper] vs T: 1000 K [0.5370370370370371, 0.4949043109198396]; 1100 K [0.5370370370370371, 0.49287393343732994]; 1200 K [0.4972325116412564, 0.5065969718397761]; 1300 K [0.49366932161264626, 0.5137594543782124]; 1400 K [0.49193879353085795, 0.5168194588207027]; 1500 K [0.49092846266051215, 0.5185202518200684]; 1600 K [0.4902628381801114, 0.519723112708198]; 1700 K [0.4897370685215871, 0.5207289918593115]; 1800 K [0.5272694749537538, 0.5224042996377651]
* segments whose boundary sits at a sampled composition limit (flag edge=True in 07_two_phase_regions.tsv; the true width may be larger): 119
* invariant reactions (pairs change between T_low and T_high):
  * 1000-1010 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1170-1180 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1420-1430 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid']
  * 1430-1440 K: ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+liquid', 'fccNi+liquid']
  * 1500-1510 K: ['B2+B2', 'B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+liquid']
  * 1520-1530 K: ['B2+B2', 'B2+liquid', 'L12+liquid'] -> ['B2+B2', 'B2+liquid']
  * 1720-1730 K: ['B2+B2', 'B2+liquid'] -> ['B2+liquid']
* two-phase regions at 900 K: none
* two-phase regions at 1200 K: liquid(0.229)-B2(0.491); B2(0.497)-B2(0.507); B2(0.537)-L12(0.759); L12(0.759)-fccNi(0.893)
* two-phase regions at 1500 K: liquid(0.324)-B2(0.490); B2(0.491)-B2(0.518); B2(0.536)-liquid(0.670); liquid(0.720)-L12(0.759); L12(0.759)-liquid(0.800); liquid(0.906)-fccNi(0.919); fccNi(0.944)-liquid(0.957)
* two-phase regions at 1800 K: liquid(0.450)-B2(0.522); B2(0.527)-liquid(0.593)

## Same-phase segments (fit noise unless wide)

* B2+B2 x = 0.490-0.510 (width 0.020) at T = 1260-1330 K (8 temperatures)
* B2+B2 x = 0.490-0.520 (width 0.028) at T = 1340-1720 K (39 temperatures)
* B2+B2 x = 0.500-0.500 (width 0.005) at T = 1180-1180 K (1 temperatures)
* B2+B2 x = 0.500-0.510 (width 0.012) at T = 1190-1250 K (7 temperatures)

## Error bands (Monte Carlo, 30 samples)

* 950 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 950 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.905 +/- 0.003 (30/30)
* 950 K fccAl+liquid: x_a = 0.026 +/- 0.001, x_b = 0.103 +/- 0.018 (30/30)
* 950 K liquid+B2: x_a = 0.165 +/- 0.006, x_b = 0.496 +/- 0.000 (30/30)
* 950 K liquid+fccAl: x_a = 0.000 +/- 0.001, x_b = 0.011 +/- 0.003 (29/30)
* 1070 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 1070 K L12+fccNi: x_a = 0.758 +/- 0.004, x_b = 0.897 +/- 0.008 (30/30)
* 1070 K liquid+B2: x_a = 0.198 +/- 0.002, x_b = 0.493 +/- 0.000 (30/30)
* 1190 K B2+B2: x_a = 0.498 +/- 0.000, x_b = 0.505 +/- 0.000 (30/30)
* 1190 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 1190 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.894 +/- 0.003 (30/30)
* 1190 K liquid+B2: x_a = 0.225 +/- 0.005, x_b = 0.492 +/- 0.000 (30/30)
* 1310 K B2+B2: x_a = 0.493 +/- 0.000, x_b = 0.514 +/- 0.000 (30/30)
* 1310 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 1310 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.888 +/- 0.003 (30/30)
* 1310 K liquid+B2: x_a = 0.263 +/- 0.005, x_b = 0.491 +/- 0.000 (30/30)
* 1430 K B2+B2: x_a = 0.492 +/- 0.000, x_b = 0.517 +/- 0.000 (30/30)
* 1430 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (10/30)
* 1430 K B2+liquid: x_a = 0.537 +/- 0.000, x_b = 0.687 +/- 0.002 (20/30)
* 1430 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.882 +/- 0.003 (23/30)
* 1430 K L12+liquid: x_a = 0.759 +/- 0.000, x_b = 0.801 +/- 0.000 (7/30)
* 1430 K liquid+B2: x_a = 0.297 +/- 0.004, x_b = 0.490 +/- 0.000 (30/30)
* 1430 K liquid+L12: x_a = 0.694 +/- 0.006, x_b = 0.759 +/- 0.000 (20/30)
* 1430 K liquid+fccNi: x_a = 0.801 +/- 0.000, x_b = 0.882 +/- 0.003 (7/30)
* 1550 K B2+B2: x_a = 0.491 +/- 0.000, x_b = 0.519 +/- 0.000 (30/30)
* 1550 K B2+liquid: x_a = 0.533 +/- 0.001, x_b = 0.662 +/- 0.003 (30/30)
* 1550 K L12+liquid: x_a = 0.759 +/- 0.000, x_b = 0.776 +/- 0.007 (5/30)
* 1550 K fccNi+liquid: x_a = 0.935 +/- 0.000, x_b = 0.940 +/- 0.000 (1/30)
* 1550 K liquid+B2: x_a = 0.339 +/- 0.005, x_b = 0.490 +/- 0.000 (30/30)
* 1550 K liquid+L12: x_a = 0.741 +/- 0.005, x_b = 0.759 +/- 0.000 (4/30)
* 1550 K liquid+fccNi: x_a = 0.920 +/- 0.000, x_b = 0.925 +/- 0.000 (1/30)
* 1670 K B2+B2: x_a = 0.490 +/- 0.000, x_b = 0.520 +/- 0.000 (30/30)
* 1670 K B2+liquid: x_a = 0.530 +/- 0.000, x_b = 0.637 +/- 0.004 (30/30)
* 1670 K liquid+B2: x_a = 0.386 +/- 0.007, x_b = 0.490 +/- 0.000 (30/30)
* 1790 K B2+liquid: x_a = 0.528 +/- 0.000, x_b = 0.599 +/- 0.006 (30/30)
* 1790 K liquid+B2: x_a = 0.443 +/- 0.007, x_b = 0.522 +/- 0.000 (30/30)

## Caveats

* This EAM puts NiAl3 and Ni2Al3 60-120 meV/atom above the 0 K hull (01_hull_0K.tsv), so the Al-rich intermetallics of the experimental diagram are absent; the B2 and L1_2 widths are the point of this example.
* Nothing below the lowest T_stop of the liquids is computed; T_stop(x) is listed in 02B_liquids.json.
* Table check: mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum) (intended).
