# B2 NiAl triple defect (2 Va_Ni + Ni_Al) with the three point defects next to each other (2026-11-17)

`nial_triple_bound.py`: 4x4x4 B2 cell (128 sites), Ni_Al on an Al site and two Ni vacancies on two of its 8 nearest Ni sites; positions relaxed at fixed cell.
E_bind = [2 raw(Va_Ni) + raw(Ni_Al)] - [E(cell with the complex) - E(perfect)] (> 0: bound). 'far apart' = the three defects as far from each other as the cell allows (should be 0; its value shows the finite-cell error).

| MLIP | triple defect, isolated (eV) | E_bind <100> (Va-Va = a) | E_bind <110> (a sqrt2) | E_bind <111> (a sqrt3) | far apart (check) | triple defect, most stable bound (eV) |
|---|---|---|---|---|---|---|
| grace-1l | 1.40 | -0.156 | +0.016 | +0.060 | +0.015 | 1.34 |
| grace-fs | 1.90 | +0.042 | +0.154 | +0.160 | -0.003 | 1.74 |
| mace-mpa-0 | 1.71 | +0.020 | +0.143 | +0.141 | +0.030 | 1.57 |
| mattersim-5m | 1.50 | -0.073 | +0.054 | +0.110 | -0.009 | 1.39 |
| sevenn-0 | 0.84 | +0.029 | +0.090 | +0.122 | -0.003 | 0.72 |
| sevenn-mf-ompa | 1.92 | -0.009 | +0.126 | +0.172 | +0.057 | 1.75 |

Reading: the most stable arrangement is the two vacancies on opposite corners (<111>) of the cube around the anti-site, bound by 0.06-0.17 eV; vacancies on a cube edge (<100>, nearest Ni-Ni distance) are not bound or repel. The check cells give 0.00-0.06 eV, so the numbers carry about +-0.05 eV.
Consequence for the Wagner-Schottky treatment: at 1400 K (k_B T = 0.121 eV) a binding of 0.15 eV raises the weight of a bound arrangement by exp(0.15 / k_B T) = 3.5; with 4 <111> and 12 <110> arrangements per anti-site and vacancy fractions of 1e-3..1e-2 on the Ni sublattice the bound fraction is of order (number of arrangements) x c_Va x exp(E_bind / k_B T) ~ 0.05-0.5 per vacancy pair, i.e. most triple defects are dissociated at the temperatures of the B2 field and the non-interacting model is adequate; binding matters below ~800 K and for the multi-vacancy cells (already sampled explicitly in the B2-width runs).
