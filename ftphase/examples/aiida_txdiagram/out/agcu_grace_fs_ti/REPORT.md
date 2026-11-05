# GRACE-FS-OAM Ag-Cu, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-06 04:54:45.  Classical level, 0.0 GPa, model GRACE-FS-OAM (foundation, FS, 6 A).

## Inputs

* solids (QHA, lowered to the classical level): 19 cells used, missing ['s09_fcc', 's10_fcc', 's11_fcc', 's12_fcc', 's13_fcc', 's14_fcc']
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [750.0, 1400.0, 66] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 900 K; coexistences: fcc(0.016) + liquid(0.055); liquid(0.095) + fcc(0.994)
* pure-A melting bracket (x < 0.02): 1100-1110 K
* invariant reactions:
  * 890-900 K: ['fcc+fcc'] -> ['fcc+liquid']
  * 1010-1020 K: ['fcc+liquid'] -> ['fcc+fcc', 'fcc+liquid']
  * 1100-1110 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']
  * 1140-1150 K: ['fcc+liquid', 'liquid+liquid'] -> ['fcc+liquid']
  * 1150-1160 K: ['fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']
  * 1180-1190 K: ['fcc+liquid', 'liquid+liquid'] -> ['liquid+liquid']
* two-phase regions at 800 K: fcc(0.011)-fcc(0.999)
* two-phase regions at 900 K: fcc(0.016)-liquid(0.055); liquid(0.095)-fcc(0.994)
* two-phase regions at 1000 K: liquid(0.140)-fcc(0.986)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.000-1.000 at T = 750-780 K (4 temperatures)
* fcc+fcc x = 0.010-1.000 at T = 790-850 K (7 temperatures)
* fcc+fcc x = 0.020-1.000 at T = 860-890 K (4 temperatures)
* fcc+fcc x = 0.440-1.000 at T = 1020-1100 K (9 temperatures)
* liquid+liquid x = 0.170-0.610 at T = 1110-1110 K (1 temperatures)
* liquid+liquid x = 0.180-0.600 at T = 1130-1130 K (1 temperatures)
* liquid+liquid x = 0.180-0.610 at T = 1120-1120 K (1 temperatures)
* liquid+liquid x = 0.190-0.580 at T = 1160-1160 K (1 temperatures)
* liquid+liquid x = 0.190-0.590 at T = 1140-1140 K (1 temperatures)
* liquid+liquid x = 0.200-0.560 at T = 1200-1200 K (1 temperatures)
* liquid+liquid x = 0.200-0.570 at T = 1180-1190 K (2 temperatures)
* liquid+liquid x = 0.200-0.580 at T = 1170-1170 K (1 temperatures)
* liquid+liquid x = 0.210-0.550 at T = 1210-1210 K (1 temperatures)
* liquid+liquid x = 0.220-0.530 at T = 1240-1250 K (2 temperatures)
* liquid+liquid x = 0.220-0.540 at T = 1230-1230 K (1 temperatures)
* liquid+liquid x = 0.220-0.550 at T = 1220-1220 K (1 temperatures)
* liquid+liquid x = 0.230-0.520 at T = 1270-1270 K (1 temperatures)
* liquid+liquid x = 0.230-0.530 at T = 1260-1260 K (1 temperatures)
* liquid+liquid x = 0.240-0.510 at T = 1280-1290 K (2 temperatures)
* liquid+liquid x = 0.250-0.500 at T = 1300-1300 K (1 temperatures)
* liquid+liquid x = 0.260-0.480 at T = 1310-1310 K (1 temperatures)
* liquid+liquid x = 0.280-0.470 at T = 1320-1320 K (1 temperatures)
* liquid+liquid x = 0.290-0.450 at T = 1340-1350 K (2 temperatures)
* liquid+liquid x = 0.290-0.460 at T = 1330-1330 K (1 temperatures)
* liquid+liquid x = 0.300-0.430 at T = 1370-1370 K (1 temperatures)
* liquid+liquid x = 0.300-0.440 at T = 1360-1360 K (1 temperatures)
* liquid+liquid x = 0.310-0.430 at T = 1380-1380 K (1 temperatures)
* liquid+liquid x = 0.320-0.410 at T = 1390-1390 K (1 temperatures)
* liquid+liquid x = 0.330-0.410 at T = 1400-1400 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 750 K fcc+fcc: x_a = 0.004 +/- 0.000, x_b = 0.999 +/- 0.000 (30/30 samples)
* 790 K fcc+fcc: x_a = 0.006 +/- 0.000, x_b = 0.999 +/- 0.000 (30/30 samples)
* 890 K fcc+fcc: x_a = 0.021 +/- 0.000, x_b = 0.998 +/- 0.000 (17/30 samples)
* 890 K fcc+liquid: x_a = 0.019 +/- 0.003, x_b = 0.060 +/- 0.019 (11/30 samples)
* 890 K liquid+fcc: x_a = 0.088 +/- 0.002, x_b = 0.998 +/- 0.000 (13/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 800 K -1.2, 975 K -7.5
* s01_fcc: 700 K +0.7, 807 K -0.6, 913 K -3.6
* s02_fcc: 700 K +0.9, 807 K -0.4, 913 K -3.3
* s03_fcc: 700 K +0.2, 797 K -1.0, 895 K -3.5
* s04_fcc: 700 K -3.3, 797 K -5.1, 895 K -7.6
* s05_fcc: 688 K -5.5, 774 K -8.1, 860 K -11.0
* s06_fcc: 688 K -5.1, 774 K -7.7, 860 K -10.6
* s07_fcc: 632 K -5.3, 711 K -7.5, 790 K -9.9
* s08_fcc: 632 K -2.5, 711 K -3.8, 790 K -5.2
* s15_fcc: 700 K -5.1, 856 K -8.2, 1012 K -11.7
* s16_fcc: 700 K -4.0, 856 K -7.2, 1012 K -10.5
* s17_fcc: 700 K -2.9, 900 K -5.0, 1101 K -7.3
* s18_fcc: 700 K -3.2, 900 K -5.0, 1101 K -7.2
* s19_fcc: 700 K -3.8, 922 K -6.5, 1145 K -9.8
* s20_fcc: 700 K -4.1, 922 K -6.7, 1145 K -10.0
* s21_fcc: 700 K -3.5, 934 K -6.3, 1168 K -9.9
* s22_fcc: 700 K -3.5, 934 K -6.4, 1168 K -10.1
* s23_fcc: 900 K -6.8, 1160 K -11.1
* s24_fcc: 900 K -6.8, 1160 K -11.1

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 0.00041512369975783364, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
