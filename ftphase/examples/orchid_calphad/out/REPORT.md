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

### 参照評価 `AlLi-20Lon` の不変反応（300-1110 K）

| T (K) | phases (x ascending) | x |
|---|---|---|
| 876.1 | FCC_A1+LIQUID+BCC_4SL | 0.131, 0.238, 0.456 |
| 876.1 | FCC_4SL+LIQUID+BCC_4SL | 0.131, 0.238, 0.456 |
| 793.0 | BCC_4SL+AL2LI3+LIQUID | 0.567, 0.600, 0.745 |
| 609.0 | AL2LI3+ALLI2+LIQUID | 0.600, 0.652, 0.916 |
| 545.9 | ALLI2+AL4LI9+LIQUID | 0.658, 0.692, 0.966 |
| 452.3 | AL4LI9+LIQUID+BCC_4SL | 0.692, 0.993, 0.996 |
| 452.3 | AL4LI9+LIQUID+BCC_A2 | 0.692, 0.993, 0.996 |

評価間のばらつき（全評価の不変反応、同じ温度窓）:

| assessment | T (K) | phases |
|---|---|---|
| AlLi-07Hal-condensed | 876.1 | FCC_A1+LIQUID+BCC_4SL |
| AlLi-07Hal-condensed | 876.1 | FCC_4SL+LIQUID+BCC_4SL |
| AlLi-07Hal-condensed | 793.0 | BCC_4SL+AL2LI3+LIQUID |
| AlLi-07Hal-condensed | 609.6 | AL2LI3+AL4LI9+LIQUID |
| AlLi-07Hal-condensed | 452.3 | AL4LI9+LIQUID+BCC_4SL |
| AlLi-11Guo | 876.5 | FCC_A1+LIQUID+B32_BCC |
| AlLi-11Guo | 793.2 | B32_BCC+AL2LI3+LIQUID |
| AlLi-11Guo | 609.6 | AL2LI3+AL4LI9+LIQUID |
| AlLi-11Guo | 452.3 | AL4LI9+LIQUID+B32_BCC |
| AlLi-11Guo | 452.3 | AL4LI9+LIQUID+BCC_A2 |
| AlLi-20Lon | 876.1 | FCC_A1+LIQUID+BCC_4SL |
| AlLi-20Lon | 876.1 | FCC_4SL+LIQUID+BCC_4SL |
| AlLi-20Lon | 793.0 | BCC_4SL+AL2LI3+LIQUID |
| AlLi-20Lon | 609.0 | AL2LI3+ALLI2+LIQUID |
| AlLi-20Lon | 545.9 | ALLI2+AL4LI9+LIQUID |
| AlLi-20Lon | 452.3 | AL4LI9+LIQUID+BCC_4SL |
| AlLi-20Lon | 452.3 | AL4LI9+LIQUID+BCC_A2 |
| AlLi-23Cui-reg2 | 873.0 | FCC_A1+LIQUID+BCC_4SL |
| AlLi-23Cui-reg2 | 873.0 | FCC_4SL+LIQUID+BCC_4SL |
| AlLi-23Cui-reg2 | 793.0 | BCC_4SL+AL2LI3+LIQUID |
| AlLi-23Cui-reg2 | 610.1 | AL2LI3+ALLI2+LIQUID |
| AlLi-23Cui-reg2 | 541.4 | ALLI2+AL4LI9+LIQUID |
| AlLi-23Cui-reg2 | 454.5 | AL4LI9+BCC_4SL+LIQUID |
| AlLi-23Cui-reg2 | 454.5 | AL4LI9+BCC_A2+LIQUID |
| AlLi-23Cui-reg3 | 872.8 | FCC_A1+LIQUID+BCC_4SL |
| AlLi-23Cui-reg3 | 872.8 | FCC_4SL+LIQUID+BCC_4SL |
| AlLi-23Cui-reg3 | 793.7 | BCC_4SL+AL2LI3+LIQUID |
| AlLi-23Cui-reg3 | 608.6 | AL2LI3+ALLI2+LIQUID |
| AlLi-23Cui-reg3 | 543.2 | ALLI2+AL4LI9+LIQUID |
| AlLi-23Cui-reg3 | 454.9 | AL4LI9+BCC_4SL+LIQUID |
| AlLi-23Cui-reg3 | 454.9 | AL4LI9+BCC_A2+LIQUID |
| AlLi-24Liu | 868.8 | L12_FCC+LIQUID+ALLI_B32 |
| AlLi-24Liu | 793.6 | ALLI_B32+AL2LI3+LIQUID |
| AlLi-24Liu | 607.2 | AL2LI3+ALLI2+LIQUID |
| AlLi-24Liu | 542.8 | ALLI2+AL4LI9+LIQUID |
| AlLi-24Liu | 447.8 | AL4LI9+LIQUID+BCC_A2 |
| AlLi-89Sau-LB | 868.8 | FCC_A1+LIQUID+ALLI_B32 |
| AlLi-89Sau-LB | 793.6 | ALLI_B32+AL2LI3+LIQUID |
| AlLi-89Sau-LB | 607.6 | AL2LI3+AL4LI9+LIQUID |
| AlLi-89Sau-LB | 447.9 | AL4LI9+LIQUID+BCC_A2 |

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
| MACE-MPA-0 | 780.0-790.0 |  |
| MACE-MPA-0 | 820.0-830.0 |  |
| MatterSim-v1-5M | 720.0-730.0 |  |
| MatterSim-v1-5M | 990.0-1000.0 |  |
| NequIP-OAM-M | 800.0-810.0 |  |
| NequIP-OAM-M | 890.0-900.0 |  |
| NequIP-OAM-S | 840.0-850.0 |  |
| NequIP-OAM-S | 900.0-910.0 |  |
| NequIP-OAM-S | 920.0-930.0 |  |
| DPA4-Plus-OMat24 | 750.0-760.0 |  |
| DPA4-Plus-OMat24 | 810.0-820.0 |  |
