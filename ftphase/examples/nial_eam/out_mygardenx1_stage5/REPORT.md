# Example 7: Ni-Al T-x diagram, Purja Pun & Mishin 2009 EAM (classical level, 0 GPa)

Assembled 2026-10-23 20:41:26 on mygardenx1.  Files: out/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.

## Inputs

* potential: potentials/nial/Mishin-Ni-Al-2009.eam.alloy (NIST, Purja Pun & Mishin, Philos. Mag. 89, 3245 (2009)).
* solids: QHA of 64-atom SQS (fcc(Al) x = 0-0.03, fcc(Ni) x = 0.75-1), B2 54-atom cells with Ni anti-sites (Ni-rich) and Ni vacancies (Al-rich), L1_2 108-atom cells with anti-sites, Ni2Al3 and NiAl3 point phases; quantum QHA lowered to the classical level.
* liquids: calphy reversible scaling 2000 K -> T_stop(x), UFM, 3 iterations, 3 independent runs per composition averaged; compositions 0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00.
* configurational terms: ideal mixing (fcc), triple-defect sublattice model (B2: anti-sites + vacancies), two-sublattice anti-site model (L1_2).
* fits: liquid = ideal mixing + 4-term Redlich-Kister; fcc = polynomial excess over ideal mixing; B2, L1_2 = analytic sublattice entropy + linear defect energy per branch (anti-site / vacancy side).

Temperature grid 950-2000 K (106 points); liquid runs per composition {0.0: 3, 0.1016: 3, 0.1992: 3, 0.3008: 3, 0.3984: 3, 0.5: 3, 0.6016: 3, 0.6992: 3, 0.8008: 3, 0.8984: 3, 1.0: 3}; sigma in the Monte Carlo (eV/atom) {'L12': 0.002, 'B2': 0.002, 'fccNi': 0.002, 'Ni2Al3': 0.002, 'NiAl3': 0.002, 'fccAl': 0.002, 'liquid': 0.0014}

## Key numbers (experiment: NiAl congruent 1911 K, B2 range ~0.45-0.60; Ni3Al peritectic 1668 K; eutectic L -> Ni3Al + (Ni) 1658 K x~0.76; Al-rich eutectic 913 K; Al 933.5 K; Ni 1728 K)

