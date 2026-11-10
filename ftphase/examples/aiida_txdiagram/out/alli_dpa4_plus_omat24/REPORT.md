# DPA4-Plus-OMat24 v20260805 Al-Li, x_Li <= 0.5, 0 GPa: QHA solids (classical level) + calphy liquid [AiiDA ftphase.txdiagram] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-10 09:11:38.  Classical level, 0.0 GPa, model DPA4-Plus-OMat24 v20260805 (deepmd 3.2.0, .pt2).

## Inputs

* solids (QHA, lowered to the classical level): 13 cells used, missing []
* liquids (calphy reversible scaling): 6 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal', 'B32': 'sublattice:b32_antisite'}; fits: {'fcc': 'poly', 'liquid': 'poly', 'B32': 'spline'} (poly = excess over analytic ideal mixing)
* temperature grid: [700.0, 1100.0, 41] (K, min, max, points); sigma (eV/atom): {'B32': 0.002, 'Al3Li': 0.002, 'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 760 K; coexistences: fcc(0.176) + liquid(0.374); liquid(0.392) + B32(0.524)
* pure-A melting bracket (x < 0.02): 980-990 K
* invariant reactions:
  * 750-760 K: ['B32+fcc'] -> ['B32+liquid', 'fcc+liquid']
  * 810-820 K: ['B32+liquid', 'fcc+liquid'] -> ['fcc+liquid']
* two-phase regions at 700 K: fcc(0.162)-B32(0.515)
* two-phase regions at 800 K: fcc(0.156)-liquid(0.331); liquid(0.471)-B32(0.562)
* two-phase regions at 900 K: fcc(0.087)-liquid(0.188)

## Error bands (Monte Carlo over per-phase offsets)

* 700 K fcc+B32: x_a = 0.162 +/- 0.011, x_b = 0.515 +/- 0.003 (30/30 samples)
* 800 K fcc+liquid: x_a = 0.151 +/- 0.019, x_b = 0.322 +/- 0.031 (30/30 samples)
* 800 K liquid+B32: x_a = 0.475 +/- 0.025, x_b = 0.562 +/- 0.003 (30/30 samples)
* 900 K fcc+liquid: x_a = 0.081 +/- 0.024, x_b = 0.175 +/- 0.047 (30/30 samples)
* 900 K liquid+B32: x_a = 0.500 +/- 0.000, x_b = 0.562 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 900 K: [{'T': 900.0, 'phase': 'B32', 'rmse_eV': 0.0, 'flag': False}, {'T': 900.0, 'phase': 'fcc', 'rmse_eV': 0.0002509308239528444, 'flag': False}, {'T': 900.0, 'phase': 'liquid', 'rmse_eV': 0.00016269281721093513, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
