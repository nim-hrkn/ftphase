# TDB of ACE Al-Li from the free-energy table (compounds: cef)

## Loss against the table (rms of the fits, meV/atom)

* fcc -> FCC_A1: RK order 3, rms 0.46 over x = 0.000-1.000
* bcc -> BCC_A2: RK order 1, rms 11.53 over x = 0.750-1.000; pure ['AL'] not computed: kept above the hull of the table + 20 meV/atom outside the sampled range
* liquid -> LIQUID: RK order 3, rms 0.34 over x = 0.000-1.000
* Al3Li -> AL3LI: dH_f -9.46 kJ/mol, dS_f -3.97 J/mol/K (vs fcc Al, bcc Li), rms 0.07
* B32 -> B32: dH_f -18.20 kJ/mol, dS_f -5.78 J/mol/K (vs fcc Al, bcc Li), rms 0.15
* Al2Li3 -> AL2LI3: dH_f -18.23 kJ/mol, dS_f -6.49 J/mol/K (vs fcc Al, bcc Li), rms 0.07
* Al4Li9 -> AL4LI9: dH_f -15.91 kJ/mol, dS_f -6.33 J/mol/K (vs fcc Al, bcc Li), rms 0.03

## pycalphad on the TDB against the hull of the table (two-phase boundaries, x_Li)

| T (K) | two-phase region | hull (table) | pycalphad (TDB) |
|---|---|---|---|
| 700 | Al2Li3+B32 | 0.530–0.608 | 0.57–0.61 |
| 700 | Al2Li3+liquid | 0.630–0.743 | 0.65–0.74 |
| 700 | B32+fcc | 0.027–0.494 | 0.07–0.49 |
| 800 | B32+liquid | 0.530–0.630 | 0.37–0.64 |
| 800 | fcc+liquid | 0.055–0.251 | 0.09–0.25 |
| 900 | fcc+liquid | 0.000–0.003 | — |
