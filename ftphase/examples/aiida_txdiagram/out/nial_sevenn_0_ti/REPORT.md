# SevenNet-0 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-06 04:54:18.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 19 cells used, missing ['s01_fccAl', 's02_fccAl']
* liquids (calphy reversible scaling): 11 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '0.8984': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'B2': 0.002, 'Ni2Al3': 0.002, 'fccNi': 0.002, 'L12': 0.002, 'NiAl3': 0.002, 'fccAl': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: liquid(0.262) + B2(0.500)
* invariant reactions:
  * 970-980 K: ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3']
  * 980-990 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3']
  * 1010-1020 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi']
  * 1090-1100 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1280-1290 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1290-1300 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1310-1320 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi', 'fccNi+fccNi']
  * 1350-1360 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi', 'fccNi+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1460-1470 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid']
  * 1490-1500 K: ['B2+B2', 'B2+L12', 'B2+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+liquid']
  * 1560-1570 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+liquid'] -> ['B2+B2', 'B2+liquid']
* two-phase regions at 1000 K: NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.499); B2(0.543)-L12(0.753); L12(0.781)-fccNi(0.929)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.490-0.500 at T = 950-1860 K (61 temperatures)
* B2+B2 x = 0.490-0.510 at T = 1870-1960 K (10 temperatures)
* B2+B2 x = 0.500-0.510 at T = 1100-1280 K (18 temperatures)
* B2+B2 x = 0.500-0.520 at T = 1270-1270 K (1 temperatures)
* fccNi+fccNi x = 0.940-0.990 at T = 1320-1350 K (4 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+B2: x_a = 0.488 +/- 0.000, x_b = 0.500 +/- 0.000 (30/30 samples)
* 950 K B2+L12: x_a = 0.545 +/- 0.006, x_b = 0.752 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.932 +/- 0.003 (30/30 samples)
* 950 K Ni2Al3+B2: x_a = 0.400 +/- 0.000, x_b = 0.473 +/- 0.008 (12/30 samples)
* 950 K NiAl3+B2: x_a = 0.250 +/- 0.000, x_b = 0.471 +/- 0.000 (18/30 samples)
* 950 K NiAl3+Ni2Al3: x_a = 0.250 +/- 0.000, x_b = 0.400 +/- 0.000 (11/30 samples)
* 950 K liquid+Ni2Al3: x_a = 0.199 +/- 0.000, x_b = 0.400 +/- 0.000 (1/30 samples)
* 950 K liquid+NiAl3: x_a = 0.199 +/- 0.000, x_b = 0.250 +/- 0.000 (29/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fccAl: 600 K -34.4, 760 K -53.1, 920 K -73.4
* s03_fccNi: 1200 K +14.2, 1500 K +24.0, 1800 K +36.2
* s04_fccNi: 1052 K -9.7, 1184 K -11.9, 1315 K -14.3
* s05_fccNi: 1081 K -4.8, 1216 K -5.9, 1351 K -7.0
* s06_fccNi: 1169 K +2.1, 1315 K +2.8, 1461 K +3.6
* s07_fccNi: 1169 K +9.1, 1315 K +11.8, 1461 K +15.0
* s08_B2: 1300 K -57.4, 1650 K -88.3, 2000 K -122.6
* s09_B2: 1300 K -53.4, 1632 K -80.3, 1964 K -109.8
* s10_B2: 1300 K -40.0, 1632 K -58.8, 1964 K -79.2
* s11_B2: 1300 K -29.2, 1632 K -43.6, 1964 K -59.4
* s12_B2: 1300 K -23.7, 1632 K -35.3, 1964 K -47.5
* s13_B2: 1300 K -54.5, 1632 K -81.4, 1964 K -111.1
* s14_B2: 1000 K -27.9, 1482 K -56.6, 1964 K -90.5
* s15_B2: 1000 K -25.8, 1482 K -51.6, 1964 K -82.1
* s16_L12: 1200 K -29.1, 1475 K -39.1, 1750 K -48.9
* s17_L12: 1200 K -20.7, 1383 K -25.7, 1567 K -30.9
* s18_L12: 1200 K -24.2, 1383 K -29.8, 1567 K -35.5
* s19_Ni2Al3: 900 K -18.1, 1228 K -30.5, 1555 K -44.8
* s20_NiAl3: 900 K -26.7, 1068 K -33.6, 1237 K -40.2

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.002003116309779537, 'flag': False}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 7.251946429389431e-16, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.001652425194268428, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
