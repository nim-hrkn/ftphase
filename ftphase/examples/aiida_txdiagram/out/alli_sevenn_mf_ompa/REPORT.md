# SevenNet-MF-ompa Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-26 22:06:56.  Classical level, 0.0 GPa, model SevenNet-MF-ompa (modal mpa; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'B32': 0.002, 'Al3Li': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 860 K; coexistences: fcc(0.165) + liquid(0.318); liquid(0.335) + B32(0.503)
* invariant reactions:
  * 850-860 K: ['B32+fcc'] -> ['B32+liquid', 'fcc+liquid']
  * 910-920 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.132)-B32(0.503)
* two-phase regions at 800 K: fcc(0.154)-B32(0.502)
* two-phase regions at 900 K: fcc(0.140)-liquid(0.256); liquid(0.425)-B32(0.509)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.132 +/- 0.006, x_b = 0.503 +/- 0.001 (30/30 samples)
* 800 K fcc+B32: x_a = 0.155 +/- 0.006, x_b = 0.502 +/- 0.001 (30/30 samples)
* 900 K fcc+liquid: x_a = 0.137 +/- 0.021, x_b = 0.251 +/- 0.045 (30/30 samples)
* 900 K liquid+B32: x_a = 0.435 +/- 0.046, x_b = 0.513 +/- 0.009 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00034424868976529145, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 8.460163383851703e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
