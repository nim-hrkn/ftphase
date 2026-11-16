# SevenNet-0 Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-16 01:11:09.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 9 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'fcc': 0.002, 'Al3Li': 0.002}

## Key numbers

* invariant reactions:
  * 450-460 K: ['Al3Li+B32', 'Al3Li+fcc'] -> ['B32+fcc']
  * 710-720 K: ['B32+fcc'] -> ['B32+fcc', 'fcc+fcc']
* two-phase regions at 700 K: fcc(0.250)-B32(0.477)
* two-phase regions at 800 K: fcc(0.219)-fcc(0.250); fcc(0.250)-B32(0.477)
* two-phase regions at 900 K: fcc(0.194)-fcc(0.250); fcc(0.250)-B32(0.478)
* two-phase regions at 1000 K: fcc(0.175)-fcc(0.250); fcc(0.250)-B32(0.481)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.160-0.250 at T = 1070-1100 K (4 temperatures)
* fcc+fcc x = 0.170-0.250 at T = 1010-1060 K (6 temperatures)
* fcc+fcc x = 0.180-0.250 at T = 950-1000 K (6 temperatures)
* fcc+fcc x = 0.190-0.250 at T = 900-940 K (5 temperatures)
* fcc+fcc x = 0.200-0.250 at T = 860-890 K (4 temperatures)
* fcc+fcc x = 0.210-0.250 at T = 820-850 K (4 temperatures)
* fcc+fcc x = 0.220-0.250 at T = 780-810 K (4 temperatures)
* fcc+fcc x = 0.230-0.250 at T = 750-770 K (3 temperatures)
* fcc+fcc x = 0.240-0.250 at T = 720-740 K (3 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.477 +/- 0.003 (30/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.476 +/- 0.004 (30/30 samples)
* 800 K fcc+fcc: x_a = 0.219 +/- 0.000, x_b = 0.250 +/- 0.000 (30/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.476 +/- 0.005 (30/30 samples)
* 900 K fcc+fcc: x_a = 0.194 +/- 0.000, x_b = 0.250 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0004783796443545437, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
