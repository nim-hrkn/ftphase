# GRACE-2L-OMAT-medium-base-fp64 Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-25 21:18:20.  Classical level, 0.0 GPa, model GRACE-2L-OMAT-medium-base-fp64 (foundation, 2 layers, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014, 'Al3Li': 0.002, 'B32': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 760 K; coexistences: fcc(0.181) + liquid(0.354); liquid(0.373) + B32(0.498)
* invariant reactions:
  * 750-760 K: ['B32+fcc'] -> ['B32+liquid', 'fcc+liquid']
  * 810-820 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.168)-B32(0.497)
* two-phase regions at 800 K: fcc(0.162)-liquid(0.308); liquid(0.448)-B32(0.508)
* two-phase regions at 900 K: fcc(0.049)-liquid(0.084)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.168 +/- 0.010, x_b = 0.497 +/- 0.001 (30/30 samples)
* 800 K fcc+liquid: x_a = 0.162 +/- 0.013, x_b = 0.307 +/- 0.022 (30/30 samples)
* 800 K liquid+B32: x_a = 0.450 +/- 0.041, x_b = 0.513 +/- 0.014 (30/30 samples)
* 900 K fcc+liquid: x_a = 0.054 +/- 0.030, x_b = 0.093 +/- 0.054 (26/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0002872415305533847, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.00035628792012138837, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
