# smoke test (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-30 23:38:33.  Classical level, 0.0 GPa, model MACE-MPA-0 medium (float32, ML-IAP).

## Inputs

* solids (QHA, lowered to the classical level): 5 cells used, missing []
* liquids (calphy reversible scaling): 2 runs used, missing []; runs per x {'0.0000': 1, '0.2037': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [900.0, 1100.0, 21] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'B32': 0.002, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 950 K; coexistences: liquid(0.006) + fcc(0.011)
* pure-A melting bracket (x < 0.02): 950-960 K
* invariant reactions:
* two-phase regions at 1000 K: liquid(0.086)-fcc(0.160)

## Error bands (Monte Carlo over per-phase offsets)

* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (5/5 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 1.1322097734007351e-15, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 1.1322097734007351e-15, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
