# DPA-4.1-Air-OAM Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-12 00:23:56.  Classical level, 0.0 GPa, model DPA-4.1-Air-OAM (deepmd 1ded5d2, .pt2).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'Al3Li': 0.002, 'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 830 K; coexistences: fcc(0.176) + liquid(0.337); liquid(0.337) + B32(0.509)
* pure-A melting bracket (x < 0.02): 1030-1040 K
* invariant reactions:
  * 820-830 K: ['B32+fcc'] -> ['B32+liquid', 'fcc+liquid']
  * 880-890 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.157)-B32(0.507)
* two-phase regions at 800 K: fcc(0.172)-B32(0.508)
* two-phase regions at 900 K: fcc(0.137)-liquid(0.246)
* two-phase regions at 1000 K: fcc(0.048)-liquid(0.079)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.157 +/- 0.007, x_b = 0.507 +/- 0.001 (30/30 samples)
* 800 K fcc+B32: x_a = 0.172 +/- 0.007, x_b = 0.508 +/- 0.001 (28/30 samples)
* 800 K fcc+liquid: x_a = 0.155 +/- 0.005, x_b = 0.284 +/- 0.012 (2/30 samples)
* 800 K liquid+B32: x_a = 0.331 +/- 0.028, x_b = 0.508 +/- 0.002 (2/30 samples)
* 900 K fcc+liquid: x_a = 0.130 +/- 0.024, x_b = 0.231 +/- 0.049 (30/30 samples)
* 900 K liquid+B32: x_a = 0.498 +/- 0.011, x_b = 0.551 +/- 0.013 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 2.5639502485114184e-16, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0001047243829177811, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.00018789735358154191, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
