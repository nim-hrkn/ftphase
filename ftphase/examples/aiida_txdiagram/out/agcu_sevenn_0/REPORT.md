# SevenNet-0 Ag-Cu, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-30 11:53:11.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 25 cells used, missing []
* liquids (calphy reversible scaling): 3 runs used, missing ['lqd_x0_50', 'lqd_x0_60', 'lqd_x0_80', 'lqd_x1_00']; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1}
* configurational terms: {'fcc': 'ideal'}; fits: {'fcc': 'rk', 'liquid': 'rk'} (poly = excess over analytic ideal mixing)
* temperature grid: [1050.0, 1400.0, 36] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'fcc': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1050 K; coexistences: liquid(0.000) + fcc(0.031)
* pure-A melting bracket (x < 0.02): 1400-1410 K
* invariant reactions:
  * 1240-1250 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.100-0.980 at T = 1120-1130 K (2 temperatures)
* fcc+fcc x = 0.110-0.970 at T = 1150-1210 K (7 temperatures)
* fcc+fcc x = 0.110-0.980 at T = 1050-1140 K (8 temperatures)
* fcc+fcc x = 0.120-0.960 at T = 1230-1240 K (2 temperatures)
* fcc+fcc x = 0.120-0.970 at T = 1220-1220 K (1 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1050 K fcc+fcc: x_a = 0.112 +/- 0.000, x_b = 0.983 +/- 0.000 (30/30 samples)
* 1050 K liquid+fcc: x_a = 0.007 +/- 0.036, x_b = 0.063 +/- 0.170 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1100 K: [{'T': 1100.0, 'phase': 'fcc', 'rmse_eV': 0.0026936126894689157, 'flag': False}, {'T': 1100.0, 'phase': 'liquid', 'rmse_eV': 3.303418813223254e-15, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
