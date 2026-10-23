# Example 7: Ni-Al T-x diagram, Purja Pun & Mishin 2009 EAM (classical level, 0 GPa)

Assembled 2026-10-22 22:35:22 on mygardenx1.  Files: out/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.

## Inputs

* potential: potentials/nial/Mishin-Ni-Al-2009.eam.alloy (NIST, Purja Pun & Mishin, Philos. Mag. 89, 3245 (2009)).
* solids: QHA of 64-atom SQS (fcc(Al) x = 0-0.03, fcc(Ni) x = 0.75-1), B2 54-atom cells with Ni anti-sites (Ni-rich) and Ni vacancies (Al-rich), L1_2 108-atom cells with anti-sites, Ni2Al3 and NiAl3 point phases; quantum QHA lowered to the classical level.
* liquids: calphy reversible scaling 2000 K -> T_stop(x), UFM, 3 iterations, 3 independent runs per composition averaged; compositions 0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00.
* configurational terms: ideal mixing (fcc), triple-defect sublattice model (B2: anti-sites + vacancies), two-sublattice anti-site model (L1_2).
* fits: liquid = ideal mixing + 4-term Redlich-Kister; fcc = polynomial excess over ideal mixing; B2, L1_2 = natural spline.

Temperature grid 950-2000 K (106 points); liquid runs per composition {0.0: 3, 0.1016: 3, 0.1992: 3, 0.3008: 3, 0.3984: 3, 0.5: 3, 0.6016: 3, 0.6992: 3, 0.8008: 3, 0.8984: 3, 1.0: 3}; sigma in the Monte Carlo (eV/atom) {'NiAl3': 0.002, 'fccNi': 0.002, 'L12': 0.002, 'Ni2Al3': 0.002, 'fccAl': 0.002, 'B2': 0.002, 'liquid': 0.0014}

## Key numbers (experiment: NiAl congruent 1911 K, B2 range ~0.45-0.60; Ni3Al peritectic 1668 K; eutectic L -> Ni3Al + (Ni) 1658 K x~0.76; Al-rich eutectic 913 K; Al 933.5 K; Ni 1728 K)

