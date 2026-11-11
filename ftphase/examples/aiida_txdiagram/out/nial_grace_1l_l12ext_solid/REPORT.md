# GRACE-1L-OMAT-medium-base-fp64 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-12 08:50:51.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 8 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50', 'lqd_x0_60', 'lqd_x0_70', 'lqd_x0_80', 'lqd_x0_90', 'lqd_x1_00']; runs per x {}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [900.0, 2000.0, 111] (K, min, max, points); sigma (eV/atom): {'fccAl': 0.002, 'fccNi': 0.002, 'L12': 0.002}

## Key numbers

* invariant reactions:
  * 1620-1630 K: ['L12+L12', 'L12+fccAl', 'L12+fccNi'] -> ['L12+L12', 'L12+fccNi']
* two-phase regions at 900 K: fccAl(0.000)-L12(0.625); L12(0.750)-L12(0.766); L12(0.844)-fccNi(1.000)
* two-phase regions at 1000 K: fccAl(0.000)-L12(0.625); L12(0.750)-L12(0.764); L12(0.844)-fccNi(1.000)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* L12+L12 x = 0.620-0.770 at T = 1910-2000 K (10 temperatures)
* L12+L12 x = 0.630-0.770 at T = 1870-1900 K (4 temperatures)
* L12+L12 x = 0.640-0.770 at T = 1830-1860 K (4 temperatures)
* L12+L12 x = 0.650-0.770 at T = 1790-1820 K (4 temperatures)
* L12+L12 x = 0.660-0.770 at T = 1750-1780 K (4 temperatures)
* L12+L12 x = 0.670-0.770 at T = 1710-1740 K (4 temperatures)
* L12+L12 x = 0.680-0.770 at T = 1670-1700 K (4 temperatures)
* L12+L12 x = 0.690-0.760 at T = 1630-1660 K (4 temperatures)
* L12+L12 x = 0.700-0.760 at T = 1590-1620 K (4 temperatures)
* L12+L12 x = 0.710-0.760 at T = 1550-1580 K (4 temperatures)
* L12+L12 x = 0.720-0.760 at T = 1500-1540 K (5 temperatures)
* L12+L12 x = 0.730-0.760 at T = 1460-1490 K (4 temperatures)
* L12+L12 x = 0.740-0.760 at T = 1390-1450 K (7 temperatures)
* L12+L12 x = 0.750-0.760 at T = 940-1380 K (45 temperatures)
* L12+L12 x = 0.750-0.770 at T = 900-930 K (4 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 900 K L12+L12: x_a = 0.750 +/- 0.000, x_b = 0.766 +/- 0.000 (30/30 samples)
* 900 K L12+fccNi: x_a = 0.844 +/- 0.000, x_b = 1.000 +/- 0.000 (30/30 samples)
* 900 K fccAl+L12: x_a = 0.000 +/- 0.000, x_b = 0.625 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'L12', 'rmse_eV': 0.002803212920961973, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
