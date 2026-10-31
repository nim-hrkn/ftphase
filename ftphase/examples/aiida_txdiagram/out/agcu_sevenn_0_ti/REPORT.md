# SevenNet-0 Ag-Cu, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-01 04:18:15.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 25 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [1100.0, 1400.0, 31] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1100 K; coexistences: liquid(0.000) + fcc(0.050)
* pure-A melting bracket (x < 0.02): 1400-1410 K
* invariant reactions:
  * 1130-1140 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']
  * 1140-1150 K: ['fcc+liquid'] -> ['fcc+fcc', 'fcc+liquid']
  * 1150-1160 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.140-1.000 at T = 1100-1100 K (1 temperatures)
* fcc+fcc x = 0.150-0.970 at T = 1110-1120 K (2 temperatures)
* fcc+fcc x = 0.150-1.000 at T = 1150-1150 K (1 temperatures)
* fcc+fcc x = 0.160-0.950 at T = 1130-1130 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1100 K fcc+fcc: x_a = 0.139 +/- 0.000, x_b = 0.998 +/- 0.000 (30/30 samples)
* 1100 K liquid+fcc: x_a = 0.001 +/- 0.001, x_b = 0.050 +/- 0.005 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 800 K -11.3
* s23_fcc: 900 K -8.7, 1125 K -11.9, 1350 K -15.1

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.00501053109135941, 'flag': True}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 0.0006423940179049913, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
