# SevenNet-0 Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 13:59:36.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'Al3Li': 0.002, 'Al2Li3': 0.002, 'bcc': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002}

## Key numbers

* invariant reactions:
  * 430-440 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al3Li+B32', 'Al3Li+fcc', 'Al4Li9+bcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'Al3Li+B32', 'Al3Li+fcc']
  * 440-450 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'Al3Li+B32', 'Al3Li+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc']
  * 760-770 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc', 'bcc+bcc']
  * 930-940 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc', 'bcc+bcc'] -> ['B32+bcc', 'B32+fcc', 'bcc+bcc']
  * 1000-1010 K: ['B32+bcc', 'B32+fcc', 'bcc+bcc'] -> ['B32+bcc', 'B32+fcc', 'bcc+bcc', 'fcc+fcc']
* two-phase regions at 700 K: fcc(0.250)-B32(0.479); B32(0.541)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.992)
* two-phase regions at 800 K: fcc(0.250)-B32(0.479); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.835); bcc(0.750)-bcc(0.986)
* two-phase regions at 900 K: fcc(0.250)-B32(0.481); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.857); bcc(0.750)-bcc(0.978)
* two-phase regions at 1000 K: fcc(0.250)-B32(0.486); B32(0.562)-bcc(0.750); bcc(0.750)-bcc(0.965)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* bcc+bcc x = 0.750-0.910 at T = 1080-1100 K (3 temperatures)
* bcc+bcc x = 0.750-0.920 at T = 1050-1070 K (3 temperatures)
* bcc+bcc x = 0.750-0.930 at T = 1030-1040 K (2 temperatures)
* bcc+bcc x = 0.750-0.960 at T = 1000-1020 K (3 temperatures)
* bcc+bcc x = 0.750-0.970 at T = 940-990 K (6 temperatures)
* bcc+bcc x = 0.750-0.980 at T = 810-930 K (13 temperatures)
* bcc+bcc x = 0.750-0.990 at T = 770-800 K (4 temperatures)
* fcc+fcc x = 0.240-0.250 at T = 1010-1100 K (10 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.947 +/- 0.070 (30/30 samples)
* 700 K B32+Al2Li3: x_a = 0.540 +/- 0.015, x_b = 0.600 +/- 0.000 (30/30 samples)
* 700 K bcc+bcc: x_a = 0.750 +/- 0.000, x_b = 0.991 +/- 0.000 (9/30 samples)
* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.479 +/- 0.002 (30/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.891 +/- 0.066 (29/30 samples)
* 800 K B32+Al2Li3: x_a = 0.553 +/- 0.013, x_b = 0.600 +/- 0.000 (29/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (1/30 samples)
* 800 K bcc+bcc: x_a = 0.750 +/- 0.000, x_b = 0.986 +/- 0.000 (21/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.480 +/- 0.003 (30/30 samples)
* 900 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.874 +/- 0.051 (21/30 samples)
* 900 K B32+Al2Li3: x_a = 0.560 +/- 0.009, x_b = 0.600 +/- 0.000 (21/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (9/30 samples)
* 900 K bcc+bcc: x_a = 0.750 +/- 0.000, x_b = 0.978 +/- 0.000 (27/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.482 +/- 0.004 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 0.001110415776586857, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00073466833313344, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
