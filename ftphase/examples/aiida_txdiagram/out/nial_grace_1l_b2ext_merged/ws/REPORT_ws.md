# Example 7, stage 4: B2 / L1_2 with thermal point defects (Wagner-Schottky), re-assembled from the stage-3 table

Grid [950.0, 2000.0, 106]; scan 56 s.  Effective defect free energies (eV per defect, raw supercell differences) in defect_energies.tsv.

## Effective defect free energies

* B2 1000 K Va_on_B: +6.993 eV (formation-like, + g0: +1.406 eV) from 7 cells
* B2 1000 K B_on_A: -0.765 eV from 6 cells
* B2 1400 K Va_on_B: +7.238 eV (formation-like, + g0: +1.398 eV) from 7 cells
* B2 1400 K B_on_A: -0.822 eV from 6 cells
* L12 1000 K A_on_B: +1.064 eV from 1 cells
* L12 1000 K B_on_A: +0.152 eV from 1 cells
* L12 1400 K A_on_B: +1.086 eV from 1 cells
* L12 1400 K B_on_A: +0.043 eV from 1 cells

## B2 composition range [x_Ni lower, upper]

* 1000 K: [0.4628437992508228, 0.5754816784870017]
* 1200 K: [0.42553191489362, 0.6546759259259305]
* 1400 K: [0.42553191489362, 0.68518518518519]
* 1600 K: [0.4454126630794968, 0.5999992343767107]
* 1800 K: [0.5, 0.5]

## Invariant reactions

* 1110-1120 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid']
* 1250-1260 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
* 1570-1580 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+liquid', 'L12+liquid', 'fccNi+liquid']
* 1580-1590 K: ['B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
* 1710-1720 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid']

## Same-phase segments

* none
* two-phase regions at 1200 K: liquid(0.242)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.425); B2(0.655)-L12(0.719); L12(0.781)-fccNi(0.895)
* two-phase regions at 1500 K: liquid(0.320)-B2(0.425); B2(0.685)-L12(0.734); L12(0.780)-fccNi(0.860)
* two-phase regions at 1800 K: liquid(0.470)-B2(0.500); B2(0.500)-liquid(0.530)
