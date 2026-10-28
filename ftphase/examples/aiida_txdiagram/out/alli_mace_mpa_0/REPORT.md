# MACE-MPA-0 medium Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-28 22:54:19.  Classical level, 0.0 GPa, model MACE-MPA-0 medium (float32).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014, 'Al3Li': 0.002, 'B32': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 780 K; coexistences: fcc(0.238) + liquid(0.385); liquid(0.386) + B32(0.490)
* pure-A melting bracket (x < 0.02): 1030-1040 K
* invariant reactions:
  * 770-780 K: ['B32+fcc'] -> ['B32+liquid', 'fcc+liquid']
  * 820-830 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.209)-B32(0.492)
* two-phase regions at 800 K: fcc(0.231)-liquid(0.372); liquid(0.420)-B32(0.496)
* two-phase regions at 900 K: fcc(0.180)-liquid(0.283)
* two-phase regions at 1000 K: fcc(0.069)-liquid(0.109)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.209 +/- 0.011, x_b = 0.492 +/- 0.002 (30/30 samples)
* 800 K fcc+B32: x_a = 0.242 +/- 0.010, x_b = 0.489 +/- 0.004 (3/30 samples)
* 800 K fcc+liquid: x_a = 0.229 +/- 0.011, x_b = 0.370 +/- 0.016 (27/30 samples)
* 800 K liquid+B32: x_a = 0.429 +/- 0.036, x_b = 0.500 +/- 0.015 (27/30 samples)
* 900 K fcc+liquid: x_a = 0.180 +/- 0.019, x_b = 0.282 +/- 0.026 (30/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00034091984711318794, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.00014727868727369892, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
