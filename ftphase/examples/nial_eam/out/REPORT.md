# Example 7: Ni-Al T-x diagram, Purja Pun & Mishin 2009 EAM (classical level, 0 GPa)

Assembled 2026-10-22 22:05:16 on mygarden5.  Files: out/07_phase_diagram.png, 07_two_phase_regions.tsv, 07_sensitivity.tsv, 05_free_energies.tsv, summary.json.

## Inputs

* potential: potentials/nial/Mishin-Ni-Al-2009.eam.alloy (NIST, Purja Pun & Mishin, Philos. Mag. 89, 3245 (2009)).
* solids: QHA of 64-atom SQS (fcc(Al) x = 0-0.03, fcc(Ni) x = 0.75-1), B2 54-atom cells with Ni anti-sites (Ni-rich) and Ni vacancies (Al-rich), L1_2 108-atom cells with anti-sites, Ni2Al3 and NiAl3 point phases; quantum QHA lowered to the classical level.
* liquids: calphy reversible scaling 2000 K -> T_stop(x), UFM, 3 iterations, 3 independent runs per composition averaged; compositions 0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00.
* configurational terms: ideal mixing (fcc), triple-defect sublattice model (B2: anti-sites + vacancies), two-sublattice anti-site model (L1_2).
* fits: liquid = ideal mixing + 4-term Redlich-Kister; fcc = polynomial excess over ideal mixing; B2, L1_2 = natural spline.

Temperature grid 950-2000 K (106 points); liquid runs per composition {0.0: 1, 0.1: 1, 0.2: 1, 0.3: 1, 0.4: 1, 0.5: 1, 0.6: 1, 0.7: 1, 0.8: 1, 0.9: 1, 1.0: 1}; sigma in the Monte Carlo (eV/atom) {'Ni2Al3': 0.002, 'fccAl': 0.002, 'B2': 0.002, 'NiAl3': 0.002, 'L12': 0.002, 'liquid': 0.0014}

## Key numbers (experiment: NiAl congruent 1911 K, B2 range ~0.45-0.60; Ni3Al peritectic 1668 K; eutectic L -> Ni3Al + (Ni) 1658 K x~0.76; Al-rich eutectic 913 K; Al 933.5 K; Ni 1728 K)

* B2 + liquid up to 1110.0 K; lowest temperature with liquid on the grid 950.0 K
* B2 composition range [x_Ni lower, upper] vs T: 1000 K [0.5, 0.5]; 1100 K [0.5, 0.5]
* segments whose boundary sits at a sampled composition limit (flag edge=True in 07_two_phase_regions.tsv; the true width may be larger): 62
* invariant reactions (pairs change between T_low and T_high):
  * 1110-1120 K: ['B2+L12', 'B2+liquid'] -> ['L12+liquid']
* two-phase regions at 900 K: none
* two-phase regions at 1200 K: liquid(0.300)-L12(0.750)
* two-phase regions at 1500 K: none
* two-phase regions at 1800 K: none

## Error bands (Monte Carlo, 30 samples)

* 950 K B2+L12: x_a = 0.500 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30)
* 950 K liquid+B2: x_a = 0.200 +/- 0.000, x_b = 0.500 +/- 0.000 (30/30)
* 1070 K B2+L12: x_a = 0.500 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30)
* 1070 K liquid+B2: x_a = 0.200 +/- 0.000, x_b = 0.500 +/- 0.000 (30/30)
* 1190 K liquid+L12: x_a = 0.300 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30)
* 1310 K liquid+L12: x_a = 0.400 +/- 0.000, x_b = 0.750 +/- 0.000 (30/30)

## Caveats

* This EAM puts NiAl3 and Ni2Al3 60-120 meV/atom above the 0 K hull (01_hull_0K.tsv), so the Al-rich intermetallics of the experimental diagram are absent; the B2 and L1_2 widths are the point of this example.
* Nothing below the lowest T_stop of the liquids is computed; T_stop(x) is listed in 02B_liquids.json.
* Table check: mixed quantum/classical treatment: ['classical', 'classical+harmonic-correction'] (see ftphase.quantum) (intended).
