# GRACE-1L-OMAT-medium-base-fp64 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-06 04:52:30.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 19 cells used, missing ['s01_fccAl', 's02_fccAl']
* liquids (calphy reversible scaling): 10 runs used, missing ['lqd_x0_90']; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'B2': 0.002, 'Ni2Al3': 0.002, 'fccNi': 0.002, 'L12': 0.002, 'NiAl3': 0.002, 'fccAl': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 950 K; coexistences: liquid(0.070) + NiAl3(0.250)
* invariant reactions:
  * 1080-1090 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3']
  * 1090-1100 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid']
  * 1110-1120 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid']
  * 1370-1380 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1590-1600 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid']
  * 1610-1620 K: ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+B2', 'B2+liquid', 'fccNi+liquid']
  * 1710-1720 K: ['B2+B2', 'B2+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid']
  * 1790-1800 K: ['B2+B2', 'B2+liquid'] -> ['B2+liquid']
* two-phase regions at 1000 K: liquid(0.099)-NiAl3(0.250); NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.476); B2(0.484)-B2(0.500); B2(0.611)-L12(0.756); L12(0.781)-fccNi(0.988)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.480-0.500 at T = 950-1270 K (33 temperatures)
* B2+B2 x = 0.490-0.500 at T = 1280-1790 K (52 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+B2: x_a = 0.483 +/- 0.000, x_b = 0.500 +/- 0.000 (27/30 samples)
* 950 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.755 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.992 +/- 0.001 (30/30 samples)
* 950 K Ni2Al3+B2: x_a = 0.400 +/- 0.000, x_b = 0.479 +/- 0.004 (30/30 samples)
* 950 K NiAl3+Ni2Al3: x_a = 0.250 +/- 0.000, x_b = 0.400 +/- 0.000 (30/30 samples)
* 950 K liquid+NiAl3: x_a = 0.070 +/- 0.009, x_b = 0.250 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fccAl: 600 K -0.2, 760 K +0.1, 920 K +0.8
* s03_fccNi: 1200 K +0.9, 1500 K +1.6, 1800 K +2.9
* s04_fccNi: 1200 K +0.5, 1458 K +0.7, 1715 K +1.3
* s05_fccNi: 1200 K +0.8, 1458 K +1.4, 1715 K +2.2
* s06_fccNi: 1200 K +2.1, 1458 K +3.2, 1715 K +4.6
* s07_fccNi: 1200 K +1.4, 1458 K +2.3, 1715 K +3.4
* s08_B2: 1300 K -8.2, 1650 K -16.8, 2000 K -37.3
* s09_B2: 1300 K -9.8, 1548 K -15.2, 1797 K -23.2
* s10_B2: 1300 K -9.8, 1548 K -14.9, 1797 K -22.0
* s11_B2: 1300 K -9.3, 1548 K -13.3, 1797 K -18.2
* s12_B2: 1300 K -5.4, 1548 K -7.8, 1797 K -10.8
* s13_B2: 1300 K -8.1, 1548 K -12.8, 1797 K -19.7
* s14_B2: 1300 K -7.8, 1548 K -11.9, 1797 K -17.4
* s15_B2: 1300 K -5.9, 1548 K -9.0, 1797 K -13.4
* s16_L12: 1200 K -0.5, 1475 K -0.4, 1750 K -0.4
* s17_L12: 1200 K +1.8, 1408 K +2.3, 1615 K +2.9
* s18_L12: 1200 K -0.7, 1408 K -0.9, 1615 K -1.3
* s20_NiAl3: 900 K +4.6, 1051 K +6.3, 1202 K +8.3

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.0019255087069492544, 'flag': False}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 1.8488908177493114e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 0.0033827823880608126, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.0010561998469575385, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
