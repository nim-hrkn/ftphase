# MatterSim-v1.0.0-5M Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (solids only) (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-17 00:33:17.  Classical level, 0.0 GPa, model MatterSim-v1.0.0-5M (float32, ML-IAP).

## Inputs

* solids (QHA, lowered to the classical level): 9 cells used, missing []
* liquids (calphy reversible scaling): 0 runs used, missing ['lqd_x0_00', 'lqd_x0_10', 'lqd_x0_20', 'lqd_x0_30', 'lqd_x0_40', 'lqd_x0_50']; runs per x {}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [300.0, 1100.0, 81] (K, min, max, points); sigma (eV/atom): {'Al3Li': 0.002, 'fcc': 0.002, 'B32': 0.002}

## Key numbers

* invariant reactions:
* two-phase regions at 700 K: fcc(0.250)-B32(0.562)
* two-phase regions at 800 K: fcc(0.250)-B32(0.562)
* two-phase regions at 900 K: fcc(0.250)-B32(0.562)
* two-phase regions at 1000 K: fcc(0.250)-B32(0.562)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: []
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 1.0735729156020888e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
