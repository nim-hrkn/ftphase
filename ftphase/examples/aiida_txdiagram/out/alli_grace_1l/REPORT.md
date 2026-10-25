# GRACE-1L-OMAT-medium-base-fp64 Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-26 02:34:22.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'B32': 0.002, 'Al3Li': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 730 K; coexistences: fcc(0.199) + liquid(0.327); liquid(0.341) + B32(0.477)
* invariant reactions:
  * 720-730 K: ['B32+fcc'] -> ['B32+liquid', 'fcc+liquid']
  * 810-820 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.194)-B32(0.477)
* two-phase regions at 800 K: fcc(0.138)-liquid(0.233); liquid(0.449)-B32(0.496)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al3Li+B32: x_a = 0.250 +/- 0.000, x_b = 0.477 +/- 0.000 (1/30 samples)
* 700 K fcc+Al3Li: x_a = 0.187 +/- 0.000, x_b = 0.250 +/- 0.000 (1/30 samples)
* 700 K fcc+B32: x_a = 0.195 +/- 0.011, x_b = 0.478 +/- 0.002 (26/30 samples)
* 700 K fcc+liquid: x_a = 0.180 +/- 0.006, x_b = 0.317 +/- 0.006 (3/30 samples)
* 700 K liquid+B32: x_a = 0.344 +/- 0.004, x_b = 0.480 +/- 0.001 (3/30 samples)
* 800 K fcc+liquid: x_a = 0.136 +/- 0.032, x_b = 0.228 +/- 0.043 (30/30 samples)
* 800 K liquid+B32: x_a = 0.456 +/- 0.037, x_b = 0.504 +/- 0.019 (30/30 samples)
* 900 K fcc+liquid: x_a = 0.013 +/- 0.000, x_b = 0.018 +/- 0.000 (1/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0002977868563275596, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.00023941768093761455, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
