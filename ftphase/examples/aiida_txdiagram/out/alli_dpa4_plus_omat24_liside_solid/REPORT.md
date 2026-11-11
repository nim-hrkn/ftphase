# DPA4-Plus-OMat24 v20260805 Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 06:40:25.  Classical level, 0.0 GPa, model DPA4-Plus-OMat24 v20260805 (deepmd 3.2.0, .pt2).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'Al3Li': 0.002, 'Al2Li3': 0.002, 'bcc': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002}

## Key numbers

* invariant reactions:
  * 410-420 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al3Li+B32', 'Al3Li+fcc', 'Al4Li9+bcc'] -> ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc']
  * 710-720 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc']
  * 910-920 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc'] -> ['B32+bcc', 'B32+fcc']
  * 960-970 K: ['B32+bcc', 'B32+fcc'] -> ['B32+bcc', 'B32+fcc', 'bcc+bcc']
  * 1070-1080 K: ['B32+bcc', 'B32+fcc', 'bcc+bcc'] -> ['B32+bcc', 'B32+fcc']
* two-phase regions at 700 K: fcc(0.162)-B32(0.514); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-Al4Li9(0.692); Al4Li9(0.692)-bcc(0.750)
* two-phase regions at 800 K: fcc(0.195)-B32(0.532); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 900 K: fcc(0.226)-B32(0.562); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 1000 K: fcc(0.250)-B32(0.562); B32(0.562)-bcc(0.750); bcc(0.750)-bcc(0.858)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* bcc+bcc x = 0.750-0.780 at T = 970-970 K (1 temperatures)
* bcc+bcc x = 0.750-0.850 at T = 980-980 K (1 temperatures)
* bcc+bcc x = 0.750-0.860 at T = 990-1020 K (4 temperatures)
* bcc+bcc x = 0.750-0.870 at T = 1030-1070 K (5 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (13/30 samples)
* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (16/30 samples)
* 700 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.761 +/- 0.029 (14/30 samples)
* 700 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (29/30 samples)
* 700 K B32+Al4Li9: x_a = 0.562 +/- 0.000, x_b = 0.692 +/- 0.000 (1/30 samples)
* 700 K fcc+B32: x_a = 0.165 +/- 0.009, x_b = 0.515 +/- 0.002 (30/30 samples)
* 800 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (3/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (23/30 samples)
* 800 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.752 +/- 0.003 (3/30 samples)
* 800 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (26/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (4/30 samples)
* 800 K fcc+B32: x_a = 0.198 +/- 0.009, x_b = 0.535 +/- 0.007 (30/30 samples)
* 900 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (1/30 samples)
* 900 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (19/30 samples)
* 900 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.750 +/- 0.000 (1/30 samples)
* 900 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (20/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (10/30 samples)
* 900 K fcc+B32: x_a = 0.229 +/- 0.009, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 2.5639502485114184e-16, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 0.000557720949998968, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0002509444936056153, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
