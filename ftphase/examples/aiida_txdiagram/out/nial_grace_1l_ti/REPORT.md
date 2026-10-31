# GRACE-1L-OMAT-medium-base-fp64 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-01 04:15:43.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 20 cells used, missing ['s19_Ni2Al3']
* liquids (calphy reversible scaling): 10 runs used, missing ['lqd_x0_90']; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'fccNi': 0.002, 'NiAl3': 0.002, 'liquid': 0.0014, 'L12': 0.002, 'B2': 0.002, 'fccAl': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 950 K; coexistences: liquid(0.091) + NiAl3(0.250)
* invariant reactions:
  * 1040-1050 K: ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid'] -> ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi']
  * 1090-1100 K: ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1640-1650 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid']
  * 1660-1670 K: ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+liquid', 'fccNi+liquid']
  * 1700-1710 K: ['B2+B2', 'B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+liquid']
  * 1760-1770 K: ['B2+B2', 'B2+liquid', 'L12+liquid'] -> ['B2+B2', 'B2+liquid']
  * 1940-1950 K: ['B2+B2', 'B2+liquid'] -> ['B2+liquid']
* two-phase regions at 1000 K: liquid(0.133)-NiAl3(0.250); NiAl3(0.250)-B2(0.471); B2(0.484)-B2(0.500); B2(0.611)-L12(0.756); L12(0.781)-fccNi(0.988)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.470-0.500 at T = 1570-1940 K (38 temperatures)
* B2+B2 x = 0.480-0.500 at T = 950-1560 K (62 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+B2: x_a = 0.483 +/- 0.000, x_b = 0.500 +/- 0.000 (30/30 samples)
* 950 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.755 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.992 +/- 0.003 (30/30 samples)
* 950 K NiAl3+B2: x_a = 0.250 +/- 0.000, x_b = 0.471 +/- 0.000 (30/30 samples)
* 950 K liquid+NiAl3: x_a = 0.091 +/- 0.010, x_b = 0.250 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fccAl: 600 K -0.2, 760 K +0.1, 920 K +0.8
* s03_fccNi: 1200 K +0.9, 1500 K +1.6, 1800 K +2.9
* s08_B2: 1300 K -8.2, 1650 K -16.8, 2000 K -37.3
* s16_L12: 1200 K -0.5, 1475 K -0.4, 1750 K -0.4

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.006174969697166463, 'flag': True}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 1.4503892858778862e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccAl', 'rmse_eV': 6.280369834735101e-16, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 0.003082968752634313, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.0010561998469575385, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
