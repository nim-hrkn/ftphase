# nial_grace_1l_ti: solids-only re-assembly 100-890 K

* phases ['B2', 'L12', 'NiAl3', 'fccAl', 'fccNi']; fits {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'}; entropy models {'B2': ['b2_triple_defect', 0.5], 'L12': ['b32_antisite@0.75', 0.75]}; liquid rows dropped
* 366 two-phase rows, 80 same-phase (fit-noise) rows

## Invariant reactions

* 570-580 K: ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+fccAl'] -> ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi']
* 870-880 K: ['B2+B2', 'B2+L12', 'B2+NiAl3', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'L12+fccNi']
* two-phase regions at 300 K: fccAl(0.000)-NiAl3(0.250); NiAl3(0.250)-B2(0.471); B2(0.556)-L12(0.750); L12(0.764)-fccNi(1.000)
* two-phase regions at 400 K: fccAl(0.000)-NiAl3(0.250); NiAl3(0.250)-B2(0.471); B2(0.579)-L12(0.750); L12(0.780)-fccNi(1.000)
* two-phase regions at 500 K: fccAl(0.000)-NiAl3(0.250); NiAl3(0.250)-B2(0.471); B2(0.555)-L12(0.750); L12(0.781)-fccNi(1.000)
* two-phase regions at 600 K: NiAl3(0.250)-B2(0.471); B2(0.611)-L12(0.750); L12(0.781)-fccNi(0.999)
* two-phase regions at 700 K: NiAl3(0.250)-B2(0.471); B2(0.611)-L12(0.751); L12(0.781)-fccNi(0.999)