* B2 + liquid up to 1820.0 K; lowest temperature with liquid on the grid 950.0 K
* B2 composition range [x_Ni lower, upper] vs T: 1000 K [0.6111111111111112, 0.5000444444444445]; 1100 K [0.6111111111111112, 0.49992955681079554]; 1200 K [0.6111111111111112, 0.5000444444444445]; 1300 K [0.6111111111111112, 0.5000444444444445]; 1400 K [0.6111111111111112, 0.5001200051160983]; 1500 K [0.6111111111111112, 0.5001199990467914]; 1600 K [0.6111111111111112, 0.49893574381359923]; 1700 K [0.6111111111111112, 0.4990217472677138]; 1800 K [0.5518495200013727, 0.5028608165497225]
* segments whose boundary sits at a sampled composition limit (flag edge=True in 07_two_phase_regions.tsv; the true width may be larger): 170
* invariant reactions (pairs change between T_low and T_high):
  * 1030-1040 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
  * 1640-1650 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+liquid', 'L12+liquid', 'fccNi+liquid']
  * 1690-1700 K: ['B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'L12+liquid']
  * 1790-1800 K: ['B2+liquid', 'L12+liquid'] -> ['B2+liquid']
* two-phase regions at 900 K: none
* two-phase regions at 1200 K: liquid(0.219)-B2(0.500); B2(0.611)-L12(0.769); L12(0.778)-fccNi(0.909)
* two-phase regions at 1500 K: liquid(0.352)-B2(0.500); B2(0.611)-L12(0.778); L12(0.778)-fccNi(0.892)
* two-phase regions at 1800 K: liquid(0.460)-B2(0.503); B2(0.552)-liquid(0.571)

## Error bands (Monte Carlo, 30 samples)

* 950 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.758 +/- 0.001 (30/30)
* 950 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.923 +/- 0.003 (30/30)
* 950 K fccAl+B2: x_a = 0.029 +/- 0.000, x_b = 0.500 +/- 0.000 (1/30)
* 950 K fccAl+liquid: x_a = 0.020 +/- 0.004, x_b = 0.097 +/- 0.019 (29/30)
* 950 K liquid+B2: x_a = 0.154 +/- 0.006, x_b = 0.500 +/- 0.000 (29/30)
* 1070 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.763 +/- 0.001 (30/30)
* 1070 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.917 +/- 0.003 (30/30)
* 1070 K fccAl+liquid: x_a = 0.006 +/- 0.003, x_b = 0.019 +/- 0.012 (5/30)
* 1070 K liquid+B2: x_a = 0.191 +/- 0.006, x_b = 0.500 +/- 0.000 (30/30)
* 1190 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.768 +/- 0.001 (30/30)
* 1190 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.911 +/- 0.003 (30/30)
* 1190 K liquid+B2: x_a = 0.218 +/- 0.005, x_b = 0.500 +/- 0.000 (30/30)
* 1310 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.773 +/- 0.001 (30/30)
* 1310 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.904 +/- 0.003 (30/30)
* 1310 K liquid+B2: x_a = 0.259 +/- 0.016, x_b = 0.500 +/- 0.000 (30/30)
* 1430 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 1430 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.897 +/- 0.003 (30/30)
* 1430 K liquid+B2: x_a = 0.294 +/- 0.011, x_b = 0.500 +/- 0.000 (30/30)
* 1550 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.778 +/- 0.000 (30/30)
* 1550 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.890 +/- 0.003 (30/30)
* 1550 K liquid+B2: x_a = 0.335 +/- 0.006, x_b = 0.499 +/- 0.000 (30/30)
* 1670 K B2+L12: x_a = 0.611 +/- 0.000, x_b = 0.778 +/- 0.000 (2/30)
* 1670 K B2+liquid: x_a = 0.611 +/- 0.000, x_b = 0.686 +/- 0.006 (28/30)
* 1670 K L12+fccNi: x_a = 0.778 +/- 0.000, x_b = 0.878 +/- 0.000 (1/30)
* 1670 K L12+liquid: x_a = 0.778 +/- 0.000, x_b = 0.856 +/- 0.006 (29/30)
* 1670 K liquid+B2: x_a = 0.382 +/- 0.007, x_b = 0.499 +/- 0.000 (30/30)
* 1670 K liquid+L12: x_a = 0.701 +/- 0.005, x_b = 0.778 +/- 0.000 (28/30)
* 1670 K liquid+fccNi: x_a = 0.898 +/- 0.031, x_b = 0.911 +/- 0.027 (27/30)
* 1790 K B2+liquid: x_a = 0.582 +/- 0.035, x_b = 0.606 +/- 0.041 (30/30)
* 1790 K L12+liquid: x_a = 0.778 +/- 0.000, x_b = 0.808 +/- 0.011 (24/30)
* 1790 K liquid+B2: x_a = 0.452 +/- 0.015, x_b = 0.500 +/- 0.002 (30/30)
* 1790 K liquid+L12: x_a = 0.748 +/- 0.011, x_b = 0.778 +/- 0.000 (24/30)

## QHA (classical level) minus calphy solid TI, per cell (anharmonic error of the quasi-harmonic route; mesh converged)

* fccAl x = 0.0000 at 1000 K: +13.2 meV/atom
* fccAl x = 0.0156 at 1000 K: +2.2 meV/atom
* fccAl x = 0.0312 at 1000 K: +0.2 meV/atom
* fccNi x = 1.0000 at 1000 K: +17.9 meV/atom
* fccNi x = 1.0000 at 1500 K: +36.3 meV/atom
* fccNi x = 0.9375 at 1000 K: +7.3 meV/atom
* fccNi x = 0.9375 at 1500 K: +18.1 meV/atom
* fccNi x = 0.8750 at 1000 K: +7.5 meV/atom
* fccNi x = 0.8750 at 1500 K: +18.7 meV/atom
* fccNi x = 0.8125 at 1000 K: +8.0 meV/atom
* fccNi x = 0.8125 at 1500 K: +19.8 meV/atom
* B2 x = 0.5000 at 1000 K: +4.5 meV/atom
* B2 x = 0.5000 at 1500 K: +8.7 meV/atom
* B2 x = 0.5185 at 1000 K: -1.0 meV/atom
* B2 x = 0.5185 at 1500 K: -2.4 meV/atom
* B2 x = 0.5370 at 1000 K: +0.1 meV/atom
* B2 x = 0.5370 at 1500 K: -0.7 meV/atom
* B2 x = 0.4906 at 1000 K: +0.5 meV/atom
* B2 x = 0.4906 at 1500 K: -0.7 meV/atom
* B2 x = 0.4808 at 1000 K: +1.2 meV/atom
* B2 x = 0.4808 at 1500 K: +1.9 meV/atom
* L12 x = 0.7500 at 1000 K: +14.0 meV/atom
* L12 x = 0.7500 at 1500 K: +28.7 meV/atom
* L12 x = 0.7593 at 1000 K: +7.5 meV/atom
* L12 x = 0.7593 at 1500 K: +17.6 meV/atom
* L12 x = 0.7407 at 1000 K: +7.9 meV/atom
* L12 x = 0.7407 at 1500 K: +18.0 meV/atom
* B2 x = 0.5556 at 1000 K: +0.4 meV/atom
* B2 x = 0.5556 at 1500 K: +2.0 meV/atom
* B2 x = 0.5741 at 1000 K: +0.2 meV/atom
* B2 x = 0.5741 at 1500 K: +1.5 meV/atom
* B2 x = 0.5926 at 1000 K: +2.2 meV/atom
* B2 x = 0.5926 at 1500 K: +6.0 meV/atom
* B2 x = 0.6111 at 1000 K: +2.3 meV/atom
* B2 x = 0.6111 at 1500 K: +6.3 meV/atom
* L12 x = 0.7685 at 1000 K: +7.2 meV/atom
* L12 x = 0.7685 at 1500 K: +17.2 meV/atom
* L12 x = 0.7315 at 1000 K: +7.3 meV/atom
* L12 x = 0.7315 at 1500 K: +17.2 meV/atom
* L12 x = 0.7778 at 1000 K: +7.3 meV/atom
* L12 x = 0.7778 at 1500 K: +17.4 meV/atom
* L12 x = 0.7222 at 1000 K: +6.9 meV/atom
* L12 x = 0.7222 at 1500 K: +16.8 meV/atom

## Caveats

* This EAM puts NiAl3 and Ni2Al3 60-120 meV/atom above the 0 K hull (01_hull_0K.tsv), so the Al-rich intermetallics of the experimental diagram are absent; the B2 and L1_2 widths are the point of this example.
* Nothing below the lowest T_stop of the liquids is computed; T_stop(x) is listed in 02B_liquids.json.
* Table check: mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum) (intended).
