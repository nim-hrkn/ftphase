# GRACE-1L-OMAT-medium-base-fp64 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-12 15:07:05.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 8 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50', 'lqd_x0_60', 'lqd_x0_70', 'lqd_x0_80', 'lqd_x0_90', 'lqd_x1_00']; runs per x {}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [900.0, 2000.0, 111] (K, min, max, points); sigma (eV/atom): {'fccNi': 0.002, 'fccAl': 0.002, 'L12': 0.002}

## Key numbers

* invariant reactions:
  * 1610-1620 K: ['L12+L12', 'L12+fccAl', 'L12+fccNi'] -> ['L12+fccAl', 'L12+fccNi']
  * 1620-1630 K: ['L12+fccAl', 'L12+fccNi'] -> ['L12+fccNi']
* two-phase regions at 900 K: fccAl(0.000)-L12(0.625); L12(0.750)-L12(0.766); L12(0.844)-fccNi(1.000)
* two-phase regions at 1000 K: fccAl(0.000)-L12(0.625); L12(0.750)-L12(0.764); L12(0.844)-fccNi(1.000)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* L12+L12 x = 0.700-0.760 at T = 1580-1610 K (4 temperatures)
* L12+L12 x = 0.710-0.760 at T = 1540-1570 K (4 temperatures)
* L12+L12 x = 0.720-0.760 at T = 1500-1530 K (4 temperatures)
* L12+L12 x = 0.730-0.760 at T = 1450-1490 K (5 temperatures)
* L12+L12 x = 0.740-0.760 at T = 1390-1440 K (6 temperatures)
* L12+L12 x = 0.750-0.760 at T = 940-1380 K (45 temperatures)
* L12+L12 x = 0.750-0.770 at T = 900-930 K (4 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 900 K L12+L12: x_a = 0.750 +/- 0.000, x_b = 0.766 +/- 0.000 (30/30 samples)
* 900 K L12+fccNi: x_a = 0.844 +/- 0.000, x_b = 1.000 +/- 0.000 (30/30 samples)
* 900 K fccAl+L12: x_a = 0.000 +/- 0.000, x_b = 0.625 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s03_L12: 1200 K -0.6, 1408 K -1.0, 1615 K -1.4
* s04_L12: 1200 K -1.1, 1408 K -1.5, 1615 K -2.1
* s05_L12: 1200 K -0.7, 1408 K -1.2, 1615 K -1.8
* s06_L12: 1200 K +0.2, 1408 K +0.5, 1615 K +0.9
* s07_L12: 1200 K +1.5, 1408 K +2.1, 1615 K +2.9

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'L12', 'rmse_eV': 0.0027796723177438455, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
