# 経路 1: ORCHID-Diagrams（SGTE binary collection, Hallstedt 2025）の CALPHAD 相図と MLIP の比較

データ: `/home/kino/kino/Claude/Projects/PhaseDiagram/data/orchid-v2026.10/phase-diagrams/orchid-phase-diagrams-v2026.10/phase-diagrams/sgte` (ORCHID-Diagrams 10.5281/zenodo.23735859, pycalphad 0.11.2 で計算された境界; TDB 本体は非同梱)。
各系の全評価を `sgte_<sys>.png` に、参照評価の境界を MLIP の T-x 図に重ねたものを `overlay_<sys>.png` に描いた。

## Pt-Rh (x = x_Rh)

ORCHID-Diagrams の評価 3 件（計算成功 3）。参照評価: `PtRh-98Jac`。

| assessment | status | phases | n_inv | source |
|---|---|---|---|---|
| PtRh-02Mam | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 0 | M.N. Mamontov, Russ. J. Phys. Chem., 76, 20-23(2002). |
| PtRh-98Jac | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 0 | K.T. Jacob, S. Priya, Y. Waseda, Metall. Mater. Trans. A, 29, 1545-50(1998). |
| PtRh-98Spe-LB | ok | BCC_A2, FCC_A1, HCP_A3, LIQUID | 0 | P.J. Spencer, unpublished work, 1998. |

図: `sgte_ptrh.png`, `overlay_ptrh.png`

### 参照評価 `PtRh-98Jac` の不変反応（1700-2410 K）

| T (K) | phases (x ascending) | x |
|---|---|---|

評価間のばらつき（全評価の不変反応、同じ温度窓）:

| assessment | T (K) | phases |
|---|---|---|

### MLIP/EAM run の不変反応（07_invariants.tsv、同相区間の出入りを除く）

| run | T bracket (K) | changed pairs |
|---|---|---|
| GRACE-2L-OMAT (QHA solids, liquid 1910-2400 K) | 1990.0-2000.0 |  |
| GRACE-2L-OMAT (QHA solids, liquid 1910-2400 K) | 2030.0-2040.0 |  |
| GRACE-2L-OMAT (QHA solids, liquid 1910-2400 K) | 2090.0-2100.0 |  |
| NequIP-OAM-M | 2220.0-2230.0 |  |
| MACE-MPA-0 | 2090.0-2100.0 |  |
| SevenNet-MF-ompa | 1930.0-1940.0 |  |
| SevenNet-MF-ompa | 2090.0-2100.0 |  |
| GRACE-2L-OMAT (+2048-atom TI ends) | 1970.0-1980.0 |  |
| GRACE-2L-OMAT (+2048-atom TI ends) | 2160.0-2170.0 |  |
| NequIP-OAM-M (+TI ends) | 2260.0-2270.0 |  |
| MACE-MPA-0 (+TI ends) | 2040.0-2050.0 |  |
