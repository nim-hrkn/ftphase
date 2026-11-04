# 経路 1: ORCHID-Diagrams（SGTE binary collection, Hallstedt 2025）の CALPHAD 相図と MLIP の比較

データ: `/home/kino/kino/Claude/Projects/PhaseDiagram/data/orchid-v2026.10/phase-diagrams/orchid-phase-diagrams-v2026.10/phase-diagrams/sgte` (ORCHID-Diagrams 10.5281/zenodo.23735859, pycalphad 0.11.2 で計算された境界; TDB 本体は非同梱)。
各系の全評価を `sgte_<sys>.png` に、参照評価の境界を MLIP の T-x 図に重ねたものを `overlay_<sys>.png` に描いた。

## Al-Li

ORCHID-Diagrams の評価 8 件（計算成功 7）。参照評価: `AlLi-20Lon`。

| assessment | status | phases | n_inv | source |
|---|---|---|---|---|
| AlLi-07Hal-condensed | ok | A1_FCC, A2_BCC, AL2LI3, AL4LI9, BCC_4SL, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, LIQUID | 12 | B. Hallstedt, O. Kim, Int. J. Mater. Res., 98, 961-69(2007) |
| AlLi-07Hal | failed |  | 0 | ValueError: COMP_SETS does not match ['DISORDERED_PART', 'MAGNETIC', 'NEVER_DISO |
| AlLi-11Guo | ok | A2_BCC, AL2LI3, AL4LI9, B32_BCC, BCC_A2, FCC_A1, HCP_A3, LIQUID | 8 | C. Guo, Y. Liang, C. Li, Z. Du, Calphad, 35, 54-65(2011). |
| AlLi-20Lon | ok | A1_FCC, A2_BCC, AL2LI3, AL4LI9, ALLI2, BCC_4SL, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, LIQUID | 10 | Z. Long, D. Cui, H. Hu, Z. Li, F. Yin, T. Fan, J. Phase Equilib. Diffus., 41, 623-41(2020). |
| AlLi-23Cui-reg2 | ok | A1_FCC, A2_BCC, AL2LI3, AL4LI9, ALLI2, BCC_4SL, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, LIQUID | 12 | S. Cui, H. Ma, J. Wang, B. Hu, Calphad, 82, 102585(2023). |
| AlLi-23Cui-reg3 | ok | A1_FCC, A2_BCC, AL2LI3, AL4LI9, ALLI2, BCC_4SL, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, LIQUID | 12 | S. Cui, H. Ma, J. Wang, B. Hu, Calphad, 82, 102585(2023). |
| AlLi-24Liu | ok | A1_FCC, AL2LI3, AL4LI9, ALLI2, ALLI_B32, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, L12_FCC, LIQUID | 10 | Y. Liu, S. Liu, Y. Du, Calphad, 87, 102752(2024). |
| AlLi-89Sau-LB | ok | AL2LI3, AL4LI9, ALLI_B32, BCC_A2, FCC_A1, HCP_A3, LIQUID | 7 | N. Saunders, Z. Metallkd., 80, 894-903 (1989) |

図: `sgte_alli.png`, `overlay_alli.png`

### 参照評価 `AlLi-20Lon` の不変反応（650-1110 K）

| T (K) | phases (x ascending) | x |
|---|---|---|
| 876.1 | FCC_A1+LIQUID+BCC_4SL | 0.131, 0.238, 0.456 |
| 876.1 | FCC_4SL+LIQUID+BCC_4SL | 0.131, 0.238, 0.456 |
| 793.0 | BCC_4SL+AL2LI3+LIQUID | 0.567, 0.600, 0.745 |

評価間のばらつき（全評価の不変反応、同じ温度窓）:

| assessment | T (K) | phases |
|---|---|---|
| AlLi-07Hal-condensed | 876.1 | FCC_A1+LIQUID+BCC_4SL |
| AlLi-07Hal-condensed | 876.1 | FCC_4SL+LIQUID+BCC_4SL |
| AlLi-07Hal-condensed | 793.0 | BCC_4SL+AL2LI3+LIQUID |
| AlLi-11Guo | 876.5 | FCC_A1+LIQUID+B32_BCC |
| AlLi-11Guo | 793.2 | B32_BCC+AL2LI3+LIQUID |
| AlLi-20Lon | 876.1 | FCC_A1+LIQUID+BCC_4SL |
| AlLi-20Lon | 876.1 | FCC_4SL+LIQUID+BCC_4SL |
| AlLi-20Lon | 793.0 | BCC_4SL+AL2LI3+LIQUID |
| AlLi-23Cui-reg2 | 873.0 | FCC_A1+LIQUID+BCC_4SL |
| AlLi-23Cui-reg2 | 873.0 | FCC_4SL+LIQUID+BCC_4SL |
| AlLi-23Cui-reg2 | 793.0 | BCC_4SL+AL2LI3+LIQUID |
| AlLi-23Cui-reg3 | 872.8 | FCC_A1+LIQUID+BCC_4SL |
| AlLi-23Cui-reg3 | 872.8 | FCC_4SL+LIQUID+BCC_4SL |
| AlLi-23Cui-reg3 | 793.7 | BCC_4SL+AL2LI3+LIQUID |
| AlLi-24Liu | 868.8 | L12_FCC+LIQUID+ALLI_B32 |
| AlLi-24Liu | 793.6 | ALLI_B32+AL2LI3+LIQUID |
| AlLi-89Sau-LB | 868.8 | FCC_A1+LIQUID+ALLI_B32 |
| AlLi-89Sau-LB | 793.6 | ALLI_B32+AL2LI3+LIQUID |

### MLIP/EAM run の不変反応（07_invariants.tsv、同相区間の出入りを除く）

| run | T bracket (K) | changed pairs |
|---|---|---|
| ACE (aiida, x<=0.5) | 760.0-770.0 |  |
| ACE (aiida, x<=0.5) | 790.0-800.0 |  |
| ACE (aiida, x<=0.5) | 850.0-860.0 |  |
| ACE full range (example 6) | 670.0-680.0 |  |
| ACE full range (example 6) | 710.0-720.0 |  |
| ACE full range (example 6) | 750.0-760.0 |  |
| ACE full range (example 6) | 760.0-770.0 |  |
| ACE full range (example 6) | 840.0-850.0 |  |
| ACE full range (example 6) | 850.0-860.0 |  |
| ACE full range (example 6) | 890.0-900.0 |  |
| GRACE-FS-OAM | 740.0-750.0 |  |
| GRACE-FS-OAM | 800.0-810.0 |  |
| GRACE-1L-OMAT | 720.0-730.0 |  |
| GRACE-1L-OMAT | 810.0-820.0 |  |
| GRACE-2L-OMAT | 750.0-760.0 |  |
| GRACE-2L-OMAT | 810.0-820.0 |  |
| SevenNet-0 | 930.0-940.0 |  |
| SevenNet-0 | 1000.0-1010.0 |  |
| SevenNet-MF-ompa | 850.0-860.0 |  |
| SevenNet-MF-ompa | 910.0-920.0 |  |
| MACE-MPA-0 | 770.0-780.0 |  |
| MACE-MPA-0 | 820.0-830.0 |  |
| NequIP-OAM-M | 800.0-810.0 |  |
| NequIP-OAM-M | 890.0-900.0 |  |

## Ni-Al (x = x_Ni)

ORCHID-Diagrams の評価 13 件（計算成功 13）。参照評価: `AlNi-01Dup-4sl`。

| assessment | status | phases | n_inv | source |
|---|---|---|---|---|
| AlNi-01Dup-4sl-old | ok | A1_FCC, A2_BCC, AL3NI2_D513, AL3NI5, AL3NI_D011, AL4NI3, B2_BCC, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, LIQUID | 20 | N. Dupin, I. Ansara, B. Sundman, Calphad, 25, 279-98(2001). |
| AlNi-01Dup-4sl | ok | A1_FCC, A2_BCC, AL3NI2_D513, AL3NI5, AL3NI_D011, AL4NI3, B2_BCC, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, LIQUID | 17 | N. Dupin, I. Ansara, B. Sundman, Calphad, 25, 279-98(2001). |
| AlNi-01Dup-LB | ok | A1_FCC, A2_BCC, AL3NI2_D513, AL3NI5, AL3NI_D011, AL4NI3, B2_BCC, BCC_A2, FCC_A1, HCP_A3, L12_FCC, LIQUID | 10 | N. Dupin, I. Ansara, B. Sundman, Calphad, 25, 279-98(2001). |
| AlNi-01Dup-orig | ok | A1_FCC, A2_BCC, AL3NI2_D513, AL3NI5, AL3NI_D011, B2_BCC, BCC_A2, FCC_A1, HCP_A3, L12_FCC, LIQUID | 8 | N. Dupin, I. Ansara, B. Sundman, Calphad, 25, 279-98(2001). |
| AlNi-03Sun | ok | A1_FCC, A2_BCC, AL3NI2_D513, AL3NI5, AL3NI_D011, B2_BCC, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, LIQUID | 15 | B. Sundman, N. Dupin, JEEP 2003 Lyon. |
| AlNi-04Oht | ok | AL3NI2_D513, AL3NI5, AL3NI_D011, B2_BCC, BCC_A2, FCC_A1, HCP_A3, L12_FCC, LIQUID | 8 | H. Ohtani, Y. Chen, M. Hasebe, Mater. Trans. (JIM), 45, 1489-98(2004). |
| AlNi-05Mie | ok | AL3NI2_D513, AL3NI5, AL3NI_D011, ALNI3_L12, BCC_A2, FCC_A1, HCP_A3, LIQUID | 13 | J. Miettinen, Calphad, 29, 40-48(2005). |
| AlNi-11Che | ok | A1_FCC, AL3NI2_D513, AL3NI5, AL3NI_D011, B2_BCC, BCC_A2, FCC_A1, HCP_A3, L12_FCC, LIQUID | 11 | H.-L. Chen, E. Doernberg, P. Svoboda, R. Schmid-Fetzer, Thermochim. Acta, 512, 189-95(2011). |
| AlNi-14Zhu | ok | A1_FCC, AL3NI2_D513, AL3NI5, AL3NI_D011, B2_BCC, BCC_A2, FCC_A1, HCP_A3, L12_FCC, LIQUID | 8 | J. Zhu, M.S. Titus, T.M. Pollock, J. Phase Equilib. Diffus., 35, 595-611(2014). |
| AlNi-22Yan | ok | A1_FCC, A2_BCC, AL3NI2_D513, AL3NI5, AL3NI_D011, AL4NI3, B2_BCC, BCC_A2, FCC_4SL, FCC_A1, HCP_A3, LIQUID | 15 | W. Yang, P. Wang, X. Huang, S. Zhang, Intermetallics, 149, 107647(2022). |
| AlNi-88Ans | ok | AL3NI2_D513, AL3NI_D011, B2_BCC, HCP_A3, L12_FCC, LIQUID | 8 | I. Ansara, B. Sundman, P. Willemin, Acta Metall., 36, 977-82(1988). |
| AlNi-97Ans | ok | A1_FCC, AL3NI2_D513, AL3NI5, AL3NI_D011, B2_BCC, BCC_A2, FCC_A1, HCP_A3, L12_FCC, LIQUID | 9 | I. Ansara, N. Dupin, H.L. Lukas, B. Sundman, J. Alloys Compd., 247, 20-30(1997). |
| AlNi-98Hua | ok | A1_FCC, AL3NI2_D513, AL3NI5, AL3NI_D011, B2_BCC, BCC_A2, FCC_A1, HCP_A3, L12_FCC, LIQUID | 9 | W. Huang, Y.A. Chang, Intermet., 6, 487-98(1998). |

図: `sgte_nial.png`, `overlay_nial.png`

### 参照評価 `AlNi-01Dup-4sl` の不変反応（900-2010 K）

| T (K) | phases (x ascending) | x |
|---|---|---|
| 1642.7 | LIQUID+FCC_4SL+FCC_4SL | 0.755, 0.760, 0.787 |
| 1642.7 | LIQUID+FCC_4SL+FCC_A1 | 0.755, 0.760, 0.787 |
| 1641.8 | B2_BCC+LIQUID+FCC_4SL | 0.710, 0.747, 0.752 |
| 1638.2 | B2_BCC+LIQUID+FCC_4SL | 0.714, 0.751, 0.784 |
| 1638.2 | B2_BCC+LIQUID+FCC_A1 | 0.714, 0.751, 0.784 |
| 1400.7 | LIQUID+AL3NI2_D513+B2_BCC | 0.255, 0.400, 0.410 |
| 1123.5 | LIQUID+AL3NI_D011+AL3NI2_D513 | 0.172, 0.250, 0.359 |
| 975.2 | AL3NI2_D513+AL4NI3+B2_BCC | 0.407, 0.429, 0.460 |
| 969.7 | B2_BCC+AL3NI5+FCC_4SL | 0.590, 0.625, 0.726 |
| 914.8 | FCC_4SL+LIQUID+AL3NI_D011 | 0.002, 0.029, 0.250 |

評価間のばらつき（全評価の不変反応、同じ温度窓）:

| assessment | T (K) | phases |
|---|---|---|
| AlNi-01Dup-4sl-old | 1642.7 | LIQUID+FCC_4SL+FCC_4SL |
| AlNi-01Dup-4sl-old | 1642.7 | LIQUID+FCC_4SL+FCC_A1 |
| AlNi-01Dup-4sl-old | 1641.8 | B2_BCC+LIQUID+FCC_4SL |
| AlNi-01Dup-4sl-old | 1638.2 | B2_BCC+LIQUID+FCC_4SL |
| AlNi-01Dup-4sl-old | 1638.2 | B2_BCC+LIQUID+FCC_A1 |
| AlNi-01Dup-4sl-old | 1400.7 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-01Dup-4sl-old | 1123.5 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-01Dup-4sl-old | 975.2 | AL3NI2_D513+AL4NI3+B2_BCC |
| AlNi-01Dup-4sl-old | 914.8 | FCC_4SL+LIQUID+AL3NI_D011 |
| AlNi-01Dup-4sl-old | 914.8 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-01Dup-4sl-old | 914.0 | B2_BCC+AL3NI5+FCC_4SL |
| AlNi-01Dup-4sl | 1642.7 | LIQUID+FCC_4SL+FCC_4SL |
| AlNi-01Dup-4sl | 1642.7 | LIQUID+FCC_4SL+FCC_A1 |
| AlNi-01Dup-4sl | 1641.8 | B2_BCC+LIQUID+FCC_4SL |
| AlNi-01Dup-4sl | 1638.2 | B2_BCC+LIQUID+FCC_4SL |
| AlNi-01Dup-4sl | 1638.2 | B2_BCC+LIQUID+FCC_A1 |
| AlNi-01Dup-4sl | 1400.7 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-01Dup-4sl | 1123.5 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-01Dup-4sl | 975.2 | AL3NI2_D513+AL4NI3+B2_BCC |
| AlNi-01Dup-4sl | 969.7 | B2_BCC+AL3NI5+FCC_4SL |
| AlNi-01Dup-4sl | 914.8 | FCC_4SL+LIQUID+AL3NI_D011 |
| AlNi-01Dup-LB | 1642.7 | LIQUID+L12_FCC+FCC_A1 |
| AlNi-01Dup-LB | 1641.8 | B2_BCC+LIQUID+L12_FCC |
| AlNi-01Dup-LB | 1400.7 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-01Dup-LB | 1123.5 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-01Dup-LB | 975.2 | AL3NI2_D513+AL4NI3+B2_BCC |
| AlNi-01Dup-LB | 914.8 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-01Dup-LB | 914.0 | B2_BCC+AL3NI5+L12_FCC |
| AlNi-01Dup-orig | 1642.7 | LIQUID+L12_FCC+FCC_A1 |
| AlNi-01Dup-orig | 1641.8 | B2_BCC+LIQUID+L12_FCC |
| AlNi-01Dup-orig | 1400.7 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-01Dup-orig | 1123.5 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-01Dup-orig | 914.8 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-01Dup-orig | 914.0 | B2_BCC+AL3NI5+L12_FCC |
| AlNi-03Sun | 1642.7 | LIQUID+FCC_4SL+FCC_4SL |
| AlNi-03Sun | 1642.7 | LIQUID+FCC_4SL+FCC_A1 |
| AlNi-03Sun | 1638.5 | B2_BCC+LIQUID+FCC_4SL |
| AlNi-03Sun | 1563.5 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-03Sun | 1123.5 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-03Sun | 931.7 | B2_BCC+AL3NI5+FCC_4SL |
| AlNi-03Sun | 914.8 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-03Sun | 914.8 | FCC_4SL+LIQUID+AL3NI_D011 |
| AlNi-04Oht | 1616.8 | B2_BCC+LIQUID+FCC_A1 |
| AlNi-04Oht | 1580.2 | B2_BCC+L12_FCC+FCC_A1 |
| AlNi-04Oht | 1462.4 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-04Oht | 1110.1 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-04Oht | 1024.9 | B2_BCC+AL3NI5+L12_FCC |
| AlNi-04Oht | 918.6 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-05Mie | 1643.1 | LIQUID+ALNI3_L12+FCC_A1 |
| AlNi-05Mie | 1637.8 | BCC_A2+LIQUID+ALNI3_L12 |
| AlNi-05Mie | 1407.1 | LIQUID+AL3NI2_D513+BCC_A2 |
| AlNi-05Mie | 1124.8 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-05Mie | 972.5 | BCC_A2+AL3NI5+ALNI3_L12 |
| AlNi-05Mie | 914.8 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-11Che | 1642.8 | LIQUID+L12_FCC+FCC_A1 |
| AlNi-11Che | 1642.5 | B2_BCC+LIQUID+L12_FCC |
| AlNi-11Che | 1407.3 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-11Che | 1134.8 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-11Che | 973.0 | B2_BCC+AL3NI5+L12_FCC |
| AlNi-11Che | 915.1 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-11Che | 915.1 | L12_FCC+LIQUID+AL3NI_D011 |
| AlNi-14Zhu | 1643.1 | LIQUID+L12_FCC+FCC_A1 |
| AlNi-14Zhu | 1642.3 | B2_BCC+LIQUID+L12_FCC |
| AlNi-14Zhu | 1412.2 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-14Zhu | 1127.0 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-14Zhu | 973.4 | B2_BCC+AL3NI5+L12_FCC |
| AlNi-14Zhu | 924.4 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-22Yan | 1647.3 | LIQUID+FCC_4SL+FCC_4SL |
| AlNi-22Yan | 1647.3 | LIQUID+FCC_4SL+FCC_A1 |
| AlNi-22Yan | 1645.6 | B2_BCC+LIQUID+FCC_4SL |
| AlNi-22Yan | 1642.0 | B2_BCC+LIQUID+FCC_4SL |
| AlNi-22Yan | 1407.9 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-22Yan | 1137.0 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-22Yan | 972.5 | B2_BCC+AL3NI5+FCC_4SL |
| AlNi-22Yan | 971.8 | AL3NI2_D513+AL4NI3+B2_BCC |
| AlNi-22Yan | 916.5 | FCC_4SL+LIQUID+AL3NI_D011 |
| AlNi-88Ans | 1662.2 | B2_BCC+L12_FCC+LIQUID |
| AlNi-88Ans | 1657.8 | L12_FCC+LIQUID+L12_FCC |
| AlNi-88Ans | 1434.8 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-88Ans | 1126.7 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-88Ans | 908.3 | L12_FCC+LIQUID+AL3NI_D011 |
| AlNi-97Ans | 1643.4 | LIQUID+L12_FCC+FCC_A1 |
| AlNi-97Ans | 1642.2 | B2_BCC+LIQUID+L12_FCC |
| AlNi-97Ans | 1410.4 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-97Ans | 1123.5 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-97Ans | 972.5 | B2_BCC+AL3NI5+L12_FCC |
| AlNi-97Ans | 914.8 | FCC_A1+LIQUID+AL3NI_D011 |
| AlNi-97Ans | 914.8 | L12_FCC+LIQUID+AL3NI_D011 |
| AlNi-98Hua | 1644.7 | LIQUID+L12_FCC+FCC_A1 |
| AlNi-98Hua | 1642.3 | B2_BCC+LIQUID+L12_FCC |
| AlNi-98Hua | 1417.0 | LIQUID+AL3NI2_D513+B2_BCC |
| AlNi-98Hua | 1123.5 | LIQUID+AL3NI_D011+AL3NI2_D513 |
| AlNi-98Hua | 995.4 | B2_BCC+AL3NI5+L12_FCC |
| AlNi-98Hua | 919.2 | FCC_A1+LIQUID+AL3NI_D011 |

### MLIP/EAM run の不変反応（07_invariants.tsv、同相区間の出入りを除く）

| run | T bracket (K) | changed pairs |
|---|---|---|
| EAM Mishin 2009 (stage 5, solid TI) | 1030.0-1040.0 |  |
| EAM Mishin 2009 (stage 5, solid TI) | 1640.0-1650.0 |  |
| EAM Mishin 2009 (stage 5, solid TI) | 1690.0-1700.0 |  |
| EAM Mishin 2009 (stage 5, solid TI) | 1790.0-1800.0 |  |
| GRACE-FS-OAM (QHA solids) | 1040.0-1050.0 |  |
| GRACE-FS-OAM (QHA solids) | 1090.0-1100.0 |  |
| GRACE-FS-OAM (QHA solids) | 1180.0-1190.0 |  |
| GRACE-FS-OAM (QHA solids) | 1290.0-1300.0 |  |
| GRACE-FS-OAM (QHA solids) | 1530.0-1540.0 |  |
| GRACE-FS-OAM (QHA solids) | 1670.0-1680.0 |  |
| GRACE-FS-OAM (QHA solids) | 1730.0-1740.0 |  |
| GRACE-FS-OAM (QHA solids) | 1800.0-1810.0 |  |
| GRACE-FS-OAM (+TI ends) | 1040.0-1050.0 |  |
| GRACE-FS-OAM (+TI ends) | 1090.0-1100.0 |  |
| GRACE-FS-OAM (+TI ends) | 1180.0-1190.0 |  |
| GRACE-FS-OAM (+TI ends) | 1280.0-1290.0 |  |
| GRACE-FS-OAM (+TI ends) | 1290.0-1300.0 |  |
| GRACE-FS-OAM (+TI ends) | 1580.0-1590.0 |  |
| GRACE-FS-OAM (+TI ends) | 1650.0-1660.0 |  |
| GRACE-FS-OAM (+TI ends) | 1680.0-1690.0 |  |
| GRACE-FS-OAM (+TI ends) | 1720.0-1730.0 |  |
| GRACE-FS-OAM (+TI ends) | 1790.0-1800.0 |  |
| GRACE-FS-OAM (+TI ends) | 1800.0-1810.0 |  |
| GRACE-FS-OAM (+TI ends) | 1810.0-1820.0 |  |
| GRACE-FS-OAM (+TI ends) | 1850.0-1860.0 |  |
| GRACE-1L-OMAT (QHA solids) | 1040.0-1050.0 |  |
| GRACE-1L-OMAT (QHA solids) | 1090.0-1100.0 |  |
| GRACE-1L-OMAT (QHA solids) | 1630.0-1640.0 |  |
| GRACE-1L-OMAT (QHA solids) | 1660.0-1670.0 |  |
| GRACE-1L-OMAT (QHA solids) | 1690.0-1700.0 |  |
| GRACE-1L-OMAT (QHA solids) | 1730.0-1740.0 |  |
| GRACE-1L-OMAT (QHA solids) | 1760.0-1770.0 |  |
| GRACE-1L-OMAT (+TI ends) | 1040.0-1050.0 |  |
| GRACE-1L-OMAT (+TI ends) | 1090.0-1100.0 |  |
| GRACE-1L-OMAT (+TI ends) | 1640.0-1650.0 |  |
| GRACE-1L-OMAT (+TI ends) | 1660.0-1670.0 |  |
| GRACE-1L-OMAT (+TI ends) | 1700.0-1710.0 |  |
| GRACE-1L-OMAT (+TI ends) | 1760.0-1770.0 |  |
| GRACE-1L-OMAT (+TI ends) | 1940.0-1950.0 |  |
| SevenNet-0 (QHA solids) | 1240.0-1250.0 |  |
| SevenNet-0 (QHA solids) | 1250.0-1260.0 |  |
| SevenNet-0 (QHA solids) | 1350.0-1360.0 |  |
| SevenNet-0 (QHA solids) | 1440.0-1450.0 |  |
| SevenNet-0 (QHA solids) | 1450.0-1460.0 |  |
| SevenNet-0 (QHA solids) | 1490.0-1500.0 |  |
| SevenNet-0 (QHA solids) | 1680.0-1690.0 |  |
| SevenNet-0 (+TI ends) | 1130.0-1140.0 |  |
| SevenNet-0 (+TI ends) | 1240.0-1250.0 |  |
| SevenNet-0 (+TI ends) | 1250.0-1260.0 |  |
| SevenNet-0 (+TI ends) | 1270.0-1280.0 |  |
| SevenNet-0 (+TI ends) | 1440.0-1450.0 |  |
| SevenNet-0 (+TI ends) | 1470.0-1480.0 |  |
| SevenNet-0 (+TI ends) | 1490.0-1500.0 |  |

## Ag-Cu

ORCHID-Diagrams の評価 6 件（計算成功 6）。参照評価: `AgCu-04Wit-LB`。

| assessment | status | phases | n_inv | source |
|---|---|---|---|---|
| AgCu-00Moo | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 1 | K.-W. Moon, W.J. Boettinger, U.R. Kattner, F.S. Biancaniello, C.A. Handwerker, J. Electron. Mater., 29, 1122-36(2000). |
| AgCu-04Wit-LB | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 1 | V.T. Witusiewicz, U. Hecht, S.G. Fries, S. Rex, J. Alloys Compd. 385, 133-43(2004). |
| AgCu-06He | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 1 | X.C. He, H. Wang, H.S. Liu, Z.P. Jin, Calphad, 30, 367-74(2006). |
| AgCu-86Hay | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 1 | F.H. Hayes, H.L. Lukas, G. Effenberg, G. Petzow, Z. Metallkd., 77, 749-54(1986). |
| AgCu-88Joe | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 1 | B. Joensson, J. Agren, J. Less-Common Met., 145, 153-66(1988). |
| AgCu-98Luk | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 1 | H.L. Lukas, unpublished, 1998. |

図: `sgte_agcu.png`, `overlay_agcu.png`

### 参照評価 `AgCu-04Wit-LB` の不変反応（1000-1410 K）

| T (K) | phases (x ascending) | x |
|---|---|---|
| 1053.4 | FCC_A1+LIQUID+FCC_A1 | 0.121, 0.398, 0.953 |

評価間のばらつき（全評価の不変反応、同じ温度窓）:

| assessment | T (K) | phases |
|---|---|---|
| AgCu-00Moo | 1052.3 | FCC_A1+LIQUID+FCC_A1 |
| AgCu-04Wit-LB | 1053.4 | FCC_A1+LIQUID+FCC_A1 |
| AgCu-06He | 1055.8 | FCC_A1+LIQUID+FCC_A1 |
| AgCu-86Hay | 1056.0 | FCC_A1+LIQUID+FCC_A1 |
| AgCu-88Joe | 1053.7 | FCC_A1+LIQUID+FCC_A1 |
| AgCu-98Luk | 1053.0 | FCC_A1+LIQUID+FCC_A1 |

### MLIP/EAM run の不変反応（07_invariants.tsv、同相区間の出入りを除く）

| run | T bracket (K) | changed pairs |
|---|---|---|
| EAM WMH 2006 (2048-atom solid TI) | 1140.0-1150.0 |  |
| EAM WMH 2006 (2048-atom solid TI) | 1150.0-1160.0 |  |
| EAM WMH 2006 (2048-atom solid TI) | 1190.0-1200.0 |  |
| EAM WMH 2006 (256-atom TI) | 1170.0-1180.0 |  |
| GRACE-FS-OAM (QHA) | 1110.0-1120.0 |  |
| GRACE-FS-OAM (QHA) | 1310.0-1320.0 |  |
| GRACE-FS-OAM (+TI ends) | 1100.0-1110.0 |  |
| GRACE-FS-OAM (+TI ends) | 1220.0-1230.0 |  |
| GRACE-FS-OAM (+TI ends) | 1240.0-1250.0 |  |
| GRACE-FS-OAM (+TI ends) | 1250.0-1260.0 |  |
| GRACE-FS-OAM (+TI ends) | 1290.0-1300.0 |  |
| GRACE-FS-OAM (+TI ends) | 1300.0-1310.0 |  |
| GRACE-1L-OMAT (+TI ends) | 1110.0-1120.0 |  |
| SevenNet-0 (QHA) | 1240.0-1250.0 |  |
| SevenNet-0 (+TI ends) | 1130.0-1140.0 |  |
| SevenNet-0 (+TI ends) | 1140.0-1150.0 |  |
| SevenNet-0 (+TI ends) | 1150.0-1160.0 |  |