* B2 + liquid up to 1900.0 K; lowest temperature with liquid on the grid 950.0 K
* B2 composition range [x_Ni lower, upper] vs T: 1000 K [0.5148112535612536, 0.5370370370370371]; 1100 K [0.5173433048433049, 0.5370370370370371]; 1200 K [0.5370370370370371, 0.4993747120034901]; 1300 K [0.5370370370370371, 0.4992689877359935]; 1400 K [0.5370370370370371, 0.49919799390342817]; 1500 K [0.5370370370370371, 0.4987782179899352]; 1600 K [0.5370370370370371, 0.4994094622158511]; 1700 K [0.5370370370370371, 0.5025966508211528]; 1800 K [0.5358960410997133, 0.5126838751576672]; 1900 K [0.5255652633263938, 0.5198986265635511]
* segments whose boundary sits at a sampled composition limit (flag edge=True in 07_two_phase_regions.tsv; the true width may be larger): 160
* invariant reactions (pairs change between T_low and T_high):
  * 950-960 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1110-1120 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1560-1570 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+liquid', 'L12+fccNi', 'L12+liquid']
  * 1640-1650 K: ['B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+liquid', 'L12+liquid', 'fccNi+liquid']
  * 1690-1700 K: ['B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
  * 1740-1750 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid']
* two-phase regions at 900 K: none
* two-phase regions at 1200 K: liquid(0.209)-B2(0.499); B2(0.537)-L12(0.759); L12(0.759)-fccNi(0.897)
* two-phase regions at 1500 K: liquid(0.304)-B2(0.499); B2(0.537)-L12(0.759); L12(0.759)-fccNi(0.879)
* two-phase regions at 1800 K: liquid(0.421)-B2(0.513); B2(0.536)-liquid(0.611)

## Same-phase segments (fit noise unless wide)

* B2+B2 x = 0.510-0.540 (width 0.023) at T = 950-1020 K (8 temperatures)
* B2+B2 x = 0.520-0.540 (width 0.021) at T = 1030-1110 K (9 temperatures)

## Error bands (Monte Carlo, 30 samples)

* 950 K B2+B2: x_a = 0.514 +/- 0.000, x_b = 0.537 +/- 0.000 (30/30)
* 950 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 950 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.910 +/- 0.003 (30/30)
* 950 K fccAl+B2: x_a = 0.030 +/- 0.001, x_b = 0.499 +/- 0.000 (10/30)
* 950 K fccAl+liquid: x_a = 0.026 +/- 0.004, x_b = 0.125 +/- 0.017 (20/30)
* 950 K liquid+B2: x_a = 0.146 +/- 0.005, x_b = 0.499 +/- 0.000 (20/30)
* 1070 K B2+B2: x_a = 0.516 +/- 0.000, x_b = 0.537 +/- 0.000 (30/30)
* 1070 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 1070 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.904 +/- 0.003 (30/30)
* 1070 K liquid+B2: x_a = 0.179 +/- 0.006, x_b = 0.499 +/- 0.000 (30/30)
* 1190 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 1190 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.897 +/- 0.003 (30/30)
* 1190 K liquid+B2: x_a = 0.206 +/- 0.005, x_b = 0.499 +/- 0.000 (30/30)
* 1310 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 1310 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.891 +/- 0.003 (30/30)
* 1310 K liquid+B2: x_a = 0.244 +/- 0.005, x_b = 0.499 +/- 0.000 (30/30)
* 1430 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (30/30)
* 1430 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.884 +/- 0.004 (30/30)
* 1430 K liquid+B2: x_a = 0.281 +/- 0.005, x_b = 0.499 +/- 0.000 (30/30)
* 1550 K B2+L12: x_a = 0.537 +/- 0.000, x_b = 0.759 +/- 0.000 (27/30)
* 1550 K B2+liquid: x_a = 0.537 +/- 0.000, x_b = 0.669 +/- 0.001 (3/30)
* 1550 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.876 +/- 0.004 (30/30)
* 1550 K liquid+B2: x_a = 0.321 +/- 0.005, x_b = 0.499 +/- 0.000 (30/30)
* 1550 K liquid+L12: x_a = 0.670 +/- 0.002, x_b = 0.759 +/- 0.000 (3/30)
* 1670 K B2+liquid: x_a = 0.537 +/- 0.000, x_b = 0.649 +/- 0.004 (30/30)
* 1670 K L12+fccNi: x_a = 0.759 +/- 0.000, x_b = 0.859 +/- 0.000 (1/30)
* 1670 K L12+liquid: x_a = 0.759 +/- 0.000, x_b = 0.817 +/- 0.006 (29/30)
* 1670 K liquid+B2: x_a = 0.364 +/- 0.006, x_b = 0.501 +/- 0.001 (30/30)
* 1670 K liquid+L12: x_a = 0.702 +/- 0.006, x_b = 0.759 +/- 0.000 (30/30)
* 1670 K liquid+fccNi: x_a = 0.839 +/- 0.012, x_b = 0.879 +/- 0.010 (29/30)
* 1790 K B2+liquid: x_a = 0.536 +/- 0.001, x_b = 0.615 +/- 0.006 (30/30)
* 1790 K liquid+B2: x_a = 0.416 +/- 0.007, x_b = 0.512 +/- 0.001 (30/30)

## QHA (classical level) minus calphy solid TI, per cell (anharmonic error of the quasi-harmonic route; mesh converged)

* fccNi x = 1.0000 at 1000 K: +22.4 meV/atom
* fccNi x = 1.0000 at 1500 K: +43.1 meV/atom
* fccNi x = 0.9375 at 1000 K: +13.0 meV/atom
* fccNi x = 0.9375 at 1500 K: +26.7 meV/atom
* fccNi x = 0.8750 at 1000 K: +13.3 meV/atom
* fccNi x = 0.8750 at 1500 K: +26.8 meV/atom
* fccNi x = 0.8125 at 1000 K: +12.0 meV/atom
* fccNi x = 0.8125 at 1500 K: +25.1 meV/atom
* fccNi x = 0.7500 at 1000 K: +13.5 meV/atom
* fccNi x = 0.7500 at 1500 K: +28.0 meV/atom
* B2 x = 0.5000 at 1000 K: +9.9 meV/atom
* B2 x = 0.5000 at 1500 K: +15.9 meV/atom
* B2 x = 0.5185 at 1000 K: +5.9 meV/atom
* B2 x = 0.5185 at 1500 K: +7.8 meV/atom
* B2 x = 0.5370 at 1000 K: +5.8 meV/atom
* B2 x = 0.5370 at 1500 K: +8.0 meV/atom
* B2 x = 0.4906 at 1000 K: +5.8 meV/atom
* B2 x = 0.4906 at 1500 K: +6.8 meV/atom
* B2 x = 0.4808 at 1000 K: +6.3 meV/atom
* B2 x = 0.4808 at 1500 K: +8.6 meV/atom
* L12 x = 0.7500 at 1000 K: +19.3 meV/atom
* L12 x = 0.7500 at 1500 K: +36.0 meV/atom
* L12 x = 0.7593 at 1000 K: +13.0 meV/atom
* L12 x = 0.7593 at 1500 K: +25.1 meV/atom
* L12 x = 0.7407 at 1000 K: +14.2 meV/atom
* L12 x = 0.7407 at 1500 K: +27.1 meV/atom

## Caveats

* This EAM puts NiAl3 and Ni2Al3 60-120 meV/atom above the 0 K hull (01_hull_0K.tsv), so the Al-rich intermetallics of the experimental diagram are absent; the B2 and L1_2 widths are the point of this example.
* Nothing below the lowest T_stop of the liquids is computed; T_stop(x) is listed in 02B_liquids.json.
* Table check: mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum) (intended).
