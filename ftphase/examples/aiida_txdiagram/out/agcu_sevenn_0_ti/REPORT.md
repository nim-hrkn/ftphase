# SevenNet-0 Ag-Cu, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-06 04:55:36.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 19 cells used, missing ['s09_fcc', 's10_fcc', 's11_fcc', 's12_fcc', 's13_fcc', 's14_fcc']
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [750.0, 1400.0, 66] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 900 K; coexistences: fcc(0.016) + liquid(0.091); liquid(0.112) + fcc(0.993)
* pure-A melting bracket (x < 0.02): 940-950 K
* invariant reactions:
  * 890-900 K: ['fcc+fcc'] -> ['fcc+liquid']
* two-phase regions at 800 K: fcc(0.007)-fcc(1.000)
* two-phase regions at 900 K: fcc(0.016)-liquid(0.091); liquid(0.112)-fcc(0.993)
* two-phase regions at 1000 K: liquid(0.234)-fcc(0.990)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.000-1.000 at T = 750-790 K (5 temperatures)
* fcc+fcc x = 0.010-1.000 at T = 800-830 K (4 temperatures)
* fcc+fcc x = 0.020-1.000 at T = 840-890 K (6 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 750 K fcc+fcc: x_a = 0.000 +/- 0.000, x_b = 1.000 +/- 0.000 (30/30 samples)
* 790 K fcc+fcc: x_a = 0.003 +/- 0.000, x_b = 1.000 +/- 0.000 (30/30 samples)
* 890 K fcc+fcc: x_a = 0.020 +/- 0.000, x_b = 0.998 +/- 0.000 (23/30 samples)
* 890 K fcc+liquid: x_a = 0.016 +/- 0.005, x_b = 0.064 +/- 0.027 (7/30 samples)
* 890 K liquid+fcc: x_a = 0.103 +/- 0.003, x_b = 0.998 +/- 0.000 (7/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 800 K -11.3
* s01_fcc: 700 K -9.9, 815 K -15.0, 931 K -22.1
* s02_fcc: 700 K -9.1, 815 K -14.1, 931 K -21.0
* s03_fcc: 700 K -13.1, 807 K -18.2, 913 K -24.1
* s04_fcc: 700 K -15.3, 807 K -21.2, 913 K -27.7
* s05_fcc: 700 K -18.2, 789 K -23.5, 878 K -29.2
* s06_fcc: 700 K -19.6, 789 K -25.0, 878 K -30.9
* s07_fcc: 645 K -9.7, 726 K -12.8, 807 K -16.2
* s08_fcc: 645 K -8.9, 726 K -11.8, 807 K -15.0
* s15_fcc: 700 K -5.9, 853 K -8.2, 1005 K -10.2
* s16_fcc: 700 K -6.2, 820 K -8.3, 940 K -10.4
* s17_fcc: 700 K -5.1, 897 K -7.8, 1093 K -10.7
* s18_fcc: 700 K -5.0, 897 K -8.0, 1093 K -11.4
* s19_fcc: 700 K -2.6, 919 K -4.4, 1138 K -6.5
* s20_fcc: 700 K -3.8, 919 K -5.9, 1138 K -8.2
* s21_fcc: 700 K -4.1, 930 K -6.4, 1160 K -9.1
* s22_fcc: 700 K -3.9, 930 K -6.2, 1160 K -8.9
* s23_fcc: 900 K -8.7, 1125 K -11.9, 1350 K -15.1
* s24_fcc: 900 K -8.7, 1125 K -11.9, 1350 K -15.1

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 0.0006423940179049913, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
