# SevenNet-MF-ompa Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-14 03:30:43.  Classical level, 0.0 GPa, model SevenNet-MF-ompa (modal mpa; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 27 cells used, missing []
* liquids (calphy reversible scaling): 11 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '0.8984': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'NiAl3': 0.002, 'L12': 0.002, 'Ni2Al3': 0.002, 'B2': 0.002, 'fccNi': 0.002, 'fccAl': 0.002, 'liquid': 0.0014}

## Key numbers

* lowest temperature with liquid on the grid: 950 K; coexistences: fccAl(0.000) + liquid(0.029); liquid(0.107) + NiAl3(0.250)
* pure-A melting bracket (x < 0.02): 970-980 K
* invariant reactions:
  * 970-980 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid']
  * 1030-1040 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid']
  * 1390-1400 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1610-1620 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid']
  * 1640-1650 K: ['B2+B2', 'B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+liquid', 'L12+fccNi', 'L12+liquid']
  * 1660-1670 K: ['B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+liquid', 'L12+liquid', 'fccNi+liquid']
  * 1680-1690 K: ['B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'L12+liquid']
  * 1780-1790 K: ['B2+liquid', 'L12+liquid'] -> ['B2+liquid']
* two-phase regions at 1000 K: liquid(0.132)-NiAl3(0.250); NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.487); B2(0.490)-B2(0.500); B2(0.559)-L12(0.756); L12(0.781)-fccNi(0.957)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.480-0.500 at T = 1210-1640 K (44 temperatures)
* B2+B2 x = 0.490-0.500 at T = 950-1200 K (26 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+B2: x_a = 0.491 +/- 0.000, x_b = 0.500 +/- 0.000 (29/30 samples)
* 950 K B2+L12: x_a = 0.553 +/- 0.007, x_b = 0.755 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.962 +/- 0.009 (30/30 samples)
* 950 K Ni2Al3+B2: x_a = 0.400 +/- 0.000, x_b = 0.489 +/- 0.001 (30/30 samples)
* 950 K NiAl3+Ni2Al3: x_a = 0.250 +/- 0.000, x_b = 0.400 +/- 0.000 (30/30 samples)
* 950 K fccAl+liquid: x_a = 0.000 +/- 0.000, x_b = 0.031 +/- 0.017 (27/30 samples)
* 950 K liquid+NiAl3: x_a = 0.104 +/- 0.008, x_b = 0.250 +/- 0.000 (30/30 samples)

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.004845469938934536, 'flag': False}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 1.9186846773327266e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccAl', 'rmse_eV': 1.2560739669470201e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 0.0032055816793028517, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.0014018759202377407, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
