# Example 7: Ni-Al T-x diagram, Purja Pun & Mishin 2009 EAM (classical level, 0 GPa)

Assembled 2026-10-22 22:46:16 on mygardenx1.  Files: out/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.

## Inputs

* potential: potentials/nial/Mishin-Ni-Al-2009.eam.alloy (NIST, Purja Pun & Mishin, Philos. Mag. 89, 3245 (2009)).
* solids: QHA of 64-atom SQS (fcc(Al) x = 0-0.03, fcc(Ni) x = 0.75-1), B2 54-atom cells with Ni anti-sites (Ni-rich) and Ni vacancies (Al-rich), L1_2 108-atom cells with anti-sites, Ni2Al3 and NiAl3 point phases; quantum QHA lowered to the classical level.
* liquids: calphy reversible scaling 2000 K -> T_stop(x), UFM, 3 iterations, 3 independent runs per composition averaged; compositions 0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00.
* configurational terms: ideal mixing (fcc), triple-defect sublattice model (B2: anti-sites + vacancies), two-sublattice anti-site model (L1_2).
* fits: liquid = ideal mixing + 4-term Redlich-Kister; fcc = polynomial excess over ideal mixing; B2, L1_2 = natural spline.

Temperature grid 950-2000 K (106 points); liquid runs per composition {0.0: 3, 0.1016: 3, 0.1992: 3, 0.3008: 3, 0.3984: 3, 0.5: 3, 0.6016: 3, 0.6992: 3, 0.8008: 3, 0.8984: 3, 1.0: 3}; sigma in the Monte Carlo (eV/atom) {'Ni2Al3': 0.002, 'L12': 0.002, 'fccNi': 0.002, 'B2': 0.002, 'fccAl': 0.002, 'NiAl3': 0.002, 'liquid': 0.0014}

## Key numbers (experiment: NiAl congruent 1911 K, B2 range ~0.45-0.60; Ni3Al peritectic 1668 K; eutectic L -> Ni3Al + (Ni) 1658 K x~0.76; Al-rich eutectic 913 K; Al 933.5 K; Ni 1728 K)

* B2 + liquid up to 1900.0 K; lowest temperature with liquid on the grid 950.0 K
* B2 composition range [x_Ni lower, upper] vs T: 1000 K [0.5131062024377906, 0.5956737844198119]; 1100 K [0.5144666791001082, 0.5963894894203008]; 1200 K [0.5165115845567441, 0.5974397106195962]; 1300 K [0.5193410949112913, 0.5991239050341307]; 1400 K [0.5214949219631109, 0.6010080598812296]; 1500 K [0.5233770167193986, 0.6059804794171932]; 1600 K [0.5246645694905281, 0.6111111111111112]; 1700 K [0.5252742047948545, 0.6111111111111112]; 1800 K [0.5260151990900673, 0.6111111111111112]; 1900 K [0.5248674129936332, 0.5197928701790195]
* segments whose boundary sits at a sampled composition limit (flag edge=True in 07_two_phase_regions.tsv; the true width may be larger): 164
* invariant reactions (pairs change between T_low and T_high):
  * 950-960 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+L12', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+L12', 'L12+fccNi']
  * 1120-1130 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+L12', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1690-1700 K: ['B2+B2', 'B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+B2', 'B2+liquid', 'fccNi+liquid']
  * 1740-1750 K: ['B2+B2', 'B2+liquid', 'fccNi+liquid'] -> ['B2+B2', 'B2+liquid']
  * 1870-1880 K: ['B2+B2', 'B2+liquid'] -> ['B2+liquid']
* two-phase regions at 900 K: none
* two-phase regions at 1200 K: liquid(0.209)-B2(0.499); B2(0.516)-B2(0.552); B2(0.555)-B2(0.597); B2(0.611)-L12(0.778); L12(0.778)-fccNi(0.917)
* two-phase regions at 1500 K: liquid(0.304)-B2(0.498); B2(0.523)-B2(0.553); B2(0.556)-B2(0.606); B2(0.611)-L12(0.778); L12(0.778)-fccNi(0.907)
* two-phase regions at 1800 K: liquid(0.422)-B2(0.513); B2(0.526)-B2(0.554); B2(0.556)-B2(0.611); B2(0.611)-liquid(0.672)

## Same-phase segments (fit noise unless wide)

