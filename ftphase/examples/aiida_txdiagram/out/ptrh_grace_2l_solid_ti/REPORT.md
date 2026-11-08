# GRACE-2L-OMAT-medium-base-fp64 Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-08 21:43:40.  Classical level, 0.0 GPa, model GRACE-2L-OMAT-medium-base-fp64 (foundation, 2 layers, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_20', 'lqd_x0_40', 'lqd_x0_50', 'lqd_x0_60', 'lqd_x0_80', 'lqd_x1_00']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [100.0, 2400.0, 231] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'PtRh3': 0.002, 'Pt3Rh': 0.002, 'PtRh': 0.002}

## Key numbers

* invariant reactions:
  * 160-170 K: ['Pt3Rh+PtRh', 'Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh3+PtRh3', 'PtRh3+fcc'] -> ['Pt3Rh+PtRh', 'Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh3+fcc']
  * 170-180 K: ['Pt3Rh+PtRh', 'Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc']
  * 180-190 K: ['Pt3Rh+fcc', 'PtRh+PtRh', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc']
  * 200-210 K: ['Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc'] -> ['Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc']
  * 220-230 K: ['Pt3Rh+fcc', 'PtRh+PtRh3', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc']
  * 230-240 K: ['Pt3Rh+fcc', 'PtRh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['Pt3Rh+fcc', 'PtRh3+fcc', 'fcc+fcc']
  * 700-710 K: ['Pt3Rh+fcc', 'PtRh3+fcc', 'fcc+fcc'] -> ['PtRh3+fcc', 'fcc+fcc']
  * 1330-1340 K: ['PtRh3+fcc', 'fcc+fcc'] -> ['fcc+fcc']
* two-phase regions at 700 K: fcc(0.182)-Pt3Rh(0.188); Pt3Rh(0.188)-fcc(0.193); fcc(0.473)-fcc(0.480); fcc(0.650)-PtRh3(0.812); PtRh3(0.812)-fcc(0.912)
* two-phase regions at 800 K: fcc(0.022)-fcc(0.210); fcc(0.473)-fcc(0.480); fcc(0.662)-PtRh3(0.812); PtRh3(0.812)-fcc(0.905)
* two-phase regions at 900 K: fcc(0.010)-fcc(0.263); fcc(0.473)-fcc(0.480); fcc(0.672)-PtRh3(0.812); PtRh3(0.812)-fcc(0.897)
* two-phase regions at 1000 K: fcc(0.006)-fcc(0.301); fcc(0.473)-fcc(0.480); fcc(0.688)-PtRh3(0.812); PtRh3(0.812)-fcc(0.890)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* PtRh+PtRh x = 0.440-0.560 at T = 100-180 K (9 temperatures)
* PtRh3+PtRh3 x = 0.660-0.810 at T = 100-160 K (7 temperatures)
* fcc+fcc x = 0.000-0.310 at T = 1040-1040 K (1 temperatures)
* fcc+fcc x = 0.000-0.320 at T = 1050-1080 K (4 temperatures)
* fcc+fcc x = 0.000-0.330 at T = 1090-1120 K (4 temperatures)
* fcc+fcc x = 0.000-0.340 at T = 1130-1170 K (5 temperatures)
* fcc+fcc x = 0.000-0.350 at T = 1180-1220 K (5 temperatures)
* fcc+fcc x = 0.000-0.360 at T = 1230-1270 K (5 temperatures)
* fcc+fcc x = 0.000-0.370 at T = 1280-1330 K (6 temperatures)
* fcc+fcc x = 0.000-0.380 at T = 1340-1400 K (7 temperatures)
* fcc+fcc x = 0.000-0.390 at T = 1410-1470 K (7 temperatures)
* fcc+fcc x = 0.000-0.400 at T = 1480-1910 K (29 temperatures)
* fcc+fcc x = 0.000-0.410 at T = 1590-2080 K (23 temperatures)
* fcc+fcc x = 0.000-0.420 at T = 1660-2340 K (24 temperatures)
* fcc+fcc x = 0.000-0.430 at T = 1800-1850 K (2 temperatures)
* fcc+fcc x = 0.000-0.440 at T = 1900-2360 K (5 temperatures)
* fcc+fcc x = 0.000-0.450 at T = 2100-2200 K (3 temperatures)
* fcc+fcc x = 0.000-0.460 at T = 2250-2400 K (7 temperatures)
* fcc+fcc x = 0.010-0.240 at T = 850-860 K (2 temperatures)
* fcc+fcc x = 0.010-0.250 at T = 870-880 K (2 temperatures)
* fcc+fcc x = 0.010-0.260 at T = 890-900 K (2 temperatures)
* fcc+fcc x = 0.010-0.270 at T = 910-920 K (2 temperatures)
* fcc+fcc x = 0.010-0.280 at T = 930-950 K (3 temperatures)
* fcc+fcc x = 0.010-0.290 at T = 960-980 K (3 temperatures)
* fcc+fcc x = 0.010-0.300 at T = 990-1010 K (3 temperatures)
* fcc+fcc x = 0.010-0.310 at T = 1020-1030 K (2 temperatures)
* fcc+fcc x = 0.020-0.200 at T = 790-790 K (1 temperatures)
* fcc+fcc x = 0.020-0.210 at T = 800-800 K (1 temperatures)
* fcc+fcc x = 0.020-0.220 at T = 810-820 K (2 temperatures)
* fcc+fcc x = 0.020-0.230 at T = 830-840 K (2 temperatures)
* fcc+fcc x = 0.030-0.170 at T = 750-750 K (1 temperatures)
* fcc+fcc x = 0.030-0.180 at T = 760-760 K (1 temperatures)
* fcc+fcc x = 0.030-0.190 at T = 770-770 K (1 temperatures)
* fcc+fcc x = 0.030-0.200 at T = 780-780 K (1 temperatures)
* fcc+fcc x = 0.040-0.150 at T = 730-730 K (1 temperatures)
* fcc+fcc x = 0.040-0.160 at T = 740-740 K (1 temperatures)
* fcc+fcc x = 0.050-0.140 at T = 720-720 K (1 temperatures)
* fcc+fcc x = 0.060-0.120 at T = 710-710 K (1 temperatures)
* fcc+fcc x = 0.470-0.480 at T = 210-2400 K (220 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K Pt3Rh+fcc: x_a = 0.188 +/- 0.000, x_b = 0.296 +/- 0.035 (18/30 samples)
* 700 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.907 +/- 0.026 (29/30 samples)
* 700 K fcc+Pt3Rh: x_a = 0.035 +/- 0.031, x_b = 0.188 +/- 0.000 (18/30 samples)
* 700 K fcc+PtRh3: x_a = 0.657 +/- 0.050, x_b = 0.812 +/- 0.000 (29/30 samples)
* 700 K fcc+fcc: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (30/30 samples)
* 800 K Pt3Rh+fcc: x_a = 0.188 +/- 0.000, x_b = 0.282 +/- 0.035 (17/30 samples)
* 800 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.905 +/- 0.017 (27/30 samples)
* 800 K fcc+Pt3Rh: x_a = 0.016 +/- 0.003, x_b = 0.188 +/- 0.000 (17/30 samples)
* 800 K fcc+PtRh3: x_a = 0.658 +/- 0.037, x_b = 0.812 +/- 0.000 (27/30 samples)
* 800 K fcc+fcc: x_a = 0.277 +/- 0.223, x_b = 0.363 +/- 0.134 (30/30 samples)
* 800 K fcc+fcc#1: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (13/30 samples)
* 900 K Pt3Rh+fcc: x_a = 0.188 +/- 0.000, x_b = 0.299 +/- 0.022 (9/30 samples)
* 900 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.903 +/- 0.011 (25/30 samples)
* 900 K fcc+Pt3Rh: x_a = 0.009 +/- 0.002, x_b = 0.188 +/- 0.000 (9/30 samples)
* 900 K fcc+PtRh3: x_a = 0.661 +/- 0.026, x_b = 0.812 +/- 0.000 (25/30 samples)
* 900 K fcc+fcc: x_a = 0.149 +/- 0.212, x_b = 0.328 +/- 0.099 (30/30 samples)
* 900 K fcc+fcc#1: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (21/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s23_fcc: 1700 K -22.2, 2025 K -37.1, 2350 K -52.5

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.011638097577799496, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.010222153701841413, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.007138168094162342, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.00889252270507616, 'flag': True}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
