# Example 7, stage 4: B2 / L1_2 with thermal point defects (Wagner-Schottky), re-assembled from the stage-3 table

Grid [950.0, 2000.0, 106]; scan 101 s.  Effective defect free energies (eV per defect, raw supercell differences) in defect_energies.tsv.

## Effective defect free energies

* B2 1000 K Va_on_B: +7.538 eV (formation-like, + g0: +1.774 eV) from 3 cells
* B2 1000 K B_on_A: -1.129 eV from 4 cells
* B2 1400 K Va_on_B: +7.672 eV (formation-like, + g0: +1.659 eV) from 3 cells
* B2 1400 K B_on_A: -1.234 eV from 4 cells
* L12 1000 K A_on_B: +1.469 eV from 1 cells
* L12 1000 K B_on_A: -0.202 eV from 1 cells
* L12 1400 K A_on_B: +1.509 eV from 1 cells
* L12 1400 K B_on_A: -0.223 eV from 1 cells

## B2 composition range [x_Ni lower, upper]

* 1000 K: [0.4899981829742106, 0.61111111111111]
* 1200 K: [0.4944771241830083, 0.61111111111111]
* 1400 K: [0.48592508962855074, 0.61111111111111]
* 1600 K: [0.49285463988502143, 0.554177000880695]
* 1800 K: [nan, nan]

## Invariant reactions

* 1030-1040 K: ['B2+L12', 'B2+NiAl3', 'L12+fccNi', 'NiAl3+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
* 1400-1410 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+liquid', 'L12+fccNi', 'L12+liquid']
* 1440-1450 K: ['B2+liquid', 'L12+fccNi', 'L12+liquid'] -> ['B2+liquid', 'L12+liquid', 'fccNi+liquid']
* 1450-1460 K: ['B2+liquid', 'L12+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
* 1480-1490 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+fccNi', 'fccNi+liquid']
* 1590-1600 K: ['B2+liquid', 'fccNi+fccNi', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
* 1650-1660 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid']

## Same-phase segments

* fccNi+fccNi x = 0.908-0.999 at 1490 K
* fccNi+fccNi x = 0.908-0.999 at 1500 K
* fccNi+fccNi x = 0.908-0.998 at 1510 K
* fccNi+fccNi x = 0.909-0.998 at 1520 K
* fccNi+fccNi x = 0.909-0.998 at 1530 K
* fccNi+fccNi x = 0.909-0.998 at 1540 K
* fccNi+fccNi x = 0.909-0.998 at 1550 K
* fccNi+fccNi x = 0.909-0.998 at 1560 K
* fccNi+fccNi x = 0.910-0.998 at 1570 K
* fccNi+fccNi x = 0.910-0.998 at 1580 K
* fccNi+fccNi x = 0.910-0.998 at 1590 K
* two-phase regions at 1200 K: liquid(0.301)-B2(0.494); B2(0.611)-L12(0.745); L12(0.781)-fccNi(0.868)
* two-phase regions at 1500 K: liquid(0.387)-B2(0.489); B2(0.611)-liquid(0.665); liquid(0.780)-fccNi(0.850); fccNi(0.908)-fccNi(0.999)
* two-phase regions at 1800 K: 
