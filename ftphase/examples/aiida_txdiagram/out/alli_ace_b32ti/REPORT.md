# ACE Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-24 01:54:28.  Classical level, 0.0 GPa, model AlLi-6gen-18May.yace (ACE).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'liquid': 0.0014, 'fcc': 0.002, 'Al3Li': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 770 K; coexistences: fcc(0.164) + liquid(0.316); liquid(0.341) + B32(0.490)
* pure-A melting bracket (x < 0.02): 880-890 K
* invariant reactions:
  * 760-770 K: ['B32+fcc', 'fcc+fcc'] -> ['B32+liquid', 'fcc+fcc', 'fcc+liquid']
  * 790-800 K: ['B32+liquid', 'fcc+fcc', 'fcc+liquid'] -> ['B32+liquid', 'fcc+liquid']
  * 840-850 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.025)-fcc(0.118); fcc(0.147)-B32(0.490)
* two-phase regions at 800 K: fcc(0.136)-liquid(0.257); liquid(0.381)-B32(0.494)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.030-0.110 at T = 720-740 K (3 temperatures)
* fcc+fcc x = 0.030-0.120 at T = 700-710 K (2 temperatures)
* fcc+fcc x = 0.040-0.090 at T = 770-770 K (1 temperatures)
* fcc+fcc x = 0.040-0.100 at T = 750-760 K (2 temperatures)
* fcc+fcc x = 0.050-0.090 at T = 780-780 K (1 temperatures)
* fcc+fcc x = 0.060-0.080 at T = 790-790 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al3Li+B32: x_a = 0.250 +/- 0.000, x_b = 0.490 +/- 0.000 (1/30 samples)
* 700 K fcc+Al3Li: x_a = 0.121 +/- 0.000, x_b = 0.250 +/- 0.000 (1/30 samples)
* 700 K fcc+B32: x_a = 0.147 +/- 0.026, x_b = 0.490 +/- 0.001 (29/30 samples)
* 700 K fcc+fcc: x_a = 0.025 +/- 0.000, x_b = 0.118 +/- 0.000 (29/30 samples)
* 800 K fcc+B32: x_a = 0.184 +/- 0.000, x_b = 0.488 +/- 0.000 (1/30 samples)
* 800 K fcc+liquid: x_a = 0.137 +/- 0.037, x_b = 0.266 +/- 0.038 (29/30 samples)
* 800 K liquid+B32: x_a = 0.384 +/- 0.023, x_b = 0.495 +/- 0.003 (29/30 samples)
* 900 K fcc+liquid: x_a = 0.012 +/- 0.010, x_b = 0.049 +/- 0.039 (11/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s10_B32: 700 K -1.2, 790 K -1.3, 880 K -1.3
* s11_B32: 700 K -2.7, 790 K -3.0, 880 K -3.2
* s12_B32: 700 K -0.3, 790 K -0.2, 880 K -0.1

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00019738959696049695, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.00036765356134874994, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
