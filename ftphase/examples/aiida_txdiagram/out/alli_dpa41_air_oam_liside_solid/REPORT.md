# DPA-4.1-Air-OAM Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-12 07:27:45.  Classical level, 0.0 GPa, model DPA-4.1-Air-OAM (deepmd 1ded5d2, .pt2).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'bcc': 0.002, 'Al3Li': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002, 'Al2Li3': 0.002}

## Key numbers

* invariant reactions:
  * 440-450 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al3Li+B32', 'Al3Li+fcc', 'Al4Li9+bcc'] -> ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc']
  * 730-740 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc']
  * 1020-1030 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc'] -> ['B32+bcc', 'B32+fcc']
* two-phase regions at 700 K: fcc(0.157)-B32(0.507); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-Al4Li9(0.692); Al4Li9(0.692)-bcc(0.792)
* two-phase regions at 800 K: fcc(0.172)-B32(0.508); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 900 K: fcc(0.187)-B32(0.510); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 1000 K: fcc(0.205)-B32(0.514); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (24/30 samples)
* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.772 +/- 0.014 (6/30 samples)
* 700 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.800 +/- 0.016 (24/30 samples)
* 700 K B32+Al2Li3: x_a = 0.556 +/- 0.009, x_b = 0.600 +/- 0.000 (30/30 samples)
* 700 K fcc+B32: x_a = 0.159 +/- 0.008, x_b = 0.507 +/- 0.001 (30/30 samples)
* 800 K Al2Li3+Al4Li9: x_a = 0.600 +/- 0.000, x_b = 0.692 +/- 0.000 (2/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.753 +/- 0.006 (27/30 samples)
* 800 K Al4Li9+bcc: x_a = 0.692 +/- 0.000, x_b = 0.759 +/- 0.013 (3/30 samples)
* 800 K B32+Al2Li3: x_a = 0.562 +/- 0.003, x_b = 0.600 +/- 0.000 (29/30 samples)
* 800 K B32+Al4Li9: x_a = 0.562 +/- 0.000, x_b = 0.692 +/- 0.000 (1/30 samples)
* 800 K fcc+B32: x_a = 0.174 +/- 0.008, x_b = 0.509 +/- 0.002 (30/30 samples)
* 900 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (25/30 samples)
* 900 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (25/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (5/30 samples)
* 900 K fcc+B32: x_a = 0.190 +/- 0.009, x_b = 0.511 +/- 0.002 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 6.280369834735101e-16, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0001047557354230687, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
