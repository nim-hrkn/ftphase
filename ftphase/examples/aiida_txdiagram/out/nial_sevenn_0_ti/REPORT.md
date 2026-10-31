# SevenNet-0 Ni-Al, 0 GPa: QHA solids + calphy liquid [AiiDA] (AiiDA workflow ftphase.txdiagram)

Assembled 2026-11-01 04:17:43.  Classical level, 0.0 GPa, model SevenNet-0 (11Jul2024, MPtrj; oeq deployment).

## Inputs

* solids (QHA, lowered to the classical level): 21 cells used, missing []
* liquids (calphy reversible scaling): 11 runs used, missing []; runs per x {'0.0000': 1, '0.1016': 1, '0.1992': 1, '0.3008': 1, '0.3984': 1, '0.5000': 1, '0.6016': 1, '0.6992': 1, '0.8008': 1, '0.8984': 1, '1.0000': 1}
* configurational terms: {'fccAl': 'ideal', 'fccNi': 'ideal', 'B2': 'sublattice:b2_triple_defect', 'L12': 'sublattice:b32_antisite@0.75'}; fits: {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'} (poly = excess over analytic ideal mixing)
* temperature grid: [950.0, 2000.0, 106] (K, min, max, points); sigma (eV/atom): {'fccNi': 0.002, 'Ni2Al3': 0.002, 'NiAl3': 0.002, 'liquid': 0.0014, 'L12': 0.002, 'B2': 0.002, 'fccAl': 0.002}

## Key numbers

* lowest temperature with liquid on the grid: 950 K; coexistences: liquid(0.000) + fccAl(0.031)
* pure-A melting bracket (x < 0.02): 2000-2010 K
* invariant reactions:
  * 1130-1140 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+fccAl', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid', 'fccAl+liquid']
  * 1240-1250 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid', 'fccAl+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid', 'fccAl+liquid']
  * 1250-1260 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid', 'fccAl+liquid'] -> ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid', 'fccAl+liquid']
  * 1270-1280 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid', 'fccAl+liquid']
  * 1440-1450 K: ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid']
  * 1470-1480 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'fccAl+liquid']
  * 1490-1500 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+liquid', 'fccAl+liquid']
* two-phase regions at 1000 K: liquid(0.000)-fccAl(0.031); fccAl(0.031)-NiAl3(0.250); NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.471); B2(0.489)-B2(0.500); B2(0.543)-L12(0.753); L12(0.781)-fccNi(0.929)

## Same-phase segments (fit noise unless wide and stable under the Monte Carlo)

* B2+B2 x = 0.470-0.500 at T = 1290-1290 K (1 temperatures)
* B2+B2 x = 0.470-0.530 at T = 1300-1340 K (5 temperatures)
* B2+B2 x = 0.470-0.540 at T = 1350-1390 K (5 temperatures)
* B2+B2 x = 0.470-0.550 at T = 1400-1440 K (5 temperatures)
* B2+B2 x = 0.470-0.560 at T = 1450-1480 K (4 temperatures)
* B2+B2 x = 0.470-0.570 at T = 1490-1530 K (5 temperatures)
* B2+B2 x = 0.470-0.580 at T = 1540-1570 K (4 temperatures)
* B2+B2 x = 0.470-0.590 at T = 1580-1620 K (5 temperatures)
* B2+B2 x = 0.470-0.600 at T = 1630-1670 K (5 temperatures)
* B2+B2 x = 0.470-0.610 at T = 1680-2000 K (33 temperatures)
* B2+B2 x = 0.490-0.500 at T = 950-1280 K (31 temperatures)

## Error bands (Monte Carlo over per-phase offsets)

* 950 K B2+B2: x_a = 0.488 +/- 0.000, x_b = 0.500 +/- 0.000 (30/30 samples)
* 950 K B2+L12: x_a = 0.544 +/- 0.007, x_b = 0.752 +/- 0.000 (30/30 samples)
* 950 K L12+fccNi: x_a = 0.781 +/- 0.000, x_b = 0.930 +/- 0.005 (30/30 samples)
* 950 K Ni2Al3+B2: x_a = 0.400 +/- 0.000, x_b = 0.471 +/- 0.000 (30/30 samples)
* 950 K NiAl3+Ni2Al3: x_a = 0.250 +/- 0.000, x_b = 0.400 +/- 0.000 (30/30 samples)
* 950 K fccAl+NiAl3: x_a = 0.031 +/- 0.000, x_b = 0.250 +/- 0.000 (30/30 samples)
* 950 K liquid+fccAl: x_a = 0.000 +/- 0.000, x_b = 0.031 +/- 0.000 (30/30 samples)

## QHA (classical level) minus calphy solid TI per cell, meV/atom (anharmonic error of the quasi-harmonic route)

* s00_fccAl: 600 K -34.4, 760 K -53.1, 920 K -73.4
* s03_fccNi: 1200 K +14.2, 1500 K +24.0, 1800 K +36.2
* s08_B2: 1300 K -57.4, 1650 K -88.3, 2000 K -122.6
* s16_L12: 1200 K -29.1, 1475 K -39.1, 1750 K -48.9

## Caveats

* table check: ["mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum)"]
* fit residuals at 1500 K: [{'T': 1500.0, 'phase': 'B2', 'rmse_eV': 0.023258475043052486, 'flag': True}, {'T': 1500.0, 'phase': 'L12', 'rmse_eV': 2.5121479338940403e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccAl', 'rmse_eV': 1.4043333874306805e-15, 'flag': False}, {'T': 1500.0, 'phase': 'fccNi', 'rmse_eV': 0.004702605159812528, 'flag': False}, {'T': 1500.0, 'phase': 'liquid', 'rmse_eV': 0.001652425194268428, 'flag': False}]
* every number is on the classical level of the potential; compare with experiment only after the quantum correction and potential error are accounted for.
