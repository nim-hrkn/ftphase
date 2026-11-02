# NequIP-OAM-M 0.1 Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-02 13:26:45.  Classical level, 0.0 GPa, model NequIP-OAM-M 0.1 (ML-IAP, OpenEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'Al3Li': 0.002, 'liquid': 0.0014, 'B32': 0.002, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 810 K; coexistences: fcc(0.172) + liquid(0.320); liquid(0.327) + B32(0.498)
* invariant reactions:
  * 800-810 K: ['B32+fcc'] -> ['B32+liquid', 'fcc+liquid']
  * 890-900 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.151)-B32(0.497)
* two-phase regions at 800 K: fcc(0.172)-B32(0.498)
* two-phase regions at 900 K: fcc(0.101)-liquid(0.157)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.149 +/- 0.009, x_b = 0.497 +/- 0.001 (30/30 samples)
* 800 K fcc+B32: x_a = 0.170 +/- 0.008, x_b = 0.498 +/- 0.001 (20/30 samples)
* 800 K fcc+liquid: x_a = 0.160 +/- 0.015, x_b = 0.298 +/- 0.031 (10/30 samples)
* 800 K liquid+B32: x_a = 0.323 +/- 0.019, x_b = 0.498 +/- 0.001 (10/30 samples)
* 900 K fcc+liquid: x_a = 0.113 +/- 0.029, x_b = 0.184 +/- 0.058 (22/30 samples)
* 900 K liquid+B32: x_a = 0.466 +/- 0.036, x_b = 0.518 +/- 0.013 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00028600401483999785, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.0003179658686698706, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
