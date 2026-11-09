# GRACE-2L-OMAT-medium-base-fp64 Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-09 16:29:19.  Classical level, 0.0 GPa, model GRACE-2L-OMAT-medium-base-fp64 (foundation, 2 layers, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [1910.0, 2400.0, 50] (K, min, max, points); sigma (eV/atom): {'PtRh3': 0.002, 'liquid': 0.0014, 'Pt3Rh': 0.002, 'PtRh': 0.002, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1910 K; coexistences: fcc(0.000) + liquid(0.258); liquid(0.453) + fcc(0.517)
* pure-A melting bracket (x < 0.02): 2400-2410 K
* invariant reactions:
  * 1910-1920 K: ['fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* liquid+liquid x = 0.470-0.480 at T = 1920-2400 K (49 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1910 K fcc+fcc: x_a = 0.472 +/- 0.000, x_b = 0.480 +/- 0.000 (3/30 samples)
* 1910 K fcc+liquid: x_a = 0.000 +/- 0.000, x_b = 0.258 +/- 0.008 (30/30 samples)
* 1910 K liquid+fcc: x_a = 0.465 +/- 0.057, x_b = 0.529 +/- 0.048 (30/30 samples)
* 1910 K liquid+liquid: x_a = 0.473 +/- 0.000, x_b = 0.480 +/- 0.000 (10/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s23_fcc: 1700 K -22.2, 2025 K -37.1, 2350 K -52.4
* s24_fcc: 1700 K -22.2, 2025 K -37.1, 2350 K -52.5

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.01152687053837413, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.010662565411576473, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.005855612308174005, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.010245065341272126, 'flag': True}, {'T': 2000.0, 'phase': 'liquid', 'rmse_eV': 0.0002390506694877179, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
