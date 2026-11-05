# GRACE-1L-OMAT-medium-base-fp64 Ag-Cu, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-06 04:55:09.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 19 cells used, missing ['s09_fcc', 's10_fcc', 's11_fcc', 's12_fcc', 's13_fcc', 's14_fcc']
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [750.0, 1400.0, 66] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 940 K; coexistences: fcc(0.028) + liquid(0.102); liquid(0.110) + fcc(0.990)
* pure-A melting bracket (x < 0.02): 980-990 K
* invariant reactions:
  * 930-940 K: ['fcc+fcc'] -> ['fcc+liquid']
* two-phase regions at 800 K: fcc(0.009)-fcc(0.996)
* two-phase regions at 900 K: fcc(0.025)-fcc(0.990)
* two-phase regions at 1000 K: liquid(0.171)-fcc(0.987)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.000-1.000 at T = 750-780 K (4 temperatures)
* fcc+fcc x = 0.010-0.990 at T = 840-840 K (1 temperatures)
* fcc+fcc x = 0.010-1.000 at T = 790-830 K (5 temperatures)
* fcc+fcc x = 0.020-0.990 at T = 850-900 K (6 temperatures)
* fcc+fcc x = 0.030-0.990 at T = 910-930 K (3 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 750 K fcc+fcc: x_a = 0.002 +/- 0.000, x_b = 0.997 +/- 0.000 (30/30 samples)
* 790 K fcc+fcc: x_a = 0.006 +/- 0.000, x_b = 0.996 +/- 0.000 (30/30 samples)
* 890 K fcc+fcc: x_a = 0.024 +/- 0.000, x_b = 0.992 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 800 K -3.1, 1025 K -7.6, 1250 K -20.5
* s01_fcc: 700 K -1.5, 835 K -3.1, 969 K -5.8
* s02_fcc: 700 K -2.1, 835 K -3.7, 969 K -6.5
* s03_fcc: 700 K -1.6, 826 K -3.1, 951 K -5.7
* s04_fcc: 700 K -3.8, 826 K -5.7, 951 K -8.4
* s05_fcc: 700 K -8.4, 807 K -11.5, 914 K -14.8
* s06_fcc: 700 K -8.5, 807 K -11.6, 914 K -15.0
* s07_fcc: 672 K -8.6, 756 K -11.1, 840 K -13.7
* s08_fcc: 672 K -8.4, 756 K -10.9, 840 K -13.4
* s15_fcc: 700 K -3.0, 907 K -5.4, 1114 K -8.2
* s16_fcc: 700 K -4.5, 907 K -8.1, 1114 K -11.9
* s17_fcc: 700 K -0.6, 956 K -1.6, 1212 K -3.1
* s18_fcc: 700 K -0.8, 956 K -1.8, 1212 K -3.5
* s19_fcc: 700 K -0.3, 980 K -1.0, 1261 K -2.5
* s20_fcc: 700 K -0.4, 980 K -1.2, 1261 K -2.7
* s21_fcc: 700 K -0.4, 993 K -1.1, 1285 K -2.6
* s22_fcc: 700 K -0.5, 993 K -1.3, 1285 K -2.7
* s23_fcc: 900 K -1.2, 1160 K -2.3
* s24_fcc: 900 K -1.2, 1160 K -2.3

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 3.0524091870596127e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
