# Example 7, stage 4: B2 / L1_2 with thermal point defects (Wagner-Schottky), re-assembled from the stage-3 table

Grid [950.0, 2000.0, 106]; scan 125 s.  Effective defect free energies (eV per defect, raw supercell differences) in defect_energies.tsv.

## Effective defect free energies

* B2 1000 K Va_on_B: +7.782 eV (formation-like, + g0: +1.980 eV) from 3 cells
* B2 1000 K B_on_A: -0.869 eV from 4 cells
* B2 1400 K Va_on_B: +7.400 eV (formation-like, + g0: +1.373 eV) from 3 cells
* B2 1400 K B_on_A: -1.076 eV from 4 cells
* B2 1800 K Va_on_B: +7.727 eV (formation-like, + g0: +1.410 eV) from 3 cells
* B2 1800 K B_on_A: -1.096 eV from 4 cells
* L12 1000 K A_on_B: +1.363 eV from 1 cells
* L12 1000 K B_on_A: +0.133 eV from 1 cells
* L12 1400 K A_on_B: +1.312 eV from 1 cells
* L12 1400 K B_on_A: -0.138 eV from 1 cells

## B2 composition range [x_Ni lower, upper]

* 1000 K: [0.49911270524516904, 0.5533454534193853]
* 1200 K: [0.49971992936323506, 0.61111111111111]
* 1400 K: [0.47058823529412, 0.61111111111111]
* 1600 K: [0.47058823529412, 0.61111111111111]
* 1800 K: [0.47058823529412, 0.5937182947758748]

## Invariant reactions

* 970-980 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid']
* 1010-1020 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid']
* 1090-1100 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
* 1310-1320 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccNi+fccNi']
* 1350-1360 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccNi+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
* 1460-1470 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+liquid']
* 1490-1500 K: ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+liquid']
* 1530-1540 K: ['B2+L12', 'B2+liquid', 'L12+liquid'] -> ['B2+liquid']

## Same-phase segments

* fccNi+fccNi x = 0.938-0.993 at 1320 K
* fccNi+fccNi x = 0.938-0.993 at 1330 K
* fccNi+fccNi x = 0.939-0.993 at 1340 K
* fccNi+fccNi x = 0.939-0.992 at 1350 K
* two-phase regions at 1200 K: liquid(0.263)-B2(0.500); B2(0.611)-L12(0.741); L12(0.762)-fccNi(0.879)
* two-phase regions at 1500 K: liquid(0.320)-B2(0.471); B2(0.611)-L12(0.722); L12(0.754)-liquid(0.792)
* two-phase regions at 1800 K: liquid(0.367)-B2(0.471); B2(0.594)-liquid(0.631)
