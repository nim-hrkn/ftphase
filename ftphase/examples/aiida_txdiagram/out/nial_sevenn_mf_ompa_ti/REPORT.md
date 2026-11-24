# SevenNet-MF-ompa Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-22 23:00:54.  Classical level, 0.0 GPa, model SevenNet-MF-ompa (modal mpa; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 26 cells used, missing ['s02_fccAl']
* liquids (calphy reversible scaling): 11 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '0.8984': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'B2': 0.002, 'NiAl3': 0.002, 'Ni2Al3': 0.002, 'L12': 0.002, 'fccAl': 0.002, 'liquid': 0.0014, 'fccNi': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 950 K; coexistences: liquid(0.102) + NiAl3(0.250)
* invariant reactions:
  * 980-990 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid']
  * 1060-1070 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid']
  * 1220-1230 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+L12', 'L12+fccNi', 'Ni2Al3+liquid']
  * 1390-1400 K: ['B2+L12', 'B2+Ni2Al3', 'L12+L12', 'L12+fccNi', 'Ni2Al3+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+L12', 'L12+fccNi']
  * 1480-1490 K: ['B2+L12', 'B2+liquid', 'L12+L12', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+L12', 'L12+fccNi', 'fccNi+fccNi']
  * 1520-1530 K: ['B2+L12', 'B2+liquid', 'L12+L12', 'L12+fccNi', 'fccNi+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+L12', 'L12+liquid', 'fccNi+fccNi', 'fccNi+liquid']
  * 1530-1540 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+L12', 'L12+liquid', 'fccNi+fccNi', 'fccNi+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+fccNi', 'fccNi+liquid']
  * 1540-1550 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+fccNi', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid', 'fccNi+fccNi', 'fccNi+liquid']
  * 1570-1580 K: ['B2+B2', 'B2+liquid', 'fccNi+fccNi', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid', 'fccNi+liquid']
  * 1640-1650 K: ['B2+B2', 'B2+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid']
  * 1880-1890 K: ['B2+B2', 'B2+liquid'] -> ['B2+liquid']
* two-phase regions at 1000 K: liquid(0.125)-NiAl3(0.250); NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.487); B2(0.553)-L12(0.719); L12(0.762)-fccNi(0.909)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.490-0.500 at T = 950-1880 K (40 temperatures)
* L12+L12 x = 0.740-0.760 at T = 1410-1530 K (13 temperatures)
* L12+L12 x = 0.750-0.750 at T = 1230-1400 K (18 temperatures)
* fccNi+fccNi x = 0.880-0.960 at T = 1530-1570 K (5 temperatures)
* fccNi+fccNi x = 0.910-1.000 at T = 1490-1520 K (4 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+B2: x_a = 0.491 +/- 0.000, x_b = 0.500 +/- 0.000 (27/30 samples)
* 950 K B2+L12: x_a = 0.541 +/- 0.008, x_b = 0.719 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.761 +/- 0.002, x_b = 0.915 +/- 0.007 (30/30 samples)
* 950 K Ni2Al3+B2: x_a = 0.400 +/- 0.000, x_b = 0.489 +/- 0.002 (30/30 samples)
* 950 K NiAl3+Ni2Al3: x_a = 0.250 +/- 0.000, x_b = 0.400 +/- 0.000 (30/30 samples)
* 950 K liquid+NiAl3: x_a = 0.102 +/- 0.008, x_b = 0.250 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fccAl: 600 K -4.2, 760 K -5.6, 920 K -6.5
* s03_fccNi: 1200 K -2.9, 1500 K -3.2, 1800 K -2.7
* s04_fccNi: 1190 K -1.5, 1339 K -1.6, 1488 K -1.7
* s05_fccNi: 1200 K -1.0, 1364 K -1.2, 1529 K -1.1
* s06_fccNi: 1200 K -1.5, 1385 K -1.6, 1570 K -1.6
* s07_fccNi: 1200 K -1.4, 1406 K -1.6, 1612 K -1.5
* s08_B2: 1300 K -9.7, 1650 K -17.6, 2000 K -31.2
* s09_B2: 1000 K -5.8, 1443 K -13.8, 1886 K -27.8
* s10_B2: 1000 K -6.3, 1443 K -14.9, 1886 K -29.1
* s11_B2: 1000 K -6.0, 1443 K -13.4, 1886 K -23.4
* s12_B2: 1000 K -2.5, 1443 K -6.6, 1886 K -13.0
* s13_B2: 1000 K -4.7, 1443 K -11.3, 1886 K -23.2
* s14_B2: 1000 K -3.8, 1443 K -9.2, 1886 K -18.5
* s15_B2: 1000 K -2.9, 1443 K -7.0, 1886 K -14.7
* s16_B2: 1000 K -2.2, 1443 K -5.7, 1886 K -11.4
* s17_B2: 1000 K -2.7, 1443 K -6.1, 1886 K -10.5
* s18_B2: 1000 K -1.2, 1443 K -3.4, 1886 K -6.7
* s19_B2: 1000 K -0.5, 1443 K -1.5, 1886 K -1.9
* s20_B2: 1000 K +1.9, 1443 K +0.7, 1886 K -1.8
* s21_B2: 1000 K +1.3, 1443 K +1.1, 1886 K -0.2
* s22_L12: 1200 K -5.0, 1475 K -7.0, 1750 K -9.0
* s23_L12: 1200 K -3.8, 1389 K -4.8, 1578 K -5.7
* s24_L12: 1200 K -3.5, 1389 K -4.6, 1578 K -5.8
* s25_Ni2Al3: 900 K -1.1, 1211 K -1.6, 1523 K -1.8
* s26_NiAl3: 900 K +1.1, 1080 K +1.9, 1260 K +3.1

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.003921646455274556, 'flag': False}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 1.538370149106851e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 2.875627660003857e-14, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.0014018759202377407, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
