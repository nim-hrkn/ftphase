# GRACE-1L-OMAT-medium-base-fp64 Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 06:13:44.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'Al3Li': 0.002, 'Al2Li3': 0.002, 'bcc': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002}

## Key numbers

* invariant reactions:
  * 490-500 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al3Li+B32', 'Al3Li+fcc', 'Al4Li9+bcc'] -> ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc']
  * 530-540 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc']
  * 590-600 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc'] -> ['B32+bcc', 'B32+fcc']
  * 1080-1090 K: ['B32+bcc', 'B32+fcc'] -> ['B32+B32', 'B32+bcc', 'B32+fcc']
* two-phase regions at 700 K: fcc(0.194)-B32(0.477); B32(0.562)-bcc(0.750)
* two-phase regions at 800 K: fcc(0.236)-B32(0.467); B32(0.562)-bcc(0.750)
* two-phase regions at 900 K: fcc(0.250)-B32(0.438); B32(0.562)-bcc(0.750)
* two-phase regions at 1000 K: fcc(0.250)-B32(0.438); B32(0.562)-bcc(0.750)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B32+B32 x = 0.440-0.560 at T = 1090-1100 K (2 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (1/30 samples)
* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (4/30 samples)
* 700 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.750 +/- 0.000 (1/30 samples)
* 700 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (5/30 samples)
* 700 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (25/30 samples)
* 700 K fcc+B32: x_a = 0.198 +/- 0.010, x_b = 0.478 +/- 0.002 (30/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (1/30 samples)
* 800 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (1/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (29/30 samples)
* 800 K fcc+B32: x_a = 0.239 +/- 0.011, x_b = 0.468 +/- 0.004 (30/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.442 +/- 0.007 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 2.5639502485114184e-16, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 0.0004929851972838732, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00029705156254852713, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
