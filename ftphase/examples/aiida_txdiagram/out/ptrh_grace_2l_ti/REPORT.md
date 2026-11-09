# GRACE-2L-OMAT-medium-base-fp64 Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-10 03:49:08.  Classical level, 0.0 GPa, model GRACE-2L-OMAT-medium-base-fp64 (foundation, 2 layers, kokkos export).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [1910.0, 2400.0, 50] (K, min, max, points); sigma (eV/atom): {'Pt3Rh': 0.002, 'PtRh': 0.002, 'fcc': 0.002, 'PtRh3': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 1910 K; coexistences: liquid(0.410) + fcc(0.568); fcc(0.031) + liquid(0.165); liquid(0.410) + fcc(0.568)
* pure-A melting bracket (x < 0.02): 2040-2050 K
* invariant reactions:
  * 1970-1980 K: ['fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']
  * 2160-2170 K: ['fcc+liquid', 'liquid+liquid'] -> ['liquid+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* liquid+liquid x = 0.470-0.480 at T = 1980-2400 K (43 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1910 K fcc+liquid: x_a = 0.031 +/- 0.000, x_b = 0.163 +/- 0.013 (30/30 samples)
* 1910 K liquid+fcc: x_a = 0.115 +/- 0.183, x_b = 0.204 +/- 0.238 (30/30 samples)
* 1910 K liquid+fcc#1: x_a = 0.412 +/- 0.018, x_b = 0.569 +/- 0.011 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 1700 K -82.4, 1775 K -87.2, 1850 K -91.6
* s23_fcc: 1700 K -22.2, 2025 K -37.1, 2350 K -52.4
* s24_fcc: 1700 K -22.2, 2025 K -37.1, 2350 K -52.5

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.01152687053837413, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.010662565411576473, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.005855612308174005, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.01228936207317169, 'flag': True}, {'T': 2000.0, 'phase': 'liquid', 'rmse_eV': 0.0002390506694877179, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
