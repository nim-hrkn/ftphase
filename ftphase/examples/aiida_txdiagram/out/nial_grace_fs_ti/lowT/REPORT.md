# nial_grace_fs_ti: solids-only re-assembly 100-890 K

* phases ['B2', 'L12', 'Ni2Al3', 'NiAl3', 'fccAl', 'fccNi']; fits {'fccAl': 'poly', 'fccNi': 'poly', 'liquid': 'rk', 'B2': 'poly', 'L12': 'poly'}; entropy models {'B2': ['b2_triple_defect', 0.5], 'L12': ['b32_antisite@0.75', 0.75]}; liquid rows dropped
* 283 two-phase rows, 7 same-phase (fit-noise) rows

## Invariant reactions

* 470-480 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+fccAl'] -> ['B2+L12', 'B2+NiAl3', 'L12+fccNi']
* 820-830 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi']
* 870-880 K: ['B2+B2', 'B2+L12', 'B2+Ni2Al3', 'L12+fccNi'] -> ['B2+B2', 'B2+L12', 'L12+fccNi']
* two-phase regions at 300 K: fccAl(0.000)-NiAl3(0.250); NiAl3(0.250)-B2(0.500); B2(0.529)-L12(0.750); L12(0.781)-fccNi(0.968)
* two-phase regions at 400 K: fccAl(0.000)-NiAl3(0.250); NiAl3(0.250)-B2(0.499); B2(0.611)-L12(0.750); L12(0.781)-fccNi(0.954)
* two-phase regions at 500 K: NiAl3(0.250)-B2(0.497); B2(0.611)-L12(0.750); L12(0.781)-fccNi(0.944)
* two-phase regions at 600 K: NiAl3(0.250)-B2(0.496); B2(0.611)-L12(0.750); L12(0.781)-fccNi(0.937)
* two-phase regions at 700 K: NiAl3(0.250)-B2(0.494); B2(0.611)-L12(0.751); L12(0.781)-fccNi(0.931)
