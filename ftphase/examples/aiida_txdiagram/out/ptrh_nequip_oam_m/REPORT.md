# NequIP-OAM-M 0.1 Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-06 01:08:37.  Classical level, 0.0 GPa, model NequIP-OAM-M 0.1 (ML-IAP, OpenEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [1910.0, 2400.0, 50] (K, min, max, points); sigma (eV/atom): {'Pt3Rh': 0.002, 'liquid': 0.0014, 'PtRh3': 0.002, 'fcc': 0.002, 'PtRh': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1910 K; coexistences: fcc(0.001) + liquid(0.167); liquid(0.284) + fcc(0.492)
* pure-A melting bracket (x < 0.02): 2300-2310 K
* invariant reactions:
  * 2220-2230 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+fcc', 'fcc+liquid', 'liquid+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.780-0.960 at T = 1950-1980 K (4 temperatures)
* fcc+fcc x = 0.780-0.970 at T = 1990-2200 K (22 temperatures)
* fcc+fcc x = 0.780-0.980 at T = 2210-2400 K (20 temperatures)
* fcc+fcc x = 0.790-0.960 at T = 1910-1940 K (4 temperatures)
* liquid+liquid x = 0.470-0.480 at T = 2230-2400 K (18 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1910 K fcc+fcc: x_a = 0.788 +/- 0.000, x_b = 0.959 +/- 0.000 (30/30 samples)
* 1910 K fcc+liquid: x_a = 0.001 +/- 0.000, x_b = 0.167 +/- 0.012 (30/30 samples)
* 1910 K liquid+fcc: x_a = 0.285 +/- 0.013, x_b = 0.492 +/- 0.008 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.019495647465218573, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.013078568171320594, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.008155387654170934, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.006751249220048021, 'flag': True}, {'T': 2000.0, 'phase': 'liquid', 'rmse_eV': 4.4998263279349777e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
