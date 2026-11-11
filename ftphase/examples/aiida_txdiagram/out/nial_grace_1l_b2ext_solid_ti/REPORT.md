# GRACE-1L-OMAT-medium-base-fp64 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-12 07:59:05.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 9 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50', 'lqd_x0_60', 'lqd_x0_70', 'lqd_x0_80', 'lqd_x0_90', 'lqd_x1_00']; runs per x {}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [900.0, 2000.0, 111] (K, min, max, points); sigma (eV/atom): {'fccNi': 0.002, 'fccAl': 0.002, 'B2': 0.002}

## Key numbers

* invariant reactions:
  * 1000-1010 K: ['B2+fccAl', 'B2+fccNi'] -> ['B2+B2', 'B2+fccAl', 'B2+fccNi']
  * 1620-1630 K: ['B2+B2', 'B2+fccAl', 'B2+fccNi'] -> ['B2+B2', 'B2+fccNi']
  * 1700-1710 K: ['B2+B2', 'B2+fccNi'] -> ['B2+fccNi']
* two-phase regions at 900 K: fccAl(0.000)-B2(0.426); B2(0.685)-fccNi(1.000)
* two-phase regions at 1000 K: fccAl(0.000)-B2(0.426); B2(0.685)-fccNi(1.000)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.490-0.500 at T = 1010-1700 K (70 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 900 K B2+fccNi: x_a = 0.685 +/- 0.000, x_b = 1.000 +/- 0.000 (30/30 samples)
* 900 K fccAl+B2: x_a = 0.000 +/- 0.000, x_b = 0.426 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s03_B2: 1000 K -2.4, 1350 K -4.6, 1700 K -8.1
* s04_B2: 1000 K -1.5, 1350 K -2.9, 1700 K -5.0
* s05_B2: 1000 K -0.8, 1350 K -1.7, 1700 K -3.0
* s06_B2: 1000 K +1.0, 1350 K +1.6, 1700 K +2.3
* s07_B2: 1000 K -2.2, 1399 K -4.3, 1797 K -7.0
* s08_B2: 1000 K +0.1, 1399 K -0.7, 1797 K -2.2

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.003176214585772088, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
