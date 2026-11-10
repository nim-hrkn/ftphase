# NequIP-OAM-M 0.1 Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-10 22:12:46.  Classical level, 0.0 GPa, model NequIP-OAM-M 0.1 (ML-IAP, OpenEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [1910.0, 2400.0, 50] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014, 'Pt3Rh': 0.002, 'PtRh3': 0.002, 'PtRh': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1910 K; coexistences: liquid(0.010) + fcc(0.031); fcc(0.031) + liquid(0.068); liquid(0.312) + fcc(0.563)
* pure-A melting bracket (x < 0.02): 1920-1930 K
* invariant reactions:
  * 2260-2270 K: ['fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* liquid+liquid x = 0.470-0.480 at T = 2270-2400 K (14 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1910 K fcc+liquid: x_a = 0.031 +/- 0.000, x_b = 0.072 +/- 0.016 (26/30 samples)
* 1910 K liquid+fcc: x_a = 0.062 +/- 0.116, x_b = 0.121 +/- 0.201 (30/30 samples)
* 1910 K liquid+fcc#1: x_a = 0.309 +/- 0.008, x_b = 0.561 +/- 0.007 (26/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 1400 K -61.2, 1550 K -67.9, 1700 K -72.6
* s23_fcc: 1700 K -53.2, 2025 K -78.4, 2350 K -103.3
* s24_fcc: 1700 K -53.2, 2025 K -78.4, 2350 K -103.3

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.019495647465218573, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.013078568171320594, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.008155387654170934, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.014239231318762187, 'flag': True}, {'T': 2000.0, 'phase': 'liquid', 'rmse_eV': 3.553320223891812e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
