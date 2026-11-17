# MACE-MPA-0 medium Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-16 20:09:50.  Classical level, 0.0 GPa, model MACE-MPA-0 medium (float32, ML-IAP, cuEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 9 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'Al3Li': 0.002, 'fcc': 0.002}

## Key numbers

* invariant reactions:
  * 1000-1010 K: ['B32+fcc'] -> ['B32+B32', 'B32+fcc']
* two-phase regions at 700 K: fcc(0.250)-B32(0.493)
* two-phase regions at 800 K: fcc(0.250)-B32(0.492)
* two-phase regions at 900 K: fcc(0.250)-B32(0.488)
* two-phase regions at 1000 K: fcc(0.250)-B32(0.438)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B32+B32 x = 0.440-0.560 at T = 1010-1100 K (10 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.250 +/- 0.002, x_b = 0.494 +/- 0.002 (30/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.493 +/- 0.003 (30/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.489 +/- 0.006 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00029673467338124784, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
