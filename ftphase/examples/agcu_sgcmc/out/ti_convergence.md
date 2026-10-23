# calphy fe convergence, pure Ag (EAM Williams 2006) at 1275 K; coexistence MD bracket 1265-1290 K -> G_s - G_l should be ~ 0

| cell | switching | G_solid (eV/atom) | G_liquid (eV/atom) | G_s - G_l (meV/atom) | errors (meV) |
|---|---|---|---|---|---|
| 256 | 10k | -3.57346 | -3.56757 | -5.89 | 0.07 / 0.35 |
| 256 | 50k | -3.57157 | -3.56693 | -4.64 | 0.58 / 0.18 |
| 2048 | 10k | -3.56592 | -3.56723 | +1.31 | 0.43 / 0.14 |
| 2048 | 50k | -3.56675 | -3.56723 | +0.48 | 0.23 / 0.14 |

A positive G_s - G_l at 1275 K means the TI route makes the liquid too unstable (melting point too high).
The entropy of fusion of Ag is about 1.1 k_B, so 1 meV/atom corresponds to about 10 K.
