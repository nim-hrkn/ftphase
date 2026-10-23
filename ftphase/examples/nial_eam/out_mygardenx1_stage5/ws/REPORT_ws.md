# Example 7, stage 4: B2 / L1_2 with thermal point defects (Wagner-Schottky), re-assembled from the stage-3 table

Grid [950.0, 2000.0, 106]; scan 117 s.  Effective defect free energies (eV per defect, raw supercell differences) in defect_energies.tsv.

## Effective defect free energies

* B2 1000 K Va_on_B: +6.477 eV (formation-like, + g0: +1.665 eV) from 4 cells
* B2 1000 K B_on_A: -0.546 eV from 6 cells
* B2 1400 K Va_on_B: +6.698 eV (formation-like, + g0: +1.638 eV) from 4 cells
* B2 1400 K B_on_A: -0.581 eV from 6 cells
* B2 1800 K Va_on_B: +6.939 eV (formation-like, + g0: +1.597 eV) from 4 cells
* B2 1800 K B_on_A: -0.618 eV from 6 cells
* L12 1000 K A_on_B: +0.734 eV from 3 cells
* L12 1000 K B_on_A: +0.470 eV from 3 cells
* L12 1400 K A_on_B: +0.733 eV from 3 cells
* L12 1400 K B_on_A: +0.428 eV from 3 cells
* L12 1800 K A_on_B: +0.719 eV from 3 cells
* L12 1800 K B_on_A: +0.383 eV from 3 cells

## B2 composition range [x_Ni lower, upper]

* 1000 K: [0.4996487231899079, 0.6111111111111112]
* 1200 K: [0.499312510755738, 0.6111111111111112]
* 1400 K: [0.4989932934839695, 0.6111111111111112]
* 1600 K: [0.49891895417022064, 0.6111111111111112]
* 1800 K: [0.5029454124756909, 0.5497105127415918]

## Invariant reactions

* 1030-1040 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccAl+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
* 1560-1570 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+liquid']
* 1570-1580 K: ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'L12+liquid', 'fccNi+liquid']
* 1590-1600 K: ['B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
* 1690-1700 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid']

## Same-phase segments

* none
* two-phase regions at 1200 K: liquid(0.222)-B2(0.499); B2(0.611)-L12(0.740); L12(0.778)-fccNi(0.886)
* two-phase regions at 1500 K: liquid(0.320)-B2(0.499); B2(0.611)-L12(0.735); L12(0.778)-fccNi(0.862)
* two-phase regions at 1800 K: liquid(0.466)-B2(0.503); B2(0.550)-liquid(0.566)
