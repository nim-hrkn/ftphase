# SevenNet-0 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-31 01:03:37.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 21 cells used, missing []
* liquids (calphy reversible scaling): 11 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '0.8984': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'fccNi': 0.002, 'L12': 0.002, 'fccAl': 0.002, 'NiAl3': 0.002, 'Ni2Al3': 0.002, 'B2': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1360 K; coexistences: fccAl(0.008) + liquid(0.196); liquid(0.197) + NiAl3(0.250)
* pure-A melting bracket (x < 0.02): 2000-2010 K
* invariant reactions:
  * 1240-1250 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+fccAl'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+fccAl']
  * 1250-1260 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+fccAl'] -> ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+fccAl']
  * 1350-1360 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+fccAl'] -> ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid', 'fccAl+liquid']
  * 1440-1450 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid']
  * 1450-1460 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'fccAl+liquid']
  * 1490-1500 K: ['B2+L12', 'B2+liquid', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccAl+liquid']
  * 1680-1690 K: ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+liquid', 'fccAl+liquid']
* two-phase regions at 1000 K: fccAl(0.004)-NiAl3(0.250); NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.471); B2(0.489)-B2(0.500); B2(0.543)-L12(0.753); L12(0.781)-fccNi(0.929)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.490-0.500 at T = 950-1240 K (30 temperatures)
* B2+B2 x = 0.500-0.510 at T = 1690-2000 K (32 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+B2: x_a = 0.488 +/- 0.000, x_b = 0.500 +/- 0.000 (30/30 samples)
* 950 K B2+L12: x_a = 0.543 +/- 0.005, x_b = 0.752 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.931 +/- 0.004 (30/30 samples)
* 950 K Ni2Al3+B2: x_a = 0.400 +/- 0.000, x_b = 0.471 +/- 0.000 (30/30 samples)
* 950 K NiAl3+Ni2Al3: x_a = 0.250 +/- 0.000, x_b = 0.400 +/- 0.000 (30/30 samples)
* 950 K fccAl+NiAl3: x_a = 0.004 +/- 0.000, x_b = 0.250 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.003599297851442262, 'flag': False}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 2.175583928816829e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccAl', 'rmse_eV': 1.1466334093198022e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 0.0034219785135395243, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.001652425194268428, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
