# ACE Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-24 17:27:18.  Classical level, 0.0 GPa, model GRACE-FS-OAM (foundation, FS, 6 A).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'fcc': 0.002, 'liquid': 0.0014, 'Al3Li': 0.002, 'B32': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 750 K; coexistences: fcc(0.229) + liquid(0.316); liquid(0.323) + B32(0.438)
* pure-A melting bracket (x < 0.02): 950-960 K
* invariant reactions:
  * 740-750 K: ['B32+fcc'] -> ['B32+liquid', 'fcc+liquid']
  * 800-810 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.225)-B32(0.438)
* two-phase regions at 800 K: fcc(0.197)-liquid(0.285); liquid(0.394)-B32(0.438); B32(0.487)-liquid(0.500)
* two-phase regions at 900 K: fcc(0.120)-liquid(0.241)
* two-phase regions at 1000 K: liquid(0.051)-fcc(0.125); fcc(0.125)-liquid(0.219)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.225 +/- 0.011, x_b = 0.438 +/- 0.000 (30/30 samples)
* 800 K B32+liquid: x_a = 0.467 +/- 0.022, x_b = 0.483 +/- 0.018 (6/30 samples)
* 800 K fcc+liquid: x_a = 0.196 +/- 0.021, x_b = 0.284 +/- 0.023 (30/30 samples)
* 800 K liquid+B32: x_a = 0.415 +/- 0.063, x_b = 0.479 +/- 0.059 (30/30 samples)
* 800 K liquid+B32#1: x_a = 0.500 +/- 0.000, x_b = 0.523 +/- 0.009 (6/30 samples)
* 900 K fcc+liquid: x_a = 0.120 +/- 0.022, x_b = 0.242 +/- 0.017 (30/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0001676033593018273, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 2.818224422583964e-05, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