* B2+B2 x = 0.500-0.500 (width 0.005) at T = 1720-1720 K (1 temperatures)
* B2+B2 x = 0.510-0.550 (width 0.039) at T = 950-1120 K (18 temperatures)
* B2+B2 x = 0.520-0.550 (width 0.032) at T = 1130-1670 K (55 temperatures)
* B2+B2 x = 0.530-0.550 (width 0.028) at T = 1680-1870 K (20 temperatures)
* B2+B2 x = 0.550-0.600 (width 0.041) at T = 950-1060 K (12 temperatures)
* B2+B2 x = 0.560-0.600 (width 0.044) at T = 1070-1540 K (44 temperatures)
* B2+B2 x = 0.560-0.610 (width 0.054) at T = 1480-1860 K (36 temperatures)
* L12+L12 x = 0.760-0.780 (width 0.014) at T = 950-1120 K (18 temperatures)

## Error bands (Monte Carlo, 30 samples)

* 950 K B2+B2: x_a = 0.512 +/- 0.000, x_b = 0.553 +/- 0.000 (30/30)
* 950 K B2+B2#1: x_a = 0.555 +/- 0.000, x_b = 0.596 +/- 0.000 (30/30)
* 950 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.760 +/- 0.000 (30/30)
* 950 K L12+L12: x_a = 0.763 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 950 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.926 +/- 0.003 (30/30)
* 950 K fccAl+B2: x_a = 0.030 +/- 0.001, x_b = 0.499 +/- 0.000 (12/30)
* 950 K fccAl+liquid: x_a = 0.025 +/- 0.004, x_b = 0.123 +/- 0.016 (18/30)
* 950 K liquid+B2: x_a = 0.144 +/- 0.005, x_b = 0.499 +/- 0.000 (18/30)
* 1070 K B2+B2: x_a = 0.514 +/- 0.000, x_b = 0.553 +/- 0.000 (30/30)
* 1070 K B2+B2#1: x_a = 0.555 +/- 0.000, x_b = 0.596 +/- 0.000 (30/30)
* 1070 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.763 +/- 0.000 (30/30)
* 1070 K L12+L12: x_a = 0.764 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 1070 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.922 +/- 0.003 (30/30)
* 1070 K liquid+B2: x_a = 0.177 +/- 0.006, x_b = 0.499 +/- 0.000 (30/30)
* 1190 K B2+B2: x_a = 0.516 +/- 0.000, x_b = 0.553 +/- 0.000 (30/30)
* 1190 K B2+B2#1: x_a = 0.555 +/- 0.000, x_b = 0.597 +/- 0.000 (30/30)
* 1190 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 1190 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.918 +/- 0.003 (30/30)
* 1190 K liquid+B2: x_a = 0.205 +/- 0.004, x_b = 0.499 +/- 0.000 (30/30)
* 1310 K B2+B2: x_a = 0.520 +/- 0.000, x_b = 0.553 +/- 0.000 (30/30)
* 1310 K B2+B2#1: x_a = 0.556 +/- 0.000, x_b = 0.599 +/- 0.000 (30/30)
* 1310 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 1310 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.913 +/- 0.003 (30/30)
* 1310 K liquid+B2: x_a = 0.243 +/- 0.005, x_b = 0.499 +/- 0.000 (30/30)
* 1430 K B2+B2: x_a = 0.522 +/- 0.000, x_b = 0.553 +/- 0.000 (30/30)
* 1430 K B2+B2#1: x_a = 0.556 +/- 0.000, x_b = 0.602 +/- 0.000 (30/30)
* 1430 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 1430 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.909 +/- 0.003 (30/30)
* 1430 K liquid+B2: x_a = 0.280 +/- 0.004, x_b = 0.498 +/- 0.000 (30/30)
* 1550 K B2+B2: x_a = 0.524 +/- 0.000, x_b = 0.553 +/- 0.000 (30/30)
* 1550 K B2+B2#1: x_a = 0.556 +/- 0.000, x_b = 0.607 +/- 0.000 (30/30)
* 1550 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 1550 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.904 +/- 0.003 (30/30)
* 1550 K liquid+B2: x_a = 0.320 +/- 0.005, x_b = 0.498 +/- 0.000 (30/30)
* 1670 K B2+B2: x_a = 0.525 +/- 0.000, x_b = 0.554 +/- 0.000 (30/30)
* 1670 K B2+B2#1: x_a = 0.557 +/- 0.000, x_b = 0.611 +/- 0.000 (30/30)
* 1670 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 1670 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.900 +/- 0.003 (30/30)
* 1670 K liquid+B2: x_a = 0.363 +/- 0.005, x_b = 0.497 +/- 0.000 (30/30)
* 1790 K B2+B2: x_a = 0.526 +/- 0.000, x_b = 0.554 +/- 0.000 (30/30)
* 1790 K B2+B2#1: x_a = 0.556 +/- 0.000, x_b = 0.611 +/- 0.000 (30/30)
* 1790 K B2+liquid: x_a = 0.602 +/- 0.033, x_b = 0.665 +/- 0.044 (30/30)
* 1790 K liquid+B2: x_a = 0.415 +/- 0.006, x_b = 0.512 +/- 0.001 (30/30)

