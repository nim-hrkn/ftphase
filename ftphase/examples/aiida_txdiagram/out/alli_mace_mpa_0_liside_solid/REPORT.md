# MACE-MPA-0 medium Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 03:44:41.  Classical level, 0.0 GPa, model MACE-MPA-0 medium (float32, ML-IAP, cuEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'bcc': 0.002, 'Al3Li': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002, 'Al2Li3': 0.002}

## Key numbers

* invariant reactions:
  * 660-670 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc']
  * 960-970 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc'] -> ['B32+bcc', 'B32+fcc']
  * 1000-1010 K: ['B32+bcc', 'B32+fcc'] -> ['B32+B32', 'B32+bcc', 'B32+fcc']
* two-phase regions at 700 K: fcc(0.209)-B32(0.492); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 800 K: fcc(0.246)-B32(0.489); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 900 K: fcc(0.250)-B32(0.483); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 1000 K: fcc(0.250)-B32(0.438); B32(0.562)-bcc(0.750)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B32+B32 x = 0.440-0.560 at T = 1010-1100 K (10 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (6/30 samples)
* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.751 +/- 0.004 (24/30 samples)
* 700 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.762 +/- 0.015 (6/30 samples)
* 700 K B32+Al2Li3: x_a = 0.554 +/- 0.011, x_b = 0.600 +/- 0.000 (30/30 samples)
* 700 K fcc+B32: x_a = 0.213 +/- 0.012, x_b = 0.493 +/- 0.002 (30/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (27/30 samples)
* 800 K B32+Al2Li3: x_a = 0.562 +/- 0.004, x_b = 0.600 +/- 0.000 (27/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (3/30 samples)
* 800 K fcc+B32: x_a = 0.245 +/- 0.008, x_b = 0.491 +/- 0.004 (30/30 samples)
* 900 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (20/30 samples)
* 900 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (20/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (10/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.485 +/- 0.010 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 1.7763568394002505e-15, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00034288699812527203, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
