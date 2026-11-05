# GRACE-FS-OAM Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-06 04:50:48.  Classical level, 0.0 GPa, model GRACE-FS-OAM (foundation, FS, 6 A).

## Inputs

* solids (QHA, lowered to the classical level): 19 cells used, missing ['s01_fccAl', 's02_fccAl']
* liquids (calphy reversible scaling): 11 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '0.8984': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'B2': 0.002, 'fccNi': 0.002, 'Ni2Al3': 0.002, 'L12': 0.002, 'NiAl3': 0.002, 'fccAl': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: liquid(0.290) + B2(0.493)
* invariant reactions:
  * 1030-1040 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi'] -> ['B2+L12', 'L12+fccNi']
  * 1090-1100 K: ['B2+L12', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1180-1190 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'L12+fccNi']
  * 1280-1290 K: ['B2+L12', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'L12+fccNi']
  * 1290-1300 K: ['B2+B2', 'B2+L12', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1440-1450 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid']
  * 1480-1490 K: ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid', 'fccNi+fccNi']
  * 1510-1520 K: ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid', 'fccNi+fccNi'] -> ['B2+B2', 'B2+liquid', 'fccNi+fccNi', 'fccNi+liquid']
  * 1540-1550 K: ['B2+B2', 'B2+liquid', 'fccNi+fccNi', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+fccNi', 'fccNi+liquid']
  * 1590-1600 K: ['B2+liquid', 'fccNi+fccNi', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
  * 1650-1660 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid']
* two-phase regions at 1000 K: NiAl3(0.250)-B2(0.491); B2(0.611)-L12(0.758); L12(0.781)-fccNi(0.914)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.490-0.500 at T = 1290-1540 K (26 temperatures)
* fccNi+fccNi x = 0.910-1.000 at T = 1490-1590 K (11 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+B2: x_a = 0.489 +/- 0.000, x_b = 0.500 +/- 0.000 (2/30 samples)
* 950 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.757 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.918 +/- 0.005 (30/30 samples)
* 950 K NiAl3+B2: x_a = 0.250 +/- 0.000, x_b = 0.491 +/- 0.001 (30/30 samples)
* 950 K liquid+NiAl3: x_a = 0.188 +/- 0.014, x_b = 0.250 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fccAl: 500 K -17.4, 640 K -27.6, 780 K -39.6
* s03_fccNi: 1200 K -3.7, 1500 K -6.3, 1800 K -9.4
* s04_fccNi: 1191 K -3.5, 1340 K -4.4, 1489 K -5.3
* s05_fccNi: 1200 K -3.9, 1427 K -5.5, 1654 K -7.2
* s06_fccNi: 1200 K -4.0, 1427 K -5.8, 1654 K -7.9
* s07_fccNi: 1200 K -3.6, 1427 K -5.2, 1654 K -7.3
* s08_B2: 1300 K -22.6, 1650 K -37.3, 2000 K -53.9
* s09_B2: 1300 K -20.2, 1485 K -27.2, 1670 K -35.0
* s10_B2: 1300 K -16.8, 1485 K -22.7, 1670 K -29.4
* s11_B2: 1300 K -11.0, 1485 K -14.6, 1670 K -18.8
* s12_B2: 1300 K -8.5, 1485 K -11.1, 1670 K -14.0
* s13_B2: 1300 K -19.0, 1485 K -25.5, 1670 K -32.6
* s14_B2: 1300 K -13.8, 1485 K -18.6, 1670 K -24.0
* s15_B2: 1300 K -11.1, 1485 K -15.1, 1670 K -19.7
* s16_L12: 1200 K -5.3, 1475 K -8.2, 1750 K -11.7
* s17_L12: 1200 K -5.5, 1356 K -7.1, 1512 K -8.8
* s18_L12: 1200 K -6.3, 1356 K -7.9, 1512 K -9.7
* s19_Ni2Al3: 900 K +1.0, 1108 K +1.8, 1316 K +2.9
* s20_NiAl3: 828 K -0.0, 932 K +0.1, 1035 K +0.2

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.0016716664309668998, 'flag': False}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 1.538370149106851e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 3.971558107329431e-14, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.0006706419762477988, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
