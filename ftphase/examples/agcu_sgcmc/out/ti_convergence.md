# calphy fe convergence, pure Ag (EAM Williams 2006) at 1275 K; coexistence MD bracket 1265-1290 K -> G_s - G_l should be ~ 0

| cell | switching | G_solid (eV/atom) | G_liquid (eV/atom) | G_s - G_l (meV/atom) | errors (meV) |
|---|---|---|---|---|---|
| 256 | 10k | -3.57346 | -3.56757 | -5.89 | 0.07 / 0.35 |
| 256 | 50k | ok | missing | | |
| 2048 | 10k | missing | missing | | |
| 2048 | 50k | missing | missing | | |

A positive G_s - G_l at 1275 K means the TI route makes the liquid too unstable (melting point too high).
The entropy of fusion of Ag is about 1.1 k_B, so 1 meV/atom corresponds to about 10 K.
