# SevenNet-0 Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-26 00:45:13.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014, 'Al3Li': 0.002, 'B32': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 940 K; coexistences: fcc(0.250) + liquid(0.500)
* invariant reactions:
  * 930-940 K: ['B32+fcc'] -> ['fcc+liquid']
  * 1000-1010 K: ['fcc+liquid'] -> ['fcc+fcc', 'fcc+liquid']
* two-phase regions at 700 K: fcc(0.250)-B32(0.479)
* two-phase regions at 800 K: fcc(0.250)-B32(0.479)
* two-phase regions at 900 K: fcc(0.250)-B32(0.481)
* two-phase regions at 1000 K: fcc(0.250)-liquid(0.500)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.240-0.250 at T = 1010-1100 K (10 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.479 +/- 0.003 (30/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.479 +/- 0.004 (30/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.480 +/- 0.005 (29/30 samples)
* 900 K fcc+liquid: x_a = 0.250 +/- 0.000, x_b = 0.500 +/- 0.000 (1/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (1/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 2.5639502485114184e-16, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0007346524752129251, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.00010135677392638773, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
