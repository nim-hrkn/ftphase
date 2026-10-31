# GRACE-FS-OAM Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-01 05:15:14.  Classical level, 0.0 GPa, model GRACE-FS-OAM (foundation, FS, 6 A).

## Inputs

* solids (QHA, lowered to the classical level): 21 cells used, missing []
* liquids (calphy reversible scaling): 11 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '0.8984': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'L12': 0.002, 'NiAl3': 0.002, 'fccAl': 0.002, 'fccNi': 0.002, 'Ni2Al3': 0.002, 'B2': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: liquid(0.290) + B2(0.493)
* invariant reactions:
  * 1040-1050 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi'] -> ['B2+L12', 'L12+fccNi']
  * 1090-1100 K: ['B2+L12', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1180-1190 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'L12+fccNi']
  * 1280-1290 K: ['B2+L12', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'L12+fccNi']
  * 1290-1300 K: ['B2+B2', 'B2+L12', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1580-1590 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid']
  * 1650-1660 K: ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid', 'fccNi+liquid']
  * 1680-1690 K: ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+liquid', 'fccNi+liquid']
  * 1720-1730 K: ['B2+B2', 'B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+liquid']
  * 1790-1800 K: ['B2+B2', 'B2+liquid', 'L12+liquid'] -> ['B2+B2', 'B2+liquid', 'L12+liquid', 'fccNi+liquid']
  * 1800-1810 K: ['B2+B2', 'B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid', 'fccNi+liquid']
  * 1810-1820 K: ['B2+B2', 'B2+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid']
  * 1850-1860 K: ['B2+B2', 'B2+liquid'] -> ['B2+liquid']
* two-phase regions at 1000 K: NiAl3(0.250)-B2(0.490); B2(0.611)-L12(0.758); L12(0.781)-fccNi(0.914)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.470-0.500 at T = 1300-1850 K (55 temperatures)
* B2+B2 x = 0.480-0.500 at T = 1290-1420 K (2 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.756 +/- 0.001 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.917 +/- 0.005 (30/30 samples)
* 950 K NiAl3+B2: x_a = 0.250 +/- 0.000, x_b = 0.491 +/- 0.001 (30/30 samples)
* 950 K liquid+NiAl3: x_a = 0.194 +/- 0.008, x_b = 0.250 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fccAl: 500 K -17.4, 640 K -27.6, 780 K -39.6
* s03_fccNi: 1200 K -3.7, 1500 K -6.3, 1800 K -9.4
* s08_B2: 1300 K -22.6, 1650 K -37.3, 2000 K -53.9
* s16_L12: 1200 K -5.3, 1475 K -8.2, 1750 K -11.7

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.010365736244914001, 'flag': True}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 1.538370149106851e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccAl', 'rmse_eV': 8.881784197001252e-16, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 0.004400532021976854, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.0006706419762477988, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
