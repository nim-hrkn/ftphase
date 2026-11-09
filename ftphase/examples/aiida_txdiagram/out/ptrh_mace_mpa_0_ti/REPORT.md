# MACE-MPA-0 medium Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-10 03:51:35.  Classical level, 0.0 GPa, model MACE-MPA-0 medium (float32, ML-IAP, cuEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [1910.0, 2400.0, 50] (K, min, max, points); sigma (eV/atom): {'Pt3Rh': 0.002, 'PtRh': 0.002, 'fcc': 0.002, 'PtRh3': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 1910 K; coexistences: fcc(0.000) + liquid(0.208); liquid(0.448) + fcc(0.791); fcc(0.995) + liquid(1.000)
* pure-A melting bracket (x < 0.02): 2300-2310 K
* invariant reactions:
  * 1990-2000 K: ['fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* liquid+liquid x = 0.470-0.480 at T = 2000-2400 K (41 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1910 K fcc+liquid: x_a = 0.000 +/- 0.000, x_b = 0.208 +/- 0.009 (30/30 samples)
* 1910 K fcc+liquid#1: x_a = 0.990 +/- 0.003, x_b = 1.000 +/- 0.000 (15/30 samples)
* 1910 K liquid+fcc: x_a = 0.449 +/- 0.008, x_b = 0.791 +/- 0.003 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s23_fcc: 1900 K -85.8, 2050 K -100.0, 2200 K -114.1
* s24_fcc: 1900 K -85.8, 2050 K -100.0, 2200 K -114.1

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.023989900008966572, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.011636094964463446, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.0117724734226492, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.017483505471239502, 'flag': True}, {'T': 2000.0, 'phase': 'liquid', 'rmse_eV': 7.300492124687109e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
