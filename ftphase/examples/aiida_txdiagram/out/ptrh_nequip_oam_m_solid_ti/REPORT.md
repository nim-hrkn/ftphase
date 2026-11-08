# NequIP-OAM-M 0.1 Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-09 00:29:29.  Classical level, 0.0 GPa, model NequIP-OAM-M 0.1 (ML-IAP, OpenEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_20', 'lqd_x0_40', 'lqd_x0_50', 'lqd_x0_60', 'lqd_x0_80', 'lqd_x1_00']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [100.0, 2400.0, 231] (K, min, max, points); sigma (eV/atom): {'PtRh': 0.002, 'fcc': 0.002, 'PtRh3': 0.002, 'Pt3Rh': 0.002}

## Key numbers

* invariant reactions:
  * 190-200 K: ['Pt3Rh+PtRh', 'Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc']
  * 200-210 K: ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc']
  * 210-220 K: ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['Pt3Rh+fcc', 'PtRh3+fcc', 'fcc+fcc']
  * 570-580 K: ['Pt3Rh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['PtRh3+fcc', 'fcc+fcc']
  * 1190-1200 K: ['PtRh3+fcc', 'fcc+fcc'] -> ['fcc+fcc']
  * 1740-1750 K: ['fcc+fcc'] -> ['Pt3Rh+fcc', 'fcc+fcc']
  * 2350-2360 K: ['Pt3Rh+fcc', 'fcc+fcc'] -> ['Pt3Rh+fcc']
  * 2370-2380 K: ['Pt3Rh+fcc'] -> ['Pt3Rh+fcc', 'fcc+fcc']
* two-phase regions at 700 K: fcc(0.000)-fcc(0.330); fcc(0.473)-fcc(0.480); fcc(0.605)-PtRh3(0.812); PtRh3(0.812)-fcc(0.902)
* two-phase regions at 800 K: fcc(0.000)-fcc(0.348); fcc(0.473)-fcc(0.480); fcc(0.625)-PtRh3(0.812); PtRh3(0.812)-fcc(0.900)
* two-phase regions at 900 K: fcc(0.000)-fcc(0.360); fcc(0.473)-fcc(0.480); fcc(0.647)-PtRh3(0.812); PtRh3(0.812)-fcc(0.893)
* two-phase regions at 1000 K: fcc(0.000)-fcc(0.375); fcc(0.473)-fcc(0.480); fcc(0.677)-PtRh3(0.812); PtRh3(0.812)-fcc(0.885)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.000-0.300 at T = 580-580 K (1 temperatures)
* fcc+fcc x = 0.000-0.310 at T = 590-630 K (5 temperatures)
* fcc+fcc x = 0.000-0.320 at T = 640-670 K (4 temperatures)
* fcc+fcc x = 0.000-0.330 at T = 680-720 K (5 temperatures)
* fcc+fcc x = 0.000-0.340 at T = 730-790 K (7 temperatures)
* fcc+fcc x = 0.000-0.350 at T = 800-840 K (5 temperatures)
* fcc+fcc x = 0.000-0.360 at T = 850-930 K (9 temperatures)
* fcc+fcc x = 0.000-0.370 at T = 940-1740 K (10 temperatures)
* fcc+fcc x = 0.000-0.380 at T = 1000-1100 K (11 temperatures)
* fcc+fcc x = 0.000-0.390 at T = 1110-1180 K (8 temperatures)
* fcc+fcc x = 0.000-0.400 at T = 1190-1700 K (15 temperatures)
* fcc+fcc x = 0.000-0.410 at T = 1330-1410 K (9 temperatures)
* fcc+fcc x = 0.000-0.420 at T = 1420-1690 K (16 temperatures)
* fcc+fcc x = 0.000-0.430 at T = 1570-1680 K (12 temperatures)
* fcc+fcc x = 0.470-0.480 at T = 210-2340 K (207 temperatures)
* fcc+fcc x = 0.560-0.670 at T = 2310-2340 K (4 temperatures)
* fcc+fcc x = 0.570-0.670 at T = 2210-2290 K (8 temperatures)
* fcc+fcc x = 0.580-0.670 at T = 2130-2190 K (6 temperatures)
* fcc+fcc x = 0.590-0.670 at T = 2040-2120 K (7 temperatures)
* fcc+fcc x = 0.600-0.660 at T = 1980-2030 K (5 temperatures)
* fcc+fcc x = 0.610-0.660 at T = 1930-1970 K (4 temperatures)
* fcc+fcc x = 0.620-0.650 at T = 1910-1920 K (2 temperatures)
* fcc+fcc x = 0.630-0.640 at T = 1880-1880 K (1 temperatures)
* fcc+fcc x = 0.630-0.650 at T = 1890-1890 K (1 temperatures)
* fcc+fcc x = 0.770-0.970 at T = 2100-2300 K (5 temperatures)
* fcc+fcc x = 0.770-0.980 at T = 2350-2400 K (4 temperatures)
* fcc+fcc x = 0.780-0.960 at T = 1950-2050 K (3 temperatures)
* fcc+fcc x = 0.790-0.940 at T = 1850-1850 K (1 temperatures)
* fcc+fcc x = 0.790-0.950 at T = 1900-1900 K (1 temperatures)
* fcc+fcc x = 0.800-0.930 at T = 1800-1800 K (1 temperatures)
* fcc+fcc x = 0.820-0.910 at T = 1750-1750 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Pt3Rh+fcc: x_a = 0.188 +/- 0.000, x_b = 0.345 +/- 0.004 (3/30 samples)
* 700 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.912 +/- 0.015 (28/30 samples)
* 700 K fcc+Pt3Rh: x_a = 0.000 +/- 0.000, x_b = 0.188 +/- 0.000 (3/30 samples)
* 700 K fcc+PtRh3: x_a = 0.589 +/- 0.032, x_b = 0.812 +/- 0.000 (28/30 samples)
* 700 K fcc+fcc: x_a = 0.047 +/- 0.142, x_b = 0.345 +/- 0.045 (30/30 samples)
* 700 K fcc+fcc#1: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (27/30 samples)
* 800 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.907 +/- 0.017 (28/30 samples)
* 800 K fcc+PtRh3: x_a = 0.609 +/- 0.035, x_b = 0.812 +/- 0.000 (28/30 samples)
* 800 K fcc+fcc: x_a = 0.000 +/- 0.000, x_b = 0.348 +/- 0.000 (30/30 samples)
* 800 K fcc+fcc#1: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (30/30 samples)
* 900 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.902 +/- 0.020 (28/30 samples)
* 900 K fcc+PtRh3: x_a = 0.632 +/- 0.041, x_b = 0.812 +/- 0.000 (28/30 samples)
* 900 K fcc+fcc: x_a = 0.000 +/- 0.000, x_b = 0.360 +/- 0.000 (30/30 samples)
* 900 K fcc+fcc#1: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s23_fcc: 1700 K -53.2, 2025 K -78.4, 2350 K -103.3

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.01989378912907424, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.013473832611426411, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.00997583126600707, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.007959927268113636, 'flag': True}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
