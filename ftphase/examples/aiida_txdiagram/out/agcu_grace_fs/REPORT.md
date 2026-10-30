# GRACE-FS-OAM Ag-Cu, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-30 10:52:00.  Classical level, 0.0 GPa, model GRACE-FS-OAM (foundation, FS, 6 A).

## Inputs

* solids (QHA, lowered to the classical level): 25 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [1100.0, 1400.0, 31] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: liquid(0.164) + fcc(0.975)
* invariant reactions:
  * 1110-1120 K: ['fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']
  * 1310-1320 K: ['fcc+liquid', 'liquid+liquid'] -> ['liquid+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* liquid+liquid x = 0.180-0.600 at T = 1130-1130 K (1 temperatures)
* liquid+liquid x = 0.180-0.610 at T = 1120-1120 K (1 temperatures)
* liquid+liquid x = 0.190-0.580 at T = 1160-1160 K (1 temperatures)
* liquid+liquid x = 0.190-0.590 at T = 1140-1150 K (2 temperatures)
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

* 1100 K liquid+fcc: x_a = 0.276 +/- 0.206, x_b = 0.976 +/- 0.001 (30/30 samples)
* 1100 K liquid+liquid: x_a = 0.170 +/- 0.000, x_b = 0.619 +/- 0.000 (7/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0012669971828698928, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 0.00041512369975783364, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
