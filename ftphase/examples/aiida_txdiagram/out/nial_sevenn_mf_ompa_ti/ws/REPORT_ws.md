# Example 7, stage 4: B2 / L1_2 with thermal point defects (Wagner-Schottky), re-assembled from the stage-3 table

Grid [950.0, 2000.0, 106]; scan 57 s.  Effective defect free energies (eV per defect, raw supercell differences) in defect_energies.tsv.

## Effective defect free energies

* B2 1000 K Va_on_B: +7.395 eV (formation-like, + g0: +1.642 eV) from 7 cells
* B2 1000 K B_on_A: -0.948 eV from 6 cells
* B2 1400 K Va_on_B: +7.611 eV (formation-like, + g0: +1.607 eV) from 7 cells
* B2 1400 K B_on_A: -1.043 eV from 6 cells
* B2 1800 K Va_on_B: +7.909 eV (formation-like, + g0: +1.616 eV) from 7 cells
* B2 1800 K B_on_A: -1.106 eV from 6 cells
* L12 1000 K A_on_B: +1.287 eV from 1 cells
* L12 1000 K B_on_A: -0.133 eV from 1 cells
* L12 1400 K A_on_B: +1.272 eV from 1 cells
* L12 1400 K B_on_A: -0.197 eV from 1 cells

## B2 composition range [x_Ni lower, upper]

* 1000 K: [0.48745077034071205, 0.5508146178093025]
* 1200 K: [0.4776164223910114, 0.6040435382190744]
* 1400 K: [0.42553191489362, 0.68518518518519]
* 1600 K: [0.4544647332411232, 0.68518518518519]
* 1800 K: [0.4788652519002146, 0.519736951906913]

## Invariant reactions

* 1060-1070 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+NiAl3', 'NiAl3+liquid'] -> ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid']
* 1380-1390 K: ['B2+L12', 'B2+Ni2Al3', 'L12+fccNi', 'Ni2Al3+liquid'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi']
* 1480-1490 K: ['B2+L12', 'B2+liquid', 'L12+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccNi+fccNi']
* 1520-1530 K: ['B2+L12', 'B2+liquid', 'L12+fccNi', 'fccNi+fccNi'] -> ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+fccNi', 'fccNi+liquid']
* 1540-1550 K: ['B2+L12', 'B2+liquid', 'L12+liquid', 'fccNi+fccNi', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+fccNi', 'fccNi+liquid']
* 1570-1580 K: ['B2+liquid', 'fccNi+fccNi', 'fccNi+liquid'] -> ['B2+liquid', 'fccNi+liquid']
* 1640-1650 K: ['B2+liquid', 'fccNi+liquid'] -> ['B2+liquid']

## Same-phase segments

* fccNi+fccNi x = 0.912-0.996 at 1490 K
* fccNi+fccNi x = 0.912-0.996 at 1500 K
* fccNi+fccNi x = 0.912-0.996 at 1510 K
* fccNi+fccNi x = 0.913-0.996 at 1520 K
* fccNi+fccNi x = 0.875-0.964 at 1530 K
* fccNi+fccNi x = 0.875-0.963 at 1540 K
* fccNi+fccNi x = 0.875-0.963 at 1550 K
* fccNi+fccNi x = 0.875-0.963 at 1560 K
* fccNi+fccNi x = 0.875-0.962 at 1570 K
* two-phase regions at 1200 K: liquid(0.206)-Ni2Al3(0.400); Ni2Al3(0.400)-B2(0.478); B2(0.604)-L12(0.719); L12(0.765)-fccNi(0.879)
* two-phase regions at 1500 K: liquid(0.314)-B2(0.438); B2(0.685)-L12(0.733); L12(0.754)-fccNi(0.850); fccNi(0.912)-fccNi(0.996)
* two-phase regions at 1800 K: liquid(0.405)-B2(0.479); B2(0.520)-liquid(0.583)
