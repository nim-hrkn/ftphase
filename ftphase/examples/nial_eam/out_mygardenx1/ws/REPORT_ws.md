# Example 7, stage 4: B2 / L1_2 with thermal point defects (Wagner-Schottky), re-assembled from the stage-3 table

Grid [950.0, 2000.0, 106]; scan 64 s.  Effective defect free energies (eV per defect, raw supercell differences) in defect_energies.tsv.

## Effective defect free energies

* B2 1000 K Va_on_B: +6.496 eV (formation-like, + g0: +1.678 eV) from 4 cells
* B2 1000 K B_on_A: -0.551 eV from 6 cells
* B2 1400 K Va_on_B: +6.706 eV (formation-like, + g0: +1.639 eV) from 4 cells
* B2 1400 K B_on_A: -0.592 eV from 6 cells
* B2 1800 K Va_on_B: +6.943 eV (formation-like, + g0: +1.592 eV) from 4 cells
* B2 1800 K B_on_A: -0.631 eV from 6 cells
* L12 1000 K A_on_B: +0.706 eV from 3 cells
* L12 1000 K B_on_A: +0.439 eV from 3 cells
* L12 1400 K A_on_B: +0.683 eV from 3 cells
* L12 1400 K B_on_A: +0.371 eV from 3 cells

## B2 composition range [x_Ni lower, upper]

* 1000 K: [0.49965963588851636, 0.6111111111111112]
* 1200 K: [0.4993119969141953, 0.6111111111111112]
* 1400 K: [0.49888103318724303, 0.6111111111111112]
* 1600 K: [0.4986155615890334, 0.6111111111111112]
* 1800 K: [0.5002815419105573, 0.6111111111111112]

## Invariant reactions

* 950-960 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
* 1630-1640 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+liquid']
* 1640-1650 K: ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'L12+liquid', 'fccNi+liquid']
* 1670-1680 K: ['B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
* 1740-1750 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid']

## Same-phase segments

* none
* two-phase regions at 1200 K: liquid(0.208)-B2(0.499); B2(0.611)-L12(0.737); L12(0.778)-fccNi(0.895)
* two-phase regions at 1500 K: liquid(0.304)-B2(0.499); B2(0.611)-L12(0.727); L12(0.778)-fccNi(0.876)
* two-phase regions at 1800 K: liquid(0.424)-B2(0.500); B2(0.611)-liquid(0.672)