## QHA (classical level) minus calphy solid TI, per cell (anharmonic error of the quasi-harmonic route; mesh converged)

* fccNi x = 1.0000 at 1000 K: +22.4 meV/atom
* fccNi x = 1.0000 at 1500 K: +43.1 meV/atom
* fccNi x = 0.9375 at 1000 K: +13.0 meV/atom
* fccNi x = 0.9375 at 1500 K: +26.7 meV/atom
* fccNi x = 0.8750 at 1000 K: +13.3 meV/atom
* fccNi x = 0.8750 at 1500 K: +26.8 meV/atom
* fccNi x = 0.8125 at 1000 K: +12.0 meV/atom
* fccNi x = 0.8125 at 1500 K: +25.1 meV/atom
* fccNi x = 0.7500 at 1000 K: +13.5 meV/atom
* fccNi x = 0.7500 at 1500 K: +28.0 meV/atom
* B2 x = 0.5000 at 1000 K: +9.9 meV/atom
* B2 x = 0.5000 at 1500 K: +15.9 meV/atom
* B2 x = 0.5185 at 1000 K: +5.9 meV/atom
* B2 x = 0.5185 at 1500 K: +7.8 meV/atom
* B2 x = 0.5370 at 1000 K: +5.8 meV/atom
* B2 x = 0.5370 at 1500 K: +8.0 meV/atom
* B2 x = 0.4906 at 1000 K: +5.8 meV/atom
* B2 x = 0.4906 at 1500 K: +6.8 meV/atom
* B2 x = 0.4808 at 1000 K: +6.3 meV/atom
* B2 x = 0.4808 at 1500 K: +8.6 meV/atom
* L12 x = 0.7500 at 1000 K: +19.3 meV/atom
* L12 x = 0.7500 at 1500 K: +36.0 meV/atom
* L12 x = 0.7593 at 1000 K: +13.0 meV/atom
* L12 x = 0.7593 at 1500 K: +25.1 meV/atom
* L12 x = 0.7407 at 1000 K: +14.2 meV/atom
* L12 x = 0.7407 at 1500 K: +27.1 meV/atom
* B2 x = 0.5556 at 1000 K: +6.1 meV/atom
* B2 x = 0.5556 at 1500 K: +10.2 meV/atom
* B2 x = 0.5741 at 1000 K: +5.0 meV/atom
* B2 x = 0.5741 at 1500 K: +9.0 meV/atom
* B2 x = 0.5926 at 1000 K: +7.4 meV/atom
* B2 x = 0.5926 at 1500 K: +12.6 meV/atom
* B2 x = 0.6111 at 1000 K: +9.0 meV/atom
* B2 x = 0.6111 at 1500 K: +16.3 meV/atom
* B2 x = 0.4706 at 1000 K: +9.9 meV/atom
* B2 x = 0.4706 at 1500 K: +17.1 meV/atom
* L12 x = 0.7685 at 1000 K: +12.6 meV/atom
* L12 x = 0.7685 at 1500 K: +25.1 meV/atom
* L12 x = 0.7315 at 1000 K: +14.2 meV/atom
* L12 x = 0.7315 at 1500 K: +27.5 meV/atom
* L12 x = 0.7778 at 1000 K: +13.8 meV/atom
* L12 x = 0.7778 at 1500 K: +26.9 meV/atom
* L12 x = 0.7222 at 1000 K: +12.0 meV/atom
* L12 x = 0.7222 at 1500 K: +23.8 meV/atom

## Caveats

* This EAM puts NiAl3 and Ni2Al3 60-120 meV/atom above the 0 K hull (01_hull_0K.tsv), so the Al-rich intermetallics of the experimental diagram are absent; the B2 and L1_2 widths are the point of this example.
* Nothing below the lowest T_stop of the liquids is computed; T_stop(x) is listed in 02B_liquids.json.
* Table check: mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum) (intended).
