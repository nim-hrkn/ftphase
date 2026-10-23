# smoke test Ag-Cu (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-23 16:24:00.  Classical level, 0.0 GPa, model CuAg.eam.alloy (Williams-Mishin-Hamilton 2006 EAM).

## Inputs

* solids (QHA, lowered to the classical level): 3 cells used, missing []
* liquids (calphy reversible scaling): 2 runs used, missing []; runs per x {'0.0000': 1, '0.5000': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [1200.0, 1400.0, 21] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* invariant reactions:

## Error bands (Monte Carlo over per-phase offsets)


## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fcc: 1000 K -8.4, 1050 K -8.7, 1100 K -8.5
* s02_fcc: 1000 K +19.0, 1050 K +19.9, 1100 K +21.8

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1200 K: [{'T': 1200.0, 'phase': 'liquid', 'rmse_eV': 1.1322097734007351e-15, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
