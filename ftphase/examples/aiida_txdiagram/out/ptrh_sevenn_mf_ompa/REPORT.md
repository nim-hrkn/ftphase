# SevenNet-MF-ompa Pt-Rh, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-08 01:14:07.  Classical level, 0.0 GPa, model SevenNet-MF-ompa (modal mpa; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 42 cells used, missing []
* liquids (calphy reversible scaling): 7 runs used, missing []; runs per x {'0.0000': 1, '0.1992': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.8008': 1, '1.0000': 1}
* configurational terms: {'fcc': 'ideal', 'PtRh': 'sublattice:b32_antisite', 'PtRh3': 'sublattice:b32_antisite@0.75', 'Pt3Rh': 'sublattice:b32_antisite@0.25'}; fits: {'fcc': 'rk', 'liquid': 'rk', 'PtRh': 'poly', 'PtRh3': 'poly', 'Pt3Rh': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [1910.0, 2400.0, 50] (K, min, max, points); sigma (eV/atom): {'PtRh': 0.002, 'fcc': 0.002, 'liquid': 0.0014, 'PtRh3': 0.002, 'Pt3Rh': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1910 K; coexistences: fcc(0.000) + liquid(0.140); liquid(0.431) + fcc(0.490)
* pure-A melting bracket (x < 0.02): 2400-2410 K
* invariant reactions:
  * 1930-1940 K: ['fcc+fcc', 'fcc+liquid'] -> ['fcc+liquid']
  * 2090-2100 K: ['fcc+liquid'] -> ['fcc+liquid', 'liquid+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* fcc+fcc x = 0.710-0.820 at T = 1930-1930 K (1 temperatures)
* fcc+fcc x = 0.720-0.820 at T = 1920-1920 K (1 temperatures)
* fcc+fcc x = 0.730-0.810 at T = 1910-1910 K (1 temperatures)
* liquid+liquid x = 0.470-0.480 at T = 2100-2400 K (31 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1910 K PtRh3+fcc: x_a = 0.812 +/- 0.000, x_b = 0.843 +/- 0.000 (1/30 samples)
* 1910 K fcc+PtRh3: x_a = 0.713 +/- 0.000, x_b = 0.812 +/- 0.000 (1/30 samples)
* 1910 K fcc+fcc: x_a = 0.646 +/- 0.119, x_b = 0.703 +/- 0.153 (28/30 samples)
* 1910 K fcc+fcc#1: x_a = 0.728 +/- 0.000, x_b = 0.808 +/- 0.000 (9/30 samples)
* 1910 K fcc+liquid: x_a = 0.000 +/- 0.000, x_b = 0.141 +/- 0.015 (30/30 samples)
* 1910 K fcc+liquid#1: x_a = 0.573 +/- 0.000, x_b = 0.602 +/- 0.000 (1/30 samples)
* 1910 K liquid+fcc: x_a = 0.449 +/- 0.076, x_b = 0.524 +/- 0.097 (30/30 samples)
* 1910 K liquid+fcc#1: x_a = 0.602 +/- 0.000, x_b = 0.635 +/- 0.000 (1/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 2000 K: [{'T': 2000.0, 'phase': 'Pt3Rh', 'rmse_eV': 0.013393239171190252, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh', 'rmse_eV': 0.005551935344671822, 'flag': True}, {'T': 2000.0, 'phase': 'PtRh3', 'rmse_eV': 0.008156996287218523, 'flag': True}, {'T': 2000.0, 'phase': 'fcc', 'rmse_eV': 0.008035094046317052, 'flag': True}, {'T': 2000.0, 'phase': 'liquid', 'rmse_eV': 0.0002445881175844158, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
