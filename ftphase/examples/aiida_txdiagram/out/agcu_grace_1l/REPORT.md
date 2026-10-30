# GRACE-1L-OMAT-medium-base-fp64 Ag-Cu, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-31 03:31:17.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 25 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [1100.0, 1400.0, 31] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: liquid(0.020) + fcc(0.025); fcc(0.170) + liquid(0.232); liquid(0.305) + fcc(0.975)
* invariant reactions:

## Error bands (Monte Carlo over per-phase offsets)

* 1100 K fcc+fcc: x_a = 0.188 +/- 0.000, x_b = 0.975 +/- 0.000 (12/30 samples)
* 1100 K fcc+liquid: x_a = 0.167 +/- 0.013, x_b = 0.228 +/- 0.037 (8/30 samples)
* 1100 K liquid+fcc: x_a = 0.245 +/- 0.128, x_b = 0.718 +/- 0.416 (18/30 samples)
* 1100 K liquid+fcc#1: x_a = 0.309 +/- 0.003, x_b = 0.975 +/- 0.000 (5/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0019968048632113614, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 3.0524091870596127e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
