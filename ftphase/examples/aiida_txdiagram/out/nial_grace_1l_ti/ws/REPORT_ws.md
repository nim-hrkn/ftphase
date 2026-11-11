# Example 7, stage 4: B2 / L1_2 with thermal point defects (Wagner-Schottky), re-assembled from the stage-3 table

Grid [950.0, 2000.0, 106]; scan 86 s.  Effective defect free energies (eV per defect, raw supercell differences) in defect_energies.tsv.

## Effective defect free energies

* B2 1000 K Va_on_B: +7.006 eV (formation-like, + g0: +1.418 eV) from 3 cells
* B2 1000 K B_on_A: -0.896 eV from 4 cells
* B2 1400 K Va_on_B: +7.276 eV (formation-like, + g0: +1.437 eV) from 3 cells
* B2 1400 K B_on_A: -0.933 eV from 4 cells
* L12 1000 K A_on_B: +1.064 eV from 1 cells
* L12 1000 K B_on_A: +0.152 eV from 1 cells
* L12 1400 K A_on_B: +1.086 eV from 1 cells
* L12 1400 K B_on_A: +0.043 eV from 1 cells

## B2 composition range [x_Ni lower, upper]

* 1000 K: [0.47058823529412, 0.61111111111111]
* 1200 K: [0.47058823529412, 0.61111111111111]
* 1400 K: [0.47058823529412, 0.61111111111111]
* 1600 K: [0.47058823529412, 0.61111111111111]
* 1800 K: [0.5, 0.5]

## Invariant reactions

* 1110-1120 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid']
* 1370-1380 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
* 1550-1560 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+liquid', 'L12+fccNi', 'L12+liquid']
* 1570-1580 K: ['B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+liquid', 'L12+liquid', 'fccNi+liquid']
* 1580-1590 K: ['B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
* 1710-1720 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid']

## Same-phase segments

* none
* two-phase regions at 1200 K: liquid(0.242)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.471); B2(0.611)-L12(0.726); L12(0.781)-fccNi(0.895)
* two-phase regions at 1500 K: liquid(0.338)-B2(0.471); B2(0.611)-L12(0.719); L12(0.780)-fccNi(0.860)
* two-phase regions at 1800 K: liquid(0.470)-B2(0.500); B2(0.500)-liquid(0.530)
