# ACE Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 11:52:39.  Classical level, 0.0 GPa, model AlLi-6gen-18May.yace (ACE).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'Al3Li': 0.002, 'Al2Li3': 0.002, 'bcc': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002}

## Key numbers

* invariant reactions:
  * 350-360 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al3Li+B32', 'Al3Li+fcc', 'Al4Li9+bcc'] -> ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc']
  * 670-680 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc'] -> ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc', 'fcc+fcc']
  * 750-760 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc', 'fcc+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc', 'fcc+fcc']
  * 790-800 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc', 'fcc+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc']
  * 810-820 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc'] -> ['B32+bcc', 'B32+fcc']
  * 1070-1080 K: ['B32+bcc', 'B32+fcc'] -> ['B32+B32', 'B32+bcc', 'B32+fcc']
* two-phase regions at 700 K: fcc(0.025)-fcc(0.118); fcc(0.140)-B32(0.486); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-Al4Li9(0.692); Al4Li9(0.692)-bcc(0.750)
* two-phase regions at 800 K: fcc(0.177)-B32(0.480); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 900 K: fcc(0.203)-B32(0.465); B32(0.562)-bcc(0.750)
* two-phase regions at 1000 K: fcc(0.224)-B32(0.438); B32(0.562)-bcc(0.750)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B32+B32 x = 0.440-0.560 at T = 1080-1100 K (3 temperatures)
* fcc+fcc x = 0.020-0.120 at T = 680-690 K (2 temperatures)
* fcc+fcc x = 0.030-0.110 at T = 720-740 K (3 temperatures)
* fcc+fcc x = 0.030-0.120 at T = 700-710 K (2 temperatures)
* fcc+fcc x = 0.040-0.090 at T = 770-770 K (1 temperatures)
* fcc+fcc x = 0.040-0.100 at T = 750-760 K (2 temperatures)
* fcc+fcc x = 0.050-0.090 at T = 780-780 K (1 temperatures)
* fcc+fcc x = 0.060-0.080 at T = 790-790 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (19/30 samples)
* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (10/30 samples)
* 700 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.765 +/- 0.026 (20/30 samples)
* 700 K B32+Al2Li3: x_a = 0.561 +/- 0.005, x_b = 0.600 +/- 0.000 (29/30 samples)
* 700 K B32+Al4Li9: x_a = 0.562 +/- 0.000, x_b = 0.692 +/- 0.000 (1/30 samples)
* 700 K fcc+B32: x_a = 0.133 +/- 0.038, x_b = 0.486 +/- 0.001 (30/30 samples)
* 700 K fcc+fcc: x_a = 0.025 +/- 0.000, x_b = 0.118 +/- 0.000 (27/30 samples)
* 800 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (3/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (17/30 samples)
* 800 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.769 +/- 0.026 (3/30 samples)
* 800 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (20/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (10/30 samples)
* 800 K fcc+B32: x_a = 0.179 +/- 0.008, x_b = 0.480 +/- 0.002 (30/30 samples)
* 900 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (1/30 samples)
* 900 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (6/30 samples)
* 900 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.750 +/- 0.000 (1/30 samples)
* 900 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (7/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (23/30 samples)
* 900 K fcc+B32: x_a = 0.205 +/- 0.007, x_b = 0.466 +/- 0.006 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 2.3777096446126297e-15, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00019738954475494115, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
