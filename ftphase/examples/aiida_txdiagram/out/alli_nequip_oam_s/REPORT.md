# NequIP-OAM-S 0.1 Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-05 08:57:56.  Classical level, 0.0 GPa, model NequIP-OAM-S 0.1 (ML-IAP, OpenEquivariance).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'Al3Li': 0.002, 'liquid': 0.0014, 'B32': 0.002, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 850 K; coexistences: B32(0.438) + liquid(0.500)
* pure-A melting bracket (x < 0.02): 1100-1110 K
* invariant reactions:
  * 840-850 K: ['B32+B32', 'B32+fcc'] -> ['B32+fcc', 'B32+liquid']
  * 900-910 K: ['B32+fcc', 'B32+liquid'] -> ['B32+fcc', 'B32+liquid', 'fcc+fcc', 'fcc+liquid']
  * 920-930 K: ['B32+fcc', 'B32+liquid', 'fcc+fcc', 'fcc+liquid'] -> ['fcc+fcc', 'fcc+liquid']
* two-phase regions at 700 K: fcc(0.250)-B32(0.438); B32(0.438)-B32(0.562)
* two-phase regions at 800 K: fcc(0.250)-B32(0.438); B32(0.438)-B32(0.562)
* two-phase regions at 900 K: fcc(0.250)-B32(0.438); B32(0.438)-liquid(0.500)
* two-phase regions at 1000 K: liquid(0.000)-fcc(0.062); fcc(0.062)-fcc(0.126); fcc(0.250)-liquid(0.468)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B32+B32 x = 0.440-0.560 at T = 700-840 K (15 temperatures)
* fcc+fcc x = 0.060-0.110 at T = 910-940 K (4 temperatures)
* fcc+fcc x = 0.060-0.120 at T = 950-990 K (5 temperatures)
* fcc+fcc x = 0.060-0.130 at T = 1000-1080 K (8 temperatures)
* fcc+fcc x = 0.060-0.140 at T = 1050-1100 K (3 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K B32+B32: x_a = 0.438 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.438 +/- 0.000 (30/30 samples)
* 800 K B32+B32: x_a = 0.438 +/- 0.000, x_b = 0.562 +/- 0.000 (29/30 samples)
* 800 K B32+liquid: x_a = 0.438 +/- 0.000, x_b = 0.500 +/- 0.000 (1/30 samples)
* 800 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.438 +/- 0.000 (30/30 samples)
* 800 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (1/30 samples)
* 900 K B32+B32: x_a = 0.438 +/- 0.000, x_b = 0.562 +/- 0.000 (3/30 samples)
* 900 K B32+liquid: x_a = 0.438 +/- 0.000, x_b = 0.497 +/- 0.006 (25/30 samples)
* 900 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.438 +/- 0.000 (28/30 samples)
* 900 K fcc+liquid: x_a = 0.250 +/- 0.000, x_b = 0.471 +/- 0.009 (2/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (27/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 2.5639502485114184e-16, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00014024162868696668, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.0001790748564455042, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
