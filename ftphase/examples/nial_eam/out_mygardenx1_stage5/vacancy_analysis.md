# B2 NiAl point defects with the Purja Pun-Mishin 2009 EAM, and what the Al-rich width needs

B2 lattice parameter 2.8321 A; E(B2) = -4.5109, E(fcc Al) = -3.3600, E(fcc Ni) = -4.4500 eV/atom; 128-site cell

## Raw supercell energy differences (defect cell minus perfect cell, relaxed positions)

* Va_Ni (Ni vacancy): +6.210 eV
* Va_Al (Al vacancy): +5.394 eV
* Ni_Al (Ni anti-site on Al sublattice): -0.578 eV
* Al_Ni (Al anti-site on Ni sublattice): +2.671 eV

## Formation energies referenced to the pure elements (mu_Ni = E(fcc Ni), mu_Al = E(fcc Al))

* Va_Ni: +1.760 eV
* Va_Al: +2.034 eV
* Ni_Al: +0.512 eV
* Al_Ni: +1.581 eV

## Composition-conserving defect complexes (eV)

* triple defect 2 Va_Ni + Ni_Al: +2.820
* anti-site pair Ni_Al + Al_Ni: +2.093
* Schottky pair Va_Ni + Va_Al: +2.582

DFT (Korzhavyi et al. 2000; Fu & Painter 1997, as collected by Mishin et al. 2002): triple defect ~1.0-1.3 eV, anti-site pair ~1.4-1.6 eV, Schottky pair ~2.7-3.0 eV; constitutional defects: Ni anti-sites on the Ni-rich side, Ni vacancies on the Al-rich side.

## Sensitivity of the Al-rich B2 boundary to the Ni-vacancy free energy (thermal-defect model on the stage-5 cells)

| T (K) | shift of e(Va_Ni) (eV) | e(Va_Ni) formation-like (eV) | B2 lower boundary x_Ni (common tangent with the liquid) |
|---|---|---|---|
| 1000 | -0.6 | 1.07 | - (no liquid rows at this T) |
| 1000 | -0.4 | 1.27 | - (no liquid rows at this T) |
| 1000 | -0.2 | 1.47 | - (no liquid rows at this T) |
| 1000 | +0.0 | 1.67 | - (no liquid rows at this T) |
| 1000 | +0.2 | 1.87 | - (no liquid rows at this T) |
| 1400 | -0.6 | 1.04 | 0.400 |
| 1400 | -0.4 | 1.24 | 0.468 |
| 1400 | -0.2 | 1.44 | 0.495 |
| 1400 | +0.0 | 1.64 | 0.499 |
| 1400 | +0.2 | 1.84 | 0.500 |
| 1800 | -0.6 | 1.00 | 0.400 |
| 1800 | -0.4 | 1.20 | 0.490 |
| 1800 | -0.2 | 1.40 | 0.500 |
| 1800 | +0.0 | 1.60 | 0.500 |
| 1800 | +0.2 | 1.80 | 0.500 |

Experiment: B2 reaches x_Ni ~ 0.45 at 1600 K on the Al-rich side (y_Va ~ 0.18 on the Ni sublattice). With the EAM value (shift 0) the boundary stays at 0.50;
a Ni-vacancy free energy lower by 0.4-0.5 eV (i.e. a formation energy of ~1.1-1.2 eV, the DFT range) reproduces the experimental width.
The EAM triple-defect energy (2.8 eV vs DFT 1.0-1.3 eV) is the reason: the Al-rich B2 width is a property of this potential, not of the workflow.
