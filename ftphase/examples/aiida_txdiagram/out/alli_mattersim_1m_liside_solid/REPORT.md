# MatterSim-v1.0.0-1M Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 06:21:25.  Classical level, 0.0 GPa, model MatterSim-v1.0.0-1M (float32, ML-IAP).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'Al3Li': 0.002, 'Al2Li3': 0.002, 'bcc': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002}

## Key numbers

* invariant reactions:
  * 400-410 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al3Li+B32', 'Al3Li+fcc', 'Al4Li9+bcc'] -> ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc']
  * 720-730 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc']
  * 900-910 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc'] -> ['B32+bcc', 'B32+fcc']
* two-phase regions at 700 K: fcc(0.250)-B32(0.495); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-Al4Li9(0.692); Al4Li9(0.692)-bcc(0.758)
* two-phase regions at 800 K: fcc(0.250)-B32(0.503); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 900 K: fcc(0.250)-B32(0.518); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 1000 K: fcc(0.250)-B32(0.562); B32(0.562)-bcc(0.750)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (12/30 samples)
* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.754 +/- 0.004 (17/30 samples)
* 700 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.768 +/- 0.019 (13/30 samples)
* 700 K B32+Al2Li3: x_a = 0.562 +/- 0.005, x_b = 0.600 +/- 0.000 (29/30 samples)
* 700 K B32+Al4Li9: x_a = 0.562 +/- 0.000, x_b = 0.692 +/- 0.000 (1/30 samples)
* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.496 +/- 0.002 (30/30 samples)
* 800 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (3/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.001 (21/30 samples)
* 800 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.771 +/- 0.014 (3/30 samples)
* 800 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (24/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (6/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.504 +/- 0.003 (30/30 samples)
* 900 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (1/30 samples)
* 900 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (20/30 samples)
* 900 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.766 +/- 0.000 (1/30 samples)
* 900 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (21/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (9/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.520 +/- 0.004 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 0.001333954915602093, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 6.562522196906556e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
