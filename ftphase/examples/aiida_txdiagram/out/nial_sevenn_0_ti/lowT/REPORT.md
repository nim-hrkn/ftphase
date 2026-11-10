# nial_sevenn_0_ti: solids-only re-assembly 100-890 K

* phases ['B2', 'L12', 'Ni2Al3', 'NiAl3', 'fccAl', 'fccNi']; fits {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'}; entropy models {'B2': ['b2_triple_defect', 0.5], 'L12': ['b32_antisite@0.75', 0.75]}; liquid rows dropped
* 444 two-phase rows, 80 same-phase (fit-noise) rows

## Invariant reactions

* 570-580 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+fccAl'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3']
* 870-880 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3'] -> ['B2+B2', 'B2+L12', 'L12+fccNi']
* two-phase regions at 300 K: fccAl(0.000)-NiAl3(0.250); NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.471); B2(0.513)-L12(0.719); L12(0.774)-fccNi(0.950)
* two-phase regions at 400 K: fccAl(0.000)-NiAl3(0.250); NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.471); B2(0.525)-L12(0.719); L12(0.781)-fccNi(0.946)
* two-phase regions at 500 K: fccAl(0.000)-NiAl3(0.250); NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.471); B2(0.534)-L12(0.747); L12(0.781)-fccNi(0.943)
* two-phase regions at 600 K: NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.471); B2(0.539)-L12(0.750); L12(0.781)-fccNi(0.941)
* two-phase regions at 700 K: NiAl3(0.250)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.471); B2(0.542)-L12(0.750); L12(0.781)-fccNi(0.938)
