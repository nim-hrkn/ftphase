# B2 NiAl point defects: MLIPs vs EAM vs DFT (eV; 4x4x4 = 128 sites, positions relaxed at the MLIP lattice parameter)

raw = E(defect cell) - E(perfect cell); formation vs pure elements adds/removes the atom at its pure-fcc energy; triple defect = 2 Va_Ni + Ni_Al + 2 E_B2 (composition conserving, per formula unit removed); Schottky = Va_Ni + Va_Al + 2 E_B2.

| MLIP | a0 (A) | E_f B2 (eV/atom) | raw Va_Ni | raw Va_Al | raw Ni_Al | raw Al_Ni | Va_Ni form. | Va_Al form. | Ni_Al form. | Al_Ni form. | triple defect | Schottky pair | antisite pair |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| grace-fs | 2.886 | -0.674 | +6.99 | +5.87 | -1.26 | +3.61 | +1.24 | +2.15 | +0.77 | +1.58 | +1.90 | +2.04 | +2.35 |
| mace-mpa-0 | 2.885 | -0.659 | +6.86 | +6.10 | -1.17 | +3.89 | +1.08 | +2.36 | +0.87 | +1.84 | +1.71 | +2.12 | +2.72 |
| mattersim-5m | 2.887 | -0.666 | +6.76 | +6.05 | -1.18 | +3.68 | +0.99 | +2.31 | +0.86 | +1.64 | +1.50 | +1.97 | +2.49 |
| sevenn-0 | 2.886 | -0.670 | +6.54 | +5.39 | -1.41 | +3.29 | +0.77 | +1.67 | +0.64 | +1.24 | +0.84 | +1.10 | +1.88 |
| sevenn-mf-ompa | 2.890 | -0.661 | +6.81 | +6.35 | -0.85 | +3.49 | +1.03 | +2.61 | +1.18 | +1.45 | +1.92 | +2.32 | +2.64 |
| EAM Mishin 2009 (vacancy_analysis.md) | 2.832 | — | — | — | — | — | 1.76 (Va_Ni, formation-like) | — | — | — | 2.82 | — | — |
| DFT (literature, vacancy_analysis.md) | 2.89 | -0.70 (expt -0.61) | — | — | — | — | 0.9-1.3 | — | — | — | 1.0-1.3 | — | — |

Reading: the Al-rich width of B2 is carried by Ni vacancies (triple defect 2 Va_Ni + Ni_Al per missing formula unit); an MLIP whose triple-defect energy is near the DFT 1.0-1.3 eV can give the experimental x_Ni ~ 0.45 at 1600 K, the EAM's 2.8 eV cannot (vacancy_analysis.md).
