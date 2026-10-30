# GRACE-FS-OAM Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-30 19:25:21.  Classical level, 0.0 GPa, model GRACE-FS-OAM (foundation, FS, 6 A).

## Inputs

* solids (QHA, lowered to the classical level): 21 cells used, missing []
* liquids (calphy reversible scaling): 11 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '0.8984': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'Ni2Al3': 0.002, 'L12': 0.002, 'fccAl': 0.002, 'fccNi': 0.002, 'liquid': 0.0014, 'B2': 0.002, 'NiAl3': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 950 K; coexistences: fccAl(0.000) + liquid(0.163)
* pure-A melting bracket (x < 0.02): 2000-2010 K
* invariant reactions:
  * 1040-1050 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'L12+fccNi', 'fccAl+liquid']
  * 1090-1100 K: ['B2+L12', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid']
  * 1180-1190 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'L12+fccNi', 'fccAl+liquid']
  * 1290-1300 K: ['B2+L12', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid']
  * 1530-1540 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+liquid', 'L12+fccNi', 'L12+liquid', 'fccAl+liquid']
  * 1670-1680 K: ['B2+liquid', 'L12+fccNi', 'L12+liquid', 'fccAl+liquid'] -> ['B2+liquid', 'L12+liquid', 'fccAl+liquid', 'fccNi+liquid']
  * 1730-1740 K: ['B2+liquid', 'L12+liquid', 'fccAl+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'L12+liquid', 'fccAl+liquid']
  * 1800-1810 K: ['B2+liquid', 'L12+liquid', 'fccAl+liquid'] -> ['B2+liquid', 'fccAl+liquid']
* two-phase regions at 1000 K: fccAl(0.000)-liquid(0.164); NiAl3(0.250)-B2(0.490); B2(0.611)-L12(0.758); L12(0.781)-fccNi(0.914)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.757 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.916 +/- 0.004 (30/30 samples)
* 950 K NiAl3+B2: x_a = 0.250 +/- 0.000, x_b = 0.491 +/- 0.001 (30/30 samples)
* 950 K fccAl+NiAl3: x_a = 0.000 +/- 0.000, x_b = 0.250 +/- 0.000 (4/30 samples)
* 950 K fccAl+liquid: x_a = 0.000 +/- 0.000, x_b = 0.161 +/- 0.007 (26/30 samples)
* 950 K liquid+NiAl3: x_a = 0.196 +/- 0.005, x_b = 0.250 +/- 0.000 (26/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.0018858234792835024, 'flag': False}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 1.1466334093198022e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccAl', 'rmse_eV': 5.127900497022837e-16, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 0.004735388256222752, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.0006706419762477988, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
