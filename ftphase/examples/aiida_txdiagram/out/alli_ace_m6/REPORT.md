# ACE Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-24 15:42:12.  Classical level, 0.0 GPa, model AlLi-6gen-18May.yace (ACE).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'Al3Li': 0.002, 'B32': 0.002, 'fcc': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 770 K; coexistences: fcc(0.164) + liquid(0.308); liquid(0.319) + B32(0.483)
* pure-A melting bracket (x < 0.02): 880-890 K
* invariant reactions:
  * 760-770 K: ['B32+fcc', 'fcc+fcc'] -> ['B32+liquid', 'fcc+fcc', 'fcc+liquid']
  * 790-800 K: ['B32+liquid', 'fcc+fcc', 'fcc+liquid'] -> ['B32+liquid', 'fcc+liquid']
  * 850-860 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.025)-fcc(0.118); fcc(0.140)-B32(0.486)
* two-phase regions at 800 K: fcc(0.135)-liquid(0.256); liquid(0.365)-B32(0.487)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.030-0.110 at T = 720-740 K (3 temperatures)
* fcc+fcc x = 0.030-0.120 at T = 700-710 K (2 temperatures)
* fcc+fcc x = 0.040-0.090 at T = 770-770 K (1 temperatures)
* fcc+fcc x = 0.040-0.100 at T = 750-760 K (2 temperatures)
* fcc+fcc x = 0.050-0.090 at T = 780-780 K (1 temperatures)
* fcc+fcc x = 0.060-0.080 at T = 790-790 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.137 +/- 0.032, x_b = 0.486 +/- 0.001 (30/30 samples)
* 700 K fcc+fcc: x_a = 0.025 +/- 0.000, x_b = 0.118 +/- 0.000 (28/30 samples)
* 800 K fcc+B32: x_a = 0.178 +/- 0.000, x_b = 0.480 +/- 0.000 (1/30 samples)
* 800 K fcc+liquid: x_a = 0.122 +/- 0.054, x_b = 0.261 +/- 0.046 (29/30 samples)
* 800 K liquid+B32: x_a = 0.371 +/- 0.026, x_b = 0.488 +/- 0.004 (29/30 samples)
* 900 K fcc+liquid: x_a = 0.013 +/- 0.010, x_b = 0.050 +/- 0.037 (11/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00019738959696049695, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.00013515971257710825, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
