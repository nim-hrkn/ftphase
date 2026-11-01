# MatterSim-v1.0.0-1M Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-02 02:09:10.  Classical level, 0.0 GPa, model MatterSim-v1.0.0-1M (float32, ML-IAP).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'Al3Li': 0.002, 'liquid': 0.0014, 'B32': 0.002, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 700 K; coexistences: fcc(0.224) + liquid(0.342)
* pure-A melting bracket (x < 0.02): 770-780 K
* invariant reactions:
* two-phase regions at 700 K: fcc(0.224)-liquid(0.342)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+liquid: x_a = 0.223 +/- 0.017, x_b = 0.340 +/- 0.029 (30/30 samples)
* 700 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.560 +/- 0.008 (30/30 samples)
* 800 K fcc+liquid: x_a = 0.165 +/- 0.016, x_b = 0.210 +/- 0.032 (13/30 samples)
* 800 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)
* 800 K liquid+fcc: x_a = 0.045 +/- 0.018, x_b = 0.065 +/- 0.020 (11/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 6.547989211356251e-05, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.0002670109823481866, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
