# MACE-MPA-0 medium Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-08 14:58:04.  Classical level, 0.0 GPa, model MACE-MPA-0 medium (float32, ML-IAP, cuEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_20', 'lqd_x0_40', 'lqd_x0_50', 'lqd_x0_60', 'lqd_x0_80', 'lqd_x1_00']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [100.0, 2400.0, 231] (K, min, max, points); sigma (eV/atom): {'PtRh': 0.002, 'fcc': 0.002, 'PtRh3': 0.002, 'Pt3Rh': 0.002}

## Key numbers

* invariant reactions:
  * 210-220 K: ['Pt3Rh+PtRh', 'Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc']
  * 230-240 K: ['Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc']
  * 240-250 K: ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc']
  * 250-260 K: ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['Pt3Rh+fcc', 'PtRh3+fcc', 'fcc+fcc']
  * 500-510 K: ['Pt3Rh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['PtRh3+fcc', 'fcc+fcc']
  * 900-910 K: ['PtRh3+fcc', 'fcc+fcc'] -> ['fcc+fcc']
* two-phase regions at 700 K: fcc(0.007)-fcc(0.266); fcc(0.473)-fcc(0.480); fcc(0.728)-PtRh3(0.812); PtRh3(0.812)-fcc(0.870)
* two-phase regions at 800 K: fcc(0.004)-fcc(0.303); fcc(0.473)-fcc(0.480); fcc(0.750)-PtRh3(0.812); PtRh3(0.812)-fcc(0.858)
* two-phase regions at 900 K: fcc(0.002)-fcc(0.329); fcc(0.473)-fcc(0.480); fcc(0.795)-PtRh3(0.812); PtRh3(0.812)-fcc(0.828)
* two-phase regions at 1000 K: fcc(0.001)-fcc(0.350); fcc(0.473)-fcc(0.480)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* PtRh+PtRh x = 0.440-0.560 at T = 100-230 K (14 temperatures)
* fcc+fcc x = 0.000-0.290 at T = 760-770 K (2 temperatures)
* fcc+fcc x = 0.000-0.300 at T = 780-800 K (3 temperatures)
* fcc+fcc x = 0.000-0.310 at T = 810-840 K (4 temperatures)
* fcc+fcc x = 0.000-0.320 at T = 850-880 K (4 temperatures)
* fcc+fcc x = 0.000-0.330 at T = 890-920 K (4 temperatures)
* fcc+fcc x = 0.000-0.340 at T = 930-970 K (5 temperatures)
* fcc+fcc x = 0.000-0.350 at T = 980-1030 K (6 temperatures)
* fcc+fcc x = 0.000-0.360 at T = 1040-1090 K (6 temperatures)
* fcc+fcc x = 0.000-0.370 at T = 1100-1150 K (6 temperatures)
* fcc+fcc x = 0.000-0.380 at T = 1160-1240 K (9 temperatures)
* fcc+fcc x = 0.000-0.390 at T = 1250-1300 K (6 temperatures)
* fcc+fcc x = 0.000-0.400 at T = 1310-1420 K (12 temperatures)
* fcc+fcc x = 0.000-0.410 at T = 1430-1500 K (8 temperatures)
* fcc+fcc x = 0.000-0.420 at T = 1510-1630 K (13 temperatures)
* fcc+fcc x = 0.000-0.430 at T = 1640-1720 K (9 temperatures)
* fcc+fcc x = 0.000-0.440 at T = 1730-1870 K (15 temperatures)
* fcc+fcc x = 0.000-0.450 at T = 1880-1970 K (10 temperatures)
* fcc+fcc x = 0.000-0.460 at T = 1980-2140 K (17 temperatures)
* fcc+fcc x = 0.000-0.470 at T = 2150-2300 K (16 temperatures)
* fcc+fcc x = 0.000-0.480 at T = 2310-2400 K (10 temperatures)
* fcc+fcc x = 0.010-0.220 at T = 610-610 K (1 temperatures)
* fcc+fcc x = 0.010-0.230 at T = 620-630 K (2 temperatures)
* fcc+fcc x = 0.010-0.240 at T = 640-650 K (2 temperatures)
* fcc+fcc x = 0.010-0.250 at T = 660-670 K (2 temperatures)
* fcc+fcc x = 0.010-0.260 at T = 680-690 K (2 temperatures)
* fcc+fcc x = 0.010-0.270 at T = 700-710 K (2 temperatures)
* fcc+fcc x = 0.010-0.280 at T = 720-740 K (3 temperatures)
* fcc+fcc x = 0.010-0.290 at T = 750-750 K (1 temperatures)
* fcc+fcc x = 0.020-0.190 at T = 570-570 K (1 temperatures)
* fcc+fcc x = 0.020-0.200 at T = 580-590 K (2 temperatures)
* fcc+fcc x = 0.020-0.210 at T = 600-600 K (1 temperatures)
* fcc+fcc x = 0.030-0.160 at T = 540-540 K (1 temperatures)
* fcc+fcc x = 0.030-0.170 at T = 550-550 K (1 temperatures)
* fcc+fcc x = 0.030-0.180 at T = 560-560 K (1 temperatures)
* fcc+fcc x = 0.040-0.140 at T = 530-530 K (1 temperatures)
* fcc+fcc x = 0.050-0.130 at T = 520-520 K (1 temperatures)
* fcc+fcc x = 0.070-0.100 at T = 510-510 K (1 temperatures)
* fcc+fcc x = 0.470-0.480 at T = 250-2300 K (206 temperatures)
* fcc+fcc x = 0.750-0.960 at T = 2390-2400 K (2 temperatures)
* fcc+fcc x = 0.760-0.950 at T = 2320-2380 K (7 temperatures)
* fcc+fcc x = 0.770-0.930 at T = 2260-2270 K (2 temperatures)
* fcc+fcc x = 0.770-0.940 at T = 2280-2310 K (4 temperatures)
* fcc+fcc x = 0.780-0.920 at T = 2220-2230 K (2 temperatures)
* fcc+fcc x = 0.780-0.930 at T = 2240-2250 K (2 temperatures)
* fcc+fcc x = 0.790-0.910 at T = 2180-2200 K (3 temperatures)
* fcc+fcc x = 0.790-0.920 at T = 2210-2210 K (1 temperatures)
* fcc+fcc x = 0.800-0.900 at T = 2160-2170 K (2 temperatures)
* fcc+fcc x = 0.810-0.890 at T = 2140-2150 K (2 temperatures)
* fcc+fcc x = 0.820-0.880 at T = 2130-2130 K (1 temperatures)
* fcc+fcc x = 0.830-0.870 at T = 2120-2120 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Pt3Rh+fcc: x_a = 0.188 +/- 0.000, x_b = 0.307 +/- 0.022 (6/30 samples)
* 700 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.886 +/- 0.026 (25/30 samples)
* 700 K fcc+Pt3Rh: x_a = 0.006 +/- 0.001, x_b = 0.188 +/- 0.000 (6/30 samples)
* 700 K fcc+PtRh3: x_a = 0.682 +/- 0.060, x_b = 0.812 +/- 0.000 (25/30 samples)
* 700 K fcc+fcc: x_a = 0.100 +/- 0.186, x_b = 0.309 +/- 0.086 (30/30 samples)
* 700 K fcc+fcc#1: x_a = 0.472 +/- 0.000, x_b = 0.480 +/- 0.000 (24/30 samples)
* 800 K Pt3Rh+fcc: x_a = 0.188 +/- 0.000, x_b = 0.317 +/- 0.005 (3/30 samples)
* 800 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.884 +/- 0.023 (22/30 samples)
* 800 K fcc+Pt3Rh: x_a = 0.003 +/- 0.000, x_b = 0.188 +/- 0.000 (3/30 samples)
* 800 K fcc+PtRh3: x_a = 0.684 +/- 0.056, x_b = 0.812 +/- 0.000 (22/30 samples)
* 800 K fcc+fcc: x_a = 0.051 +/- 0.141, x_b = 0.320 +/- 0.053 (30/30 samples)
* 800 K fcc+fcc#1: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (27/30 samples)
* 900 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.878 +/- 0.024 (20/30 samples)
* 900 K fcc+PtRh3: x_a = 0.695 +/- 0.058, x_b = 0.812 +/- 0.000 (20/30 samples)
* 900 K fcc+fcc: x_a = 0.002 +/- 0.000, x_b = 0.329 +/- 0.000 (30/30 samples)
* 900 K fcc+fcc#1: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.023187645689810625, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.01024977796567844, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.01179033115863557, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.010552517495918153, 'flag': True}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
