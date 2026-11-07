# smoke test (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-08 08:42:12.  Classical level, 0.0 GPa, model DPA4-Air-OMat24 v20260805 (deepmd 3.2.0, .pt2).

## Inputs

* solids (QHA, lowered to the classical level): 5 cells used, missing []
* liquids (calphy reversible scaling): 2 runs used, missing []; runs per x {'0.0000': 1, '0.2037': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [900.0, 1100.0, 21] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'fcc': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 900 K; coexistences: liquid(0.068) + fcc(0.152)
* invariant reactions:
* two-phase regions at 900 K: liquid(0.068)-fcc(0.152)

## Error bands (Monte Carlo over per-phase offsets)

* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (5/5 samples)
* 900 K liquid+fcc: x_a = 0.081 +/- 0.014, x_b = 0.177 +/- 0.027 (5/5 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 1.4043333874306805e-15, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 3.1401849173675503e-16, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
