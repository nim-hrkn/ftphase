# EAM Ag-Cu (Williams-Mishin-Hamilton 2006), 0 GPa: fcc (calphy TI >= 900 K, QHA below) + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-24 01:02:52.  Classical level, 0.0 GPa, model CuAg.eam.alloy (Williams-Mishin-Hamilton 2006 EAM).

## Inputs

* solids (QHA, lowered to the classical level): 25 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [1100.0, 1400.0, 31] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: fcc(0.310) + liquid(0.410); liquid(0.711) + fcc(0.966)
* pure-A melting bracket (x < 0.02): 1260-1270 K
* invariant reactions:
  * 1140-1150 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']
  * 1150-1160 K: ['fcc+liquid'] -> ['fcc+fcc', 'fcc+liquid']
  * 1190-1200 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.010-0.210 at T = 1160-1190 K (4 temperatures)
* fcc+fcc x = 0.010-0.240 at T = 1110-1140 K (4 temperatures)
* fcc+fcc x = 0.020-0.230 at T = 1100-1100 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1100 K fcc+fcc: x_a = 0.018 +/- 0.000, x_b = 0.233 +/- 0.000 (23/30 samples)
* 1100 K fcc+liquid: x_a = 0.246 +/- 0.130, x_b = 0.373 +/- 0.105 (30/30 samples)
* 1100 K liquid+fcc: x_a = 0.716 +/- 0.027, x_b = 0.967 +/- 0.004 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 900 K -16.6, 1130 K -20.0, 1360 K -22.6
* s01_fcc: 900 K -16.1, 1132 K -20.5, 1364 K -24.8
* s02_fcc: 900 K -16.1, 1132 K -20.4, 1364 K -24.7
* s03_fcc: 900 K -17.3, 1134 K -23.0, 1368 K -28.8
* s04_fcc: 900 K -18.3, 1134 K -24.4, 1368 K -30.1
* s05_fcc: 900 K -19.3, 1138 K -27.1, 1375 K -34.6
* s06_fcc: 900 K -19.6, 1138 K -27.5, 1375 K -35.3
* s07_fcc: 900 K -16.9, 1025 K -21.2, 1150 K -25.6
* s08_fcc: 900 K -19.5, 1025 K -24.3, 1150 K -29.1
* s15_fcc: 900 K -9.1, 1075 K -13.5, 1250 K -17.6
* s17_fcc: 900 K -1.8, 1100 K -3.7, 1300 K -5.7
* s18_fcc: 900 K +0.2, 1100 K -0.7, 1300 K -2.0
* s19_fcc: 900 K +1.0, 1186 K +1.3
* s20_fcc: 900 K +1.5, 1186 K +1.9
* s21_fcc: 900 K +1.4, 1188 K +1.7
* s22_fcc: 900 K +2.2, 1188 K +2.9
* s23_fcc: 900 K +0.4, 1190 K +0.8
* s24_fcc: 900 K +1.3, 1190 K +1.9

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0037696701483445902, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 0.0002988720000118667, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
