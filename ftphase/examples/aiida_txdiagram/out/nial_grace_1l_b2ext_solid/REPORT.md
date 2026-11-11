# GRACE-1L-OMAT-medium-base-fp64 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-11 20:49:36.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 9 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50', 'lqd_x0_60', 'lqd_x0_70', 'lqd_x0_80', 'lqd_x0_90', 'lqd_x1_00']; runs per x {}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [900.0, 2000.0, 111] (K, min, max, points); sigma (eV/atom): {'fccNi': 0.002, 'fccAl': 0.002, 'B2': 0.002}

## Key numbers

* invariant reactions:
  * 1620-1630 K: ['B2+fccAl', 'B2+fccNi'] -> ['B2+fccNi']
  * 1960-1970 K: ['B2+fccNi'] -> ['B2+B2', 'B2+fccNi']
* two-phase regions at 900 K: fccAl(0.000)-B2(0.426); B2(0.685)-fccNi(1.000)
* two-phase regions at 1000 K: fccAl(0.000)-B2(0.426); B2(0.685)-fccNi(1.000)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.490-0.500 at T = 1970-2000 K (3 temperatures)
* B2+B2 x = 0.500-0.500 at T = 1980-1980 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 900 K B2+fccNi: x_a = 0.685 +/- 0.000, x_b = 1.000 +/- 0.000 (30/30 samples)
* 900 K fccAl+B2: x_a = 0.000 +/- 0.000, x_b = 0.426 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.004160628764408052, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
