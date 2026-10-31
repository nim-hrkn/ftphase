# GRACE-1L-OMAT-medium-base-fp64 Ag-Cu, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-01 04:18:04.  Classical level, 0.0 GPa, model GRACE-1L-OMAT-medium-base-fp64 (foundation, 1 layer, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 25 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [1100.0, 1400.0, 31] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: liquid(0.041) + fcc(0.091)
* invariant reactions:
  * 1110-1120 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.180-0.980 at T = 1100-1100 K (1 temperatures)
* fcc+fcc x = 0.190-0.970 at T = 1110-1110 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1100 K fcc+fcc: x_a = 0.180 +/- 0.000, x_b = 0.981 +/- 0.000 (19/30 samples)
* 1100 K fcc+liquid: x_a = 0.171 +/- 0.008, x_b = 0.268 +/- 0.050 (8/30 samples)
* 1100 K liquid+fcc: x_a = 0.079 +/- 0.101, x_b = 0.181 +/- 0.268 (30/30 samples)
* 1100 K liquid+fcc#1: x_a = 0.339 +/- 0.011, x_b = 0.981 +/- 0.000 (8/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 800 K -3.1, 1025 K -7.6, 1250 K -20.5
* s23_fcc: 900 K -1.2, 1160 K -2.3

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0015869099399749653, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 3.0524091870596127e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
