# EAM Ag-Cu (Williams-Mishin-Hamilton 2006), 0 GPa: fcc (calphy TI >= 900 K, QHA below) + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-23 17:56:06.  Classical level, 0.0 GPa, model CuAg.eam.alloy (Williams-Mishin-Hamilton 2006 EAM).

## Inputs

* solids (QHA, lowered to the classical level): 25 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [1100.0, 1400.0, 31] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: fcc(0.306) + liquid(0.472); liquid(0.665) + fcc(0.957)
* pure-A melting bracket (x < 0.02): 1320-1330 K
* invariant reactions:
  * 1170-1180 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.020-0.210 at T = 1100-1150 K (6 temperatures)
* fcc+fcc x = 0.030-0.210 at T = 1160-1170 K (2 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1100 K fcc+fcc: x_a = 0.022 +/- 0.000, x_b = 0.212 +/- 0.000 (29/30 samples)
* 1100 K fcc+liquid: x_a = 0.290 +/- 0.058, x_b = 0.452 +/- 0.068 (30/30 samples)
* 1100 K liquid+fcc: x_a = 0.669 +/- 0.025, x_b = 0.957 +/- 0.004 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 900 K -12.6, 1130 K -14.9, 1360 K -16.8
* s01_fcc: 900 K -11.9, 1132 K -15.3, 1364 K -18.9
* s02_fcc: 900 K -13.3, 1132 K -16.9, 1364 K -20.3
* s03_fcc: 900 K -14.4, 1134 K -19.4, 1368 K -24.4
* s04_fcc: 900 K -13.3, 1134 K -18.1, 1368 K -22.6
* s05_fcc: 900 K -15.5, 1138 K -22.4, 1375 K -29.0
* s06_fcc: 900 K -15.3, 1138 K -22.2, 1375 K -28.5
* s07_fcc: 900 K -15.6, 1145 K -24.2, 1390 K -31.9
* s08_fcc: 900 K -15.7, 1145 K -24.1, 1390 K -32.1
* s17_fcc: 900 K -0.4, 1183 K -2.8
* s19_fcc: 900 K +4.5, 1186 K +5.4
* s20_fcc: 900 K +7.5, 1186 K +9.4
* s21_fcc: 900 K +4.5, 1188 K +6.0
* s22_fcc: 900 K +5.5, 1188 K +7.6
* s23_fcc: 900 K +4.5, 1190 K +6.5
* s24_fcc: 900 K +2.7, 1190 K +3.7

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0035174693355349445, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 0.0002988720000118667, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
