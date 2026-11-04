# GRACE-FS-OAM Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-10-30 01:27:37.  Classical level, 0.0 GPa, model GRACE-FS-OAM (foundation, FS, 6 A).

## Inputs

* solids (QHA, lowered to the classical level): 5 cells used, missing []
* liquids (calphy reversible scaling): 3 runs used, missing []; runs per x {'0.0000': 1, '0.5000': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [1700.0, 2000.0, 31] (K, min, max, points); sigma (eV/atom): {'liquid': 0.0014, 'B2': 0.002, 'fccNi': 0.002, 'fccAl': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 1700 K; coexistences: liquid(0.414) + B2(0.481); B2(0.562) + liquid(0.657)
* invariant reactions:
  * 1800-1810 K: ['B2+B2', 'B2+liquid'] -> ['B2+liquid']

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.490-0.520 at T = 1700-1800 K (11 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 1700 K B2+B2: x_a = 0.492 +/- 0.000, x_b = 0.515 +/- 0.000 (5/5 samples)
* 1700 K B2+liquid: x_a = 0.550 +/- 0.026, x_b = 0.640 +/- 0.037 (5/5 samples)
* 1700 K liquid+B2: x_a = 0.413 +/- 0.004, x_b = 0.480 +/- 0.001 (5/5 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1700 K: [{'T': 1700.0, 'phase': 'B2', 'rmse_eV': 3.4399002279594067e-15, 'flag': False}, {'T': 1700.0, 'phase': 'liquid', 'rmse_eV': 0.0, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
