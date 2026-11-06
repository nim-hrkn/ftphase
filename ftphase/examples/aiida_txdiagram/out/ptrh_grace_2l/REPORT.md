# GRACE-2L-OMAT-medium-base-fp64 Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-05 17:32:10.  Classical level, 0.0 GPa, model GRACE-2L-OMAT-medium-base-fp64 (foundation, 2 layers, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [1910.0, 2400.0, 50] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'PtRh3': 0.002, 'fcc': 0.002, 'PtRh': 0.002, 'Pt3Rh': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1910 K; coexistences: fcc(0.000) + liquid(0.258); liquid(0.398) + fcc(0.504)
* pure-A melting bracket (x < 0.02): 2400-2410 K
* invariant reactions:
  * 1990-2000 K: ['PtRh3+fcc', 'fcc+liquid'] -> ['PtRh3+fcc', 'PtRh3+liquid', 'fcc+liquid']
  * 2030-2040 K: ['PtRh3+fcc', 'PtRh3+liquid', 'fcc+liquid'] -> ['fcc+liquid']
  * 2090-2100 K: ['fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* liquid+liquid x = 0.470-0.480 at T = 2100-2400 K (31 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1910 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.902 +/- 0.022 (20/30 samples)
* 1910 K fcc+PtRh3: x_a = 0.642 +/- 0.184, x_b = 0.806 +/- 0.021 (20/30 samples)
* 1910 K fcc+fcc: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (1/30 samples)
* 1910 K fcc+liquid: x_a = 0.000 +/- 0.000, x_b = 0.257 +/- 0.009 (30/30 samples)
* 1910 K liquid+fcc: x_a = 0.403 +/- 0.029, x_b = 0.506 +/- 0.017 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.01152687053837413, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.010662565411576473, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.005855612308174005, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.008988361745957286, 'flag': True}, {'T': 2000.0, 'phase': 'liquid', 'rmse_eV': 0.00026898183659230526, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
