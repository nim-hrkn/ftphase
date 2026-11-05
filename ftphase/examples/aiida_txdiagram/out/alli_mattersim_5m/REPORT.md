# MatterSim-v1.0.0-5M Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-05 06:48:03.  Classical level, 0.0 GPa, model MatterSim-v1.0.0-5M (float32, ML-IAP).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'Al3Li': 0.002, 'liquid': 0.0014, 'B32': 0.002, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 730 K; coexistences: fcc(0.250) + liquid(0.500)
* pure-A melting bracket (x < 0.02): 1000-1010 K
* invariant reactions:
  * 720-730 K: ['B32+fcc', 'fcc+fcc'] -> ['fcc+fcc', 'fcc+liquid']
  * 990-1000 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.040)-fcc(0.153); fcc(0.250)-B32(0.562)
* two-phase regions at 800 K: fcc(0.037)-fcc(0.173); fcc(0.250)-liquid(0.500)
* two-phase regions at 900 K: fcc(0.035)-fcc(0.193); fcc(0.250)-liquid(0.500)
* two-phase regions at 1000 K: liquid(0.020)-fcc(0.215); fcc(0.250)-liquid(0.496)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.030-0.190 at T = 890-910 K (3 temperatures)
* fcc+fcc x = 0.030-0.200 at T = 920-960 K (5 temperatures)
* fcc+fcc x = 0.030-0.210 at T = 970-990 K (3 temperatures)
* fcc+fcc x = 0.040-0.150 at T = 700-700 K (1 temperatures)
* fcc+fcc x = 0.040-0.160 at T = 710-750 K (5 temperatures)
* fcc+fcc x = 0.040-0.170 at T = 760-800 K (5 temperatures)
* fcc+fcc x = 0.040-0.180 at T = 810-860 K (6 temperatures)
* fcc+fcc x = 0.040-0.190 at T = 870-880 K (2 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.250 +/- 0.000, x_b = 0.562 +/- 0.000 (28/30 samples)
* 700 K fcc+fcc: x_a = 0.040 +/- 0.000, x_b = 0.153 +/- 0.000 (30/30 samples)
* 700 K fcc+liquid: x_a = 0.250 +/- 0.000, x_b = 0.500 +/- 0.000 (2/30 samples)
* 700 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (2/30 samples)
* 800 K fcc+fcc: x_a = 0.037 +/- 0.000, x_b = 0.173 +/- 0.000 (30/30 samples)
* 800 K fcc+liquid: x_a = 0.250 +/- 0.000, x_b = 0.500 +/- 0.000 (30/30 samples)
* 800 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 900 K fcc+fcc: x_a = 0.035 +/- 0.000, x_b = 0.193 +/- 0.000 (30/30 samples)
* 900 K fcc+liquid: x_a = 0.250 +/- 0.000, x_b = 0.500 +/- 0.002 (30/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.00039087843108518474, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.0003125980449951683, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
