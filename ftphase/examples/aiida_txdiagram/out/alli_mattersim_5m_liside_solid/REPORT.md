# MatterSim-v1.0.0-5M Al-Li, 0 <= x_Li <= 1, Li side solids only, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 07:33:08.  Classical level, 0.0 GPa, model MatterSim-v1.0.0-5M (float32, ML-IAP).

## Inputs

* solids (QHA, lowered to the classical level): 24 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite', 'bcc': 'ideal'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline', 'bcc': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'bcc': 0.002, 'Al3Li': 0.002, 'fcc': 0.002, 'Al4Li9': 0.002, 'Al2Li3': 0.002}

## Key numbers

* invariant reactions:
  * 490-500 K: ['Al2Li3+Al4Li9', 'Al2Li3+B32', 'Al4Li9+bcc', 'B32+fcc', 'fcc+fcc'] -> ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc', 'fcc+fcc']
  * 750-760 K: ['Al2Li3+B32', 'Al2Li3+bcc', 'B32+fcc', 'fcc+fcc'] -> ['B32+bcc', 'B32+fcc', 'fcc+fcc']
  * 1090-1100 K: ['B32+bcc', 'B32+fcc', 'fcc+fcc'] -> ['bcc+fcc', 'fcc+fcc']
* two-phase regions at 700 K: fcc(0.040)-fcc(0.153); fcc(0.250)-B32(0.562); B32(0.562)-Al2Li3(0.600); Al2Li3(0.600)-bcc(0.750)
* two-phase regions at 800 K: fcc(0.037)-fcc(0.173); fcc(0.250)-B32(0.562); B32(0.562)-bcc(0.750)
* two-phase regions at 900 K: fcc(0.035)-fcc(0.193); fcc(0.250)-B32(0.562); B32(0.562)-bcc(0.750)
* two-phase regions at 1000 K: fcc(0.032)-fcc(0.212); fcc(0.250)-B32(0.562); B32(0.562)-bcc(0.750)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.030-0.100 at T = 300-310 K (2 temperatures)
* fcc+fcc x = 0.030-0.190 at T = 890-910 K (3 temperatures)
* fcc+fcc x = 0.030-0.200 at T = 920-960 K (5 temperatures)
* fcc+fcc x = 0.030-0.210 at T = 970-1010 K (5 temperatures)
* fcc+fcc x = 0.030-0.220 at T = 1020-1070 K (6 temperatures)
* fcc+fcc x = 0.030-0.230 at T = 1080-1100 K (3 temperatures)
* fcc+fcc x = 0.040-0.100 at T = 320-420 K (11 temperatures)
* fcc+fcc x = 0.040-0.110 at T = 430-490 K (7 temperatures)
* fcc+fcc x = 0.040-0.120 at T = 500-540 K (5 temperatures)
* fcc+fcc x = 0.040-0.130 at T = 550-600 K (6 temperatures)
* fcc+fcc x = 0.040-0.140 at T = 610-650 K (5 temperatures)
* fcc+fcc x = 0.040-0.150 at T = 660-700 K (5 temperatures)
* fcc+fcc x = 0.040-0.160 at T = 710-750 K (5 temperatures)
* fcc+fcc x = 0.040-0.170 at T = 760-800 K (5 temperatures)
* fcc+fcc x = 0.040-0.180 at T = 810-860 K (6 temperatures)
* fcc+fcc x = 0.040-0.190 at T = 870-880 K (2 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (20/30 samples)
* 700 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (20/30 samples)
* 700 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (10/30 samples)
* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 700 K fcc+fcc: x_a = 0.040 +/- 0.000, x_b = 0.153 +/- 0.000 (30/30 samples)
* 800 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (11/30 samples)
* 800 K B32+Al2Li3: x_a = 0.562 +/- 0.000, x_b = 0.600 +/- 0.000 (11/30 samples)
* 800 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (19/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 800 K fcc+fcc: x_a = 0.037 +/- 0.000, x_b = 0.173 +/- 0.000 (30/30 samples)
* 900 K Al2Li3+bcc: x_a = 0.600 +/- 0.000, x_b = 0.750 +/- 0.000 (2/30 samples)
* 900 K B32+Al2Li3: x_a = 0.489 +/- 0.002, x_b = 0.600 +/- 0.000 (2/30 samples)
* 900 K B32+bcc: x_a = 0.562 +/- 0.000, x_b = 0.750 +/- 0.000 (28/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 900 K fcc+fcc: x_a = 0.035 +/- 0.000, x_b = 0.193 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 2.5639502485114184e-16, 'flag': False}, {'T': 900.0, 'phase': 'bcc', 'rmse_eV': 0.000555742568027958, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00039092638733507985, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
