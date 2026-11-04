# ORCHID v2026.10 との比較（stage 07 の出力）

データ: ORCHID-Assemblages 10.5281/zenodo.23735996（評価状態図の相領域内部点）、ORCHID-Values 10.5281/zenodo.23735569（文献の不変反応温度）。論文 arXiv:2610.41164 の §4.2 と同じ prevalence-weighted phase recall S = Σ n_p R_p / Σ n_p を各 run の T 格子と組成範囲に入る点だけで計算した。exact は相集合（多重集合）が完全一致した点の数。precision は予測した相のうち観測された相の割合。不変反応は、括弧 [T_low, T_high] の前後で変わる二相対に含まれる相の多重集合で同定し（同相対 p+p は p を 2 回数える: Ag-Cu の共晶は fcc+fcc+liquid）、kind = reaction（3 相以上）と melting（固相+液相で、その固相が括弧の上で消える = 合致溶融）だけを、同じ多重集合を持つ ORCHID の記録（INVARIANT_TEMPERATURE と 2 相の TRANSITION_TEMPERATURE、extraction_accepted）と照合した。dT_exp = T_run − median(experimental)。model は評価（CALPHAD）由来の値で参考。partial は、文献の相集合が我々の相集合に加えてモデルに無い相を含む場合（組成範囲や相の欠落による切り詰め）。x_run は括弧の上下の二相対端点の平均、x_lit は文献の印刷組成の中央値。

## 一覧

| run | system | points evaluable/total | exact | S | precision | S (represented only) | invariants matched | dT_exp (K) |
|---|---|---|---|---|---|---|---|---|
| agcu_eam | AG-CU | 3/6 | 2 | 0.80 | 0.80 | 0.80 | 0/0 | - |
| agcu_eam_2048 | AG-CU | 3/6 | 2 | 0.80 | 0.80 | 0.80 | 0/0 | - |
| agcu_grace_1l | AG-CU | 3/6 | 3 | 1.00 | 1.00 | 1.00 | 0/0 | - |
| agcu_grace_1l_ti | AG-CU | 3/6 | 2 | 0.80 | 0.80 | 0.80 | 0/0 | - |
| agcu_grace_fs | AG-CU | 3/6 | 2 | 1.00 | 0.83 | 1.00 | 0/1 | - |
| agcu_grace_fs_ti | AG-CU | 3/6 | 2 | 1.00 | 0.83 | 1.00 | 0/3 | - |
| agcu_sevenn_0 | AG-CU | 4/6 | 0 | 0.67 | 0.50 | 0.67 | 0/0 | - |
| agcu_sevenn_0_ti | AG-CU | 3/6 | 1 | 0.80 | 0.67 | 0.80 | 0/0 | - |
| alli_ace | AL-LI | 4/14 | 1 | 0.67 | 0.80 | 0.67 | 2/2 | B32+fcc+liquid: -107; B32+liquid: -115 |
| alli_ace_b32ti | AL-LI | 4/14 | 1 | 0.67 | 0.80 | 0.67 | 2/2 | B32+fcc+liquid: -107; B32+liquid: -125 |
| alli_ace_m6 | AL-LI | 4/14 | 1 | 0.67 | 0.80 | 0.67 | 2/2 | B32+fcc+liquid: -107; B32+liquid: -115 |
| alli_grace_1l | AL-LI | 4/14 | 2 | 0.67 | 1.00 | 0.67 | 2/2 | B32+fcc+liquid: -147; B32+liquid: -155 |
| alli_grace_2l | AL-LI | 4/14 | 2 | 0.67 | 1.00 | 0.67 | 2/2 | B32+fcc+liquid: -117; B32+liquid: -155 |
| alli_grace_fs | AL-LI | 4/14 | 3 | 0.83 | 1.00 | 0.83 | 2/2 | B32+fcc+liquid: -127; B32+liquid: -165 |
| alli_mace_mpa_0 | AL-LI | 4/14 | 2 | 0.67 | 1.00 | 0.67 | 2/2 | B32+fcc+liquid: -97; B32+liquid: -145 |
| alli_mattersim_1m | AL-LI | 2/14 | 1 | 0.67 | 1.00 | 0.67 | 0/0 | - |
| alli_nequip_oam_m | AL-LI | 4/14 | 3 | 0.83 | 1.00 | 0.83 | 2/2 | B32+fcc+liquid: -67; B32+liquid: -75 |
| alli_sevenn_0 | AL-LI | 4/14 | 2 | 0.67 | 0.80 | 0.67 | 1/1 | B32+fcc+liquid: +63 |
| alli_sevenn_mf_ompa | AL-LI | 4/14 | 1 | 0.67 | 0.80 | 0.67 | 2/2 | B32+fcc+liquid: -17; B32+liquid: -55 |
| nial_grace_1l | AL-NI | 12/17 | 7 | 0.84 | 0.73 | 1.00 | 2/5 | B2+L12+liquid: -7; L12+fccNi+liquid: +20 |
| nial_grace_1l_ti | AL-NI | 12/17 | 7 | 0.84 | 0.73 | 1.00 | 2/5 | B2+L12+liquid: +3; L12+fccNi+liquid: +20 |
| nial_grace_fs | AL-NI | 12/17 | 5 | 0.74 | 0.70 | 0.86 | 2/4 | B2+L12+liquid: -107; L12+fccNi+liquid: +30 |
| nial_grace_fs_ti | AL-NI | 12/17 | 6 | 0.68 | 0.72 | 0.86 | 1/4 | B2+L12+liquid: -57 |
| nial_sevenn_0 | AL-NI | 12/17 | 6 | 0.84 | 0.73 | 0.84 | 1/3 | NiAl3+fccAl+liquid: +442 |
| nial_sevenn_0_ti | AL-NI | 12/17 | 6 | 0.84 | 0.73 | 0.84 | 1/3 | NiAl3+fccAl+liquid: +222 |

## agcu_eam  (AG-CU, x = x_Cu)

相: fcc, liquid; T 格子 1100–1400 K（二相対は 1100–1370 K）; 組成範囲 0.00–1.00; 純 AG の融点括弧 1320–1330 K (ORCHID unary AG に融点記録なし)

### 相領域の内部点（ORCHID-Assemblages）

点 6、評価可能 3（T 格子と組成範囲の内側）、exact 2、S = 0.80、precision = 0.80

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 754 | 0.515 | fcc+fcc | - | outside_T  |
| 974 | 0.041 | fcc | - | outside_T  |
| 1076 | 0.983 | fcc | - | outside_T  |
| 1103 | 0.184 | fcc+liquid | fcc+fcc | T_grid=1100 x |
| 1143 | 0.786 | fcc+liquid | fcc+liquid | T_grid=1140 OK |
| 1309 | 0.457 | liquid | liquid | T_grid=1310 OK |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1170–1180 | artefact | fcc+fcc | {"fcc": 0.118} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- fcc+fcc+liquid: 1053 K (1/4); represented=True; in_T_grid=False

## agcu_eam_2048  (AG-CU, x = x_Cu)

相: fcc, liquid; T 格子 1100–1400 K（二相対は 1100–1370 K）; 組成範囲 0.00–1.00; 純 AG の融点括弧 1260–1270 K (ORCHID unary AG に融点記録なし)

### 相領域の内部点（ORCHID-Assemblages）

点 6、評価可能 3（T 格子と組成範囲の内側）、exact 2、S = 0.80、precision = 0.80

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 754 | 0.515 | fcc+fcc | - | outside_T  |
| 974 | 0.041 | fcc | - | outside_T  |
| 1076 | 0.983 | fcc | - | outside_T  |
| 1103 | 0.184 | fcc+liquid | fcc+fcc | T_grid=1100 x |
| 1143 | 0.786 | fcc+liquid | fcc+liquid | T_grid=1140 OK |
| 1309 | 0.457 | liquid | liquid | T_grid=1310 OK |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1140–1150 | artefact | fcc+fcc | {"fcc": 0.125} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1150–1160 | artefact | fcc+fcc | {"fcc": 0.11} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1190–1200 | artefact | fcc+fcc | {"fcc": 0.11} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- fcc+fcc+liquid: 1053 K (1/4); represented=True; in_T_grid=False

## agcu_grace_1l  (AG-CU, x = x_Cu)

相: fcc, liquid; T 格子 1100–1400 K（二相対は 1100–1320 K）; 組成範囲 0.00–1.00

### 相領域の内部点（ORCHID-Assemblages）

点 6、評価可能 3（T 格子と組成範囲の内側）、exact 3、S = 1.00、precision = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 754 | 0.515 | fcc+fcc | - | outside_T  |
| 974 | 0.041 | fcc | - | outside_T  |
| 1076 | 0.983 | fcc | - | outside_T  |
| 1103 | 0.184 | fcc+liquid | fcc+liquid | T_grid=1100 OK |
| 1143 | 0.786 | fcc+liquid | fcc+liquid | T_grid=1140 OK |
| 1309 | 0.457 | liquid | liquid | T_grid=1310 OK |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

run に不変反応なし（07_invariants.tsv が空）。

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- fcc+fcc+liquid: 1053 K (1/4); represented=True; in_T_grid=False

## agcu_grace_1l_ti  (AG-CU, x = x_Cu)

相: fcc, liquid; T 格子 1100–1400 K（二相対は 1100–1300 K）; 組成範囲 0.00–1.00

### 相領域の内部点（ORCHID-Assemblages）

点 6、評価可能 3（T 格子と組成範囲の内側）、exact 2、S = 0.80、precision = 0.80

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 754 | 0.515 | fcc+fcc | - | outside_T  |
| 974 | 0.041 | fcc | - | outside_T  |
| 1076 | 0.983 | fcc | - | outside_T  |
| 1103 | 0.184 | fcc+liquid | fcc+fcc | T_grid=1100 x |
| 1143 | 0.786 | fcc+liquid | fcc+liquid | T_grid=1140 OK |
| 1309 | 0.457 | liquid | liquid | T>1300 (no tie-lines left) OK |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1110–1120 | artefact | fcc+fcc | {"fcc": 0.578} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- fcc+fcc+liquid: 1053 K (1/4); represented=True; in_T_grid=False

## agcu_grace_fs  (AG-CU, x = x_Cu)

相: fcc, liquid; T 格子 1100–1400 K（二相対は 1100–1400 K）; 組成範囲 0.00–1.00

### 相領域の内部点（ORCHID-Assemblages）

点 6、評価可能 3（T 格子と組成範囲の内側）、exact 2、S = 1.00、precision = 0.83

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 754 | 0.515 | fcc+fcc | - | outside_T  |
| 974 | 0.041 | fcc | - | outside_T  |
| 1076 | 0.983 | fcc | - | outside_T  |
| 1103 | 0.184 | fcc+liquid | fcc+liquid | T_grid=1100 OK |
| 1143 | 0.786 | fcc+liquid | fcc+liquid | T_grid=1140 OK |
| 1309 | 0.457 | liquid | liquid+liquid | T_grid=1310 x |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1110–1120 | artefact | liquid+liquid | {"liquid": 0.393} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1310–1320 | melting | fcc+liquid | {"liquid": 0.98, "fcc": 0.991} | 0 | - | - | 0 | - | - | no literature record with this phase set |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- fcc+fcc+liquid: 1053 K (1/4); represented=True; in_T_grid=False

## agcu_grace_fs_ti  (AG-CU, x = x_Cu)

相: fcc, liquid; T 格子 1100–1400 K（二相対は 1100–1400 K）; 組成範囲 0.00–1.00

### 相領域の内部点（ORCHID-Assemblages）

点 6、評価可能 3（T 格子と組成範囲の内側）、exact 2、S = 1.00、precision = 0.83

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 754 | 0.515 | fcc+fcc | - | outside_T  |
| 974 | 0.041 | fcc | - | outside_T  |
| 1076 | 0.983 | fcc | - | outside_T  |
| 1103 | 0.184 | fcc+liquid | fcc+liquid | T_grid=1100 OK |
| 1143 | 0.786 | fcc+liquid | fcc+liquid | T_grid=1140 OK |
| 1309 | 0.457 | liquid | liquid+liquid | T_grid=1310 x |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1100–1110 | artefact | liquid+liquid | {"liquid": 0.394} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1220–1230 | melting | fcc+liquid | {"liquid": 0.929, "fcc": 0.96} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1240–1250 | liquid_reaches | fcc+liquid | {"liquid": 0.846, "fcc": 0.976} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1250–1260 | melting | fcc+liquid | {"liquid": 0.846, "fcc": 0.976} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1290–1300 | liquid_reaches | fcc+liquid | {"liquid": 0.963, "fcc": 0.986} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1300–1310 | melting | fcc+liquid | {"liquid": 0.963, "fcc": 0.986} | 0 | - | - | 0 | - | - | no literature record with this phase set |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- fcc+fcc+liquid: 1053 K (1/4); represented=True; in_T_grid=False

## agcu_sevenn_0  (AG-CU, x = x_Cu)

相: fcc, liquid; T 格子 1050–1400 K（二相対は 1050–1400 K）; 組成範囲 0.00–1.00; 純 AG は格子上限 1400 K まで融けない

### 相領域の内部点（ORCHID-Assemblages）

点 6、評価可能 4（T 格子と組成範囲の内側）、exact 0、S = 0.67、precision = 0.50

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 754 | 0.515 | fcc+fcc | - | outside_T  |
| 974 | 0.041 | fcc | - | outside_T  |
| 1076 | 0.983 | fcc | fcc+fcc | T_grid=1080 x |
| 1103 | 0.184 | fcc+liquid | fcc+fcc | T_grid=1100 x |
| 1143 | 0.786 | fcc+liquid | fcc+fcc | T_grid=1140 x |
| 1309 | 0.457 | liquid | fcc+liquid | T_grid=1310 x |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1240–1250 | artefact | fcc+fcc | {"fcc": 0.54} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- fcc+fcc+liquid: 1053 K (1/4); represented=True; in_T_grid=True

## agcu_sevenn_0_ti  (AG-CU, x = x_Cu)

相: fcc, liquid; T 格子 1100–1400 K（二相対は 1100–1400 K）; 組成範囲 0.00–1.00; 純 AG は格子上限 1400 K まで融けない

### 相領域の内部点（ORCHID-Assemblages）

点 6、評価可能 3（T 格子と組成範囲の内側）、exact 1、S = 0.80、precision = 0.67

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 754 | 0.515 | fcc+fcc | - | outside_T  |
| 974 | 0.041 | fcc | - | outside_T  |
| 1076 | 0.983 | fcc | - | outside_T  |
| 1103 | 0.184 | fcc+liquid | fcc+fcc | T_grid=1100 x |
| 1143 | 0.786 | fcc+liquid | fcc+liquid | T_grid=1140 OK |
| 1309 | 0.457 | liquid | fcc+liquid | T_grid=1310 x |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1130–1140 | artefact | fcc+fcc | {"fcc": 0.553} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1140–1150 | artefact | fcc+fcc | {"fcc": 0.572} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1150–1160 | artefact | fcc+fcc | {"fcc": 0.572} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- fcc+fcc+liquid: 1053 K (1/4); represented=True; in_T_grid=False

## alli_ace  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–880 K）; 組成範囲 0.00–0.52; 純 AL の融点括弧 880–890 K vs ORCHID unary AL: 933.5 (unsp); dT = -48 K

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 1、S = 0.67、precision = 0.80

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc+fcc | T_grid=730 x |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | liquid | T>880 (no tie-lines left) x |
| 907 | 0.393 | B32+liquid | liquid | T>880 (no tie-lines left) x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 760–770 | reaction | B32+fcc+liquid | {"fcc": 0.164, "B32": 0.482, "liquid": 0.32} | 4 | 872 (863–875) | -107 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 790–800 | artefact | fcc+fcc | {"fcc": 0.068} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 850–860 | melting | B32+liquid | {"liquid": 0.493, "B32": 0.51} | 1 | 970 (970–970) | -115 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## alli_ace_b32ti  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–880 K）; 組成範囲 0.00–0.52; 純 AL の融点括弧 880–890 K vs ORCHID unary AL: 933.5 (unsp); dT = -48 K

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 1、S = 0.67、precision = 0.80

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc+fcc | T_grid=730 x |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | liquid | T>880 (no tie-lines left) x |
| 907 | 0.393 | B32+liquid | liquid | T>880 (no tie-lines left) x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 760–770 | reaction | B32+fcc+liquid | {"fcc": 0.167, "B32": 0.489, "liquid": 0.328} | 4 | 872 (863–875) | -107 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 790–800 | artefact | fcc+fcc | {"fcc": 0.068} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 840–850 | melting | B32+liquid | {"liquid": 0.476, "B32": 0.51} | 1 | 970 (970–970) | -125 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## alli_ace_m6  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–880 K）; 組成範囲 0.00–0.52; 純 AL の融点括弧 880–890 K vs ORCHID unary AL: 933.5 (unsp); dT = -48 K

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 1、S = 0.67、precision = 0.80

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc+fcc | T_grid=730 x |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | liquid | T>880 (no tie-lines left) x |
| 907 | 0.393 | B32+liquid | liquid | T>880 (no tie-lines left) x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 760–770 | reaction | B32+fcc+liquid | {"fcc": 0.164, "B32": 0.483, "liquid": 0.313} | 4 | 872 (863–875) | -107 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 790–800 | artefact | fcc+fcc | {"fcc": 0.068} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 850–860 | melting | B32+liquid | {"liquid": 0.494, "B32": 0.511} | 1 | 970 (970–970) | -115 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## alli_grace_1l  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–860 K）; 組成範囲 0.00–0.52

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 2、S = 0.67、precision = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc | T_grid=730 OK |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | liquid | T>860 (no tie-lines left) x |
| 907 | 0.393 | B32+liquid | liquid | T>860 (no tie-lines left) x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 720–730 | reaction | B32+fcc+liquid | {"fcc": 0.201, "B32": 0.476, "liquid": 0.334} | 4 | 872 (863–875) | -147 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 810–820 | melting | B32+liquid | {"liquid": 0.489, "B32": 0.506} | 1 | 970 (970–970) | -155 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## alli_grace_2l  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–910 K）; 組成範囲 0.00–0.52

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 2、S = 0.67、precision = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc | T_grid=730 OK |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | liquid | T_grid=890 x |
| 907 | 0.393 | B32+liquid | liquid | T_grid=910 x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 750–760 | reaction | B32+fcc+liquid | {"fcc": 0.182, "B32": 0.497, "liquid": 0.363} | 4 | 872 (863–875) | -117 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 810–820 | melting | B32+liquid | {"liquid": 0.481, "B32": 0.514} | 1 | 970 (970–970) | -155 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## alli_grace_fs  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–1050 K）; 組成範囲 0.00–0.51; 純 AL の融点括弧 950–960 K vs ORCHID unary AL: 933.5 (unsp); dT = +22 K

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 3、S = 0.83、precision = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc | T_grid=730 OK |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | fcc+liquid | T_grid=890 OK |
| 907 | 0.393 | B32+liquid | liquid | T_grid=910 x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 740–750 | reaction | B32+fcc+liquid | {"fcc": 0.23, "B32": 0.438, "liquid": 0.319} | 4 | 872 (863–875) | -127 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 800–810 | melting | B32+liquid | {"liquid": 0.447, "B32": 0.462} | 1 | 970 (970–970) | -165 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## alli_mace_mpa_0  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–1030 K）; 組成範囲 0.00–0.52; 純 AL の融点括弧 1030–1040 K vs ORCHID unary AL: 933.5 (unsp); dT = +102 K

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 2、S = 0.67、precision = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc | T_grid=730 OK |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | fcc | T_grid=890 x |
| 907 | 0.393 | B32+liquid | liquid | T_grid=910 x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 770–780 | reaction | B32+fcc+liquid | {"fcc": 0.236, "B32": 0.49, "liquid": 0.386} | 4 | 872 (863–875) | -97 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 820–830 | melting | B32+liquid | {"liquid": 0.474, "B32": 0.509} | 1 | 970 (970–970) | -145 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## alli_mattersim_1m  (AL-LI, x = x_Li)

相: fcc, liquid; T 格子 700–1100 K（二相対は 700–790 K）; 組成範囲 0.00–0.35; 純 AL の融点括弧 770–780 K vs ORCHID unary AL: 933.5 (unsp); dT = -158 K

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 2（T 格子と組成範囲の内側）、exact 1、S = 0.67、precision = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3,B32) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  (not in model: B32) |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc | T_grid=730 OK |
| 733 | 0.497 | B32 | - | outside_x  (not in model: B32) |
| 862 | 0.620 | B32+liquid | - | outside_x  (not in model: B32) |
| 891 | 0.146 | fcc+liquid | liquid | T>790 (no tie-lines left) x |
| 907 | 0.393 | B32+liquid | - | outside_x  (not in model: B32) |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

run に不変反応なし（07_invariants.tsv が空）。

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True
- B32+fcc+liquid: 872 K (4/4); represented=False; in_T_grid=True
- B32+liquid: 970 K (1/3); represented=False; in_T_grid=True

## alli_nequip_oam_m  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–920 K）; 組成範囲 0.00–0.52

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 3、S = 0.83、precision = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc | T_grid=730 OK |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | fcc+liquid | T_grid=890 OK |
| 907 | 0.393 | B32+liquid | liquid | T_grid=910 x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 800–810 | reaction | B32+fcc+liquid | {"fcc": 0.172, "B32": 0.498, "liquid": 0.323} | 4 | 872 (863–875) | -67 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 890–900 | melting | B32+liquid | {"liquid": 0.459, "B32": 0.512} | 1 | 970 (970–970) | -75 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## alli_sevenn_0  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–1100 K）; 組成範囲 0.00–0.51

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 2、S = 0.67、precision = 0.80

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc | T_grid=730 OK |
| 733 | 0.497 | B32 | B32 | T_grid=730 OK |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | fcc | T_grid=890 x |
| 907 | 0.393 | B32+liquid | B32+fcc | T_grid=910 x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 930–940 | reaction | B32+fcc+liquid | {"fcc": 0.25, "B32": 0.482, "liquid": 0.5} | 4 | 872 (863–875) | +63 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 1000–1010 | artefact | fcc+fcc | {"fcc": 0.247} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True
- B32+liquid: 970 K (1/3); represented=True; in_T_grid=True

## alli_sevenn_mf_ompa  (AL-LI, x = x_Li)

相: B32, fcc, liquid; T 格子 700–1100 K（二相対は 700–980 K）; 組成範囲 0.00–0.52

### 相領域の内部点（ORCHID-Assemblages）

点 14、評価可能 4（T 格子と組成範囲の内側）、exact 1、S = 0.67、precision = 0.80

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 411 | 0.845 | Al4Li9+bccLi | - | outside_T  (not in model: Al4Li9,bccLi) |
| 460 | 0.645 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 498 | 0.830 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 568 | 0.557 | Al2Li3+B32 | - | outside_T  (not in model: Al2Li3) |
| 574 | 0.809 | Al4Li9+liquid | - | outside_T  (not in model: Al4Li9) |
| 575 | 0.646 | Al2Li3+Al4Li9 | - | outside_T  (not in model: Al2Li3,Al4Li9) |
| 602 | 0.271 | B32+fcc | - | outside_T  |
| 689 | 0.723 | Al2Li3+liquid | - | outside_T  (not in model: Al2Li3) |
| 731 | 0.048 | fcc | fcc | T_grid=730 OK |
| 733 | 0.497 | B32 | B32+fcc | T_grid=730 x |
| 862 | 0.620 | B32+liquid | - | outside_x  |
| 891 | 0.146 | fcc+liquid | fcc | T_grid=890 x |
| 907 | 0.393 | B32+liquid | liquid | T_grid=910 x |
| 955 | 0.831 | liquid | - | outside_x  |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 850–860 | reaction | B32+fcc+liquid | {"fcc": 0.166, "B32": 0.502, "liquid": 0.326} | 4 | 872 (863–875) | -17 | 4 | 874 | {"L": 0.256, "fcc(Al)": 0.138, "AlLi": 0.5} | matched |
| 910–920 | melting | B32+liquid | {"liquid": 0.464, "B32": 0.513} | 1 | 970 (970–970) | -55 | 3 | 975 | {"L": 0.49, "AlLi": 0.49} | matched |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- Al4Li9+bccLi+liquid: 454 K (1/4); represented=False; in_T_grid=False
- Al4Li9+AlLi2+liquid: 543 K (1/1); represented=False; in_T_grid=False
- Al2Li3+AlLi2+liquid: 608 K (1/1); represented=False; in_T_grid=False
- Al2Li3+Al4Li9+liquid: 609 K (0/4); represented=False; in_T_grid=False
- Al2Li3+B32+liquid: 793 K (3/4); represented=False; in_T_grid=True

## nial_grace_1l  (AL-NI, x = x_Ni)

相: B2, L12, NiAl3, fccNi, liquid; T 格子 950–2000 K（二相対は 950–2000 K）; 組成範囲 0.00–1.00

### 相領域の内部点（ORCHID-Assemblages）

点 17、評価可能 12（T 格子と組成範囲の内側）、exact 7、S = 0.84、precision = 0.73; 我々の相語彙にある相だけ: 評価可能 9, exact 7, S = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 694 | 0.655 | Al3Ni5 | - | outside_T  (not in model: Al3Ni5) |
| 793 | 0.124 | NiAl3+fccAl | - | outside_T  (not in model: fccAl) |
| 825 | 0.621 | Al3Ni5+B2 | - | outside_T  (not in model: Al3Ni5) |
| 827 | 0.698 | Al3Ni5+L12 | - | outside_T  (not in model: Al3Ni5) |
| 900 | 0.309 | Ni2Al3+NiAl3 | - | outside_T  (not in model: Ni2Al3) |
| 977 | 0.389 | Ni2Al3 | B2+NiAl3 | T_grid=980 x (not in model: Ni2Al3) |
| 1009 | 0.159 | NiAl3+liquid | NiAl3+liquid | T_grid=1010 OK |
| 1015 | 0.425 | B2+Ni2Al3 | B2+NiAl3 | T_grid=1010 x (not in model: Ni2Al3) |
| 1026 | 0.815 | L12+fccNi | L12+fccNi | T_grid=1030 OK |
| 1166 | 0.746 | L12 | B2+L12 | T_grid=1170 x |
| 1253 | 0.286 | Ni2Al3+liquid | B2+liquid | T_grid=1250 x (not in model: Ni2Al3) |
| 1255 | 0.923 | fccNi | L12+fccNi | T_grid=1260 x |
| 1261 | 0.681 | B2+L12 | B2+L12 | T_grid=1260 OK |
| 1317 | 0.539 | B2 | B2 | T_grid=1320 OK |
| 1602 | 0.385 | B2+liquid | B2+liquid | T_grid=1600 OK |
| 1753 | 0.653 | B2+liquid | B2+liquid | T_grid=1750 OK |
| 1811 | 0.187 | liquid | liquid | T_grid=1810 OK |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1040–1050 | liquid_reaches | NiAl3+liquid | {"liquid": 0.195, "NiAl3": 0.25} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1090–1100 | reaction | B2+NiAl3+liquid | {"NiAl3": 0.25, "B2": 0.471, "liquid": 0.262} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1630–1640 | reaction | B2+L12+liquid | {"B2": 0.611, "L12": 0.781, "liquid": 0.7} | 8 | 1642 (1633–1653) | -7 | 8 | 1642 | {"L": 0.752, "γ′": 0.76, "bcc": 0.7, "B2": 0.71, "L12": 0.76, "γ'": 0.76} | matched |
| 1660–1670 | reaction | L12+fccNi+liquid | {"L12": 0.781, "fccNi": 0.912, "liquid": 0.885} | 8 | 1645 (1635–1656) | +20 | 8 | 1643 | {"γ′": 0.766, "L": 0.755, "fcc": 0.785, "(Ni)": 0.785, "L12": 0.762, "γ'": 0.761, "γ": 0.785} | matched |
| 1690–1700 | melting | fccNi+liquid | {"liquid": 0.942, "fccNi": 0.952} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1730–1740 | artefact | B2+B2 | {"B2": 0.493} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1760–1770 | melting | L12+liquid | {"liquid": 0.782, "L12": 0.781} | 0 | - | - | 0 | - | - | no literature record with this phase set |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- NiAl3+fccAl+liquid: 913 K (4/7); represented=False; in_T_grid=False
- NiAl3+fccNi+liquid: 913 K (1/1); represented=True; in_T_grid=False
- Al4Ni3+B2+Ni2Al3: 973 K (1/1); represented=False; in_T_grid=True
- Al3Ni5+B2+L12: 973 K (4/9); represented=False; in_T_grid=True
- Ni2Al3+NiAl3+liquid: 1127 K (7/8); represented=False; in_T_grid=True
- B2+Ni2Al3+liquid: 1406 K (7/8); represented=False; in_T_grid=True
- B2+liquid: 1915 K (6/8); represented=True; in_T_grid=True

## nial_grace_1l_ti  (AL-NI, x = x_Ni)

相: B2, L12, NiAl3, fccNi, liquid; T 格子 950–2000 K（二相対は 950–1950 K）; 組成範囲 0.00–1.00

### 相領域の内部点（ORCHID-Assemblages）

点 17、評価可能 12（T 格子と組成範囲の内側）、exact 7、S = 0.84、precision = 0.73; 我々の相語彙にある相だけ: 評価可能 9, exact 7, S = 1.00

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 694 | 0.655 | Al3Ni5 | - | outside_T  (not in model: Al3Ni5) |
| 793 | 0.124 | NiAl3+fccAl | - | outside_T  (not in model: fccAl) |
| 825 | 0.621 | Al3Ni5+B2 | - | outside_T  (not in model: Al3Ni5) |
| 827 | 0.698 | Al3Ni5+L12 | - | outside_T  (not in model: Al3Ni5) |
| 900 | 0.309 | Ni2Al3+NiAl3 | - | outside_T  (not in model: Ni2Al3) |
| 977 | 0.389 | Ni2Al3 | B2+NiAl3 | T_grid=980 x (not in model: Ni2Al3) |
| 1009 | 0.159 | NiAl3+liquid | NiAl3+liquid | T_grid=1010 OK |
| 1015 | 0.425 | B2+Ni2Al3 | B2+NiAl3 | T_grid=1010 x (not in model: Ni2Al3) |
| 1026 | 0.815 | L12+fccNi | L12+fccNi | T_grid=1030 OK |
| 1166 | 0.746 | L12 | B2+L12 | T_grid=1170 x |
| 1253 | 0.286 | Ni2Al3+liquid | B2+liquid | T_grid=1250 x (not in model: Ni2Al3) |
| 1255 | 0.923 | fccNi | L12+fccNi | T_grid=1260 x |
| 1261 | 0.681 | B2+L12 | B2+L12 | T_grid=1260 OK |
| 1317 | 0.539 | B2 | B2 | T_grid=1320 OK |
| 1602 | 0.385 | B2+liquid | B2+liquid | T_grid=1600 OK |
| 1753 | 0.653 | B2+liquid | B2+liquid | T_grid=1750 OK |
| 1811 | 0.187 | liquid | liquid | T_grid=1810 OK |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1040–1050 | liquid_reaches | NiAl3+liquid | {"liquid": 0.195, "NiAl3": 0.25} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1090–1100 | reaction | B2+NiAl3+liquid | {"NiAl3": 0.25, "B2": 0.471, "liquid": 0.262} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1640–1650 | reaction | B2+L12+liquid | {"B2": 0.611, "L12": 0.781, "liquid": 0.703} | 8 | 1642 (1633–1653) | +3 | 8 | 1642 | {"L": 0.752, "γ′": 0.76, "bcc": 0.7, "B2": 0.71, "L12": 0.76, "γ'": 0.76} | matched |
| 1660–1670 | reaction | L12+fccNi+liquid | {"L12": 0.781, "fccNi": 0.915, "liquid": 0.887} | 8 | 1645 (1635–1656) | +20 | 8 | 1643 | {"γ′": 0.766, "L": 0.755, "fcc": 0.785, "(Ni)": 0.785, "L12": 0.762, "γ'": 0.761, "γ": 0.785} | matched |
| 1700–1710 | melting | fccNi+liquid | {"liquid": 0.964, "fccNi": 0.975} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1760–1770 | melting | L12+liquid | {"liquid": 0.782, "L12": 0.781} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1940–1950 | artefact | B2+B2 | {"B2": 0.487} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- NiAl3+fccAl+liquid: 913 K (4/7); represented=False; in_T_grid=False
- NiAl3+fccNi+liquid: 913 K (1/1); represented=True; in_T_grid=False
- Al4Ni3+B2+Ni2Al3: 973 K (1/1); represented=False; in_T_grid=True
- Al3Ni5+B2+L12: 973 K (4/9); represented=False; in_T_grid=True
- Ni2Al3+NiAl3+liquid: 1127 K (7/8); represented=False; in_T_grid=True
- B2+Ni2Al3+liquid: 1406 K (7/8); represented=False; in_T_grid=True
- B2+liquid: 1915 K (6/8); represented=True; in_T_grid=True

## nial_grace_fs  (AL-NI, x = x_Ni)

相: B2, L12, NiAl3, fccAl, fccNi, liquid; T 格子 950–2000 K（二相対は 950–2000 K）; 組成範囲 0.00–1.00; 純 AL は格子上限 2000 K まで融けない (ORCHID unary AL: 933.5 K)

### 相領域の内部点（ORCHID-Assemblages）

点 17、評価可能 12（T 格子と組成範囲の内側）、exact 5、S = 0.74、precision = 0.70; 我々の相語彙にある相だけ: 評価可能 9, exact 5, S = 0.86

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 694 | 0.655 | Al3Ni5 | - | outside_T  (not in model: Al3Ni5) |
| 793 | 0.124 | NiAl3+fccAl | - | outside_T  |
| 825 | 0.621 | Al3Ni5+B2 | - | outside_T  (not in model: Al3Ni5) |
| 827 | 0.698 | Al3Ni5+L12 | - | outside_T  (not in model: Al3Ni5) |
| 900 | 0.309 | Ni2Al3+NiAl3 | - | outside_T  (not in model: Ni2Al3) |
| 977 | 0.389 | Ni2Al3 | B2+NiAl3 | T_grid=980 x (not in model: Ni2Al3) |
| 1009 | 0.159 | NiAl3+liquid | fccAl+liquid | T_grid=1010 x |
| 1015 | 0.425 | B2+Ni2Al3 | B2+NiAl3 | T_grid=1010 x (not in model: Ni2Al3) |
| 1026 | 0.815 | L12+fccNi | L12+fccNi | T_grid=1030 OK |
| 1166 | 0.746 | L12 | B2+L12 | T_grid=1170 x |
| 1253 | 0.286 | Ni2Al3+liquid | liquid | T_grid=1250;ambiguous(liquid|B2) x (not in model: Ni2Al3) |
| 1255 | 0.923 | fccNi | fccNi | T_grid=1260 OK |
| 1261 | 0.681 | B2+L12 | B2+L12 | T_grid=1260 OK |
| 1317 | 0.539 | B2 | B2 | T_grid=1320 OK |
| 1602 | 0.385 | B2+liquid | B2+liquid | T_grid=1600 OK |
| 1753 | 0.653 | B2+liquid | liquid | T_grid=1750 x |
| 1811 | 0.187 | liquid | fccAl+liquid | T_grid=1810 x |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1040–1050 | other | B2+NiAl3 | {"NiAl3": 0.25, "B2": 0.49} | 0 | - | - | 0 | - | - | not compared |
| 1090–1100 | liquid_reaches | B2+liquid | {"liquid": 0.29, "B2": 0.493} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1180–1190 | liquid_reaches | B2+liquid | {"liquid": 0.3, "B2": 0.494} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1290–1300 | liquid_reaches | B2+liquid | {"liquid": 0.308, "B2": 0.496} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1530–1540 | reaction | B2+L12+liquid | {"B2": 0.611, "L12": 0.779, "liquid": 0.683} | 8 | 1642 (1633–1653) | -107 | 8 | 1642 | {"L": 0.752, "γ′": 0.76, "bcc": 0.7, "B2": 0.71, "L12": 0.76, "γ'": 0.76} | matched |
| 1670–1680 | reaction | L12+fccNi+liquid | {"L12": 0.781, "fccNi": 0.886, "liquid": 0.86} | 8 | 1645 (1635–1656) | +30 | 8 | 1643 | {"γ′": 0.766, "L": 0.755, "fcc": 0.785, "(Ni)": 0.785, "L12": 0.762, "γ'": 0.761, "γ": 0.785} | matched |
| 1730–1740 | melting | fccNi+liquid | {"liquid": 0.925, "fccNi": 0.933} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1800–1810 | melting | L12+liquid | {"liquid": 0.781, "L12": 0.781} | 0 | - | - | 0 | - | - | no literature record with this phase set |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- NiAl3+fccAl+liquid: 913 K (4/7); represented=True; in_T_grid=False
- NiAl3+fccNi+liquid: 913 K (1/1); represented=True; in_T_grid=False
- Al4Ni3+B2+Ni2Al3: 973 K (1/1); represented=False; in_T_grid=True
- Al3Ni5+B2+L12: 973 K (4/9); represented=False; in_T_grid=True
- Ni2Al3+NiAl3+liquid: 1127 K (7/8); represented=False; in_T_grid=True
- B2+Ni2Al3+liquid: 1406 K (7/8); represented=False; in_T_grid=True
- B2+liquid: 1915 K (6/8); represented=True; in_T_grid=True

## nial_grace_fs_ti  (AL-NI, x = x_Ni)

相: B2, L12, NiAl3, fccNi, liquid; T 格子 950–2000 K（二相対は 950–1870 K）; 組成範囲 0.00–1.00

### 相領域の内部点（ORCHID-Assemblages）

点 17、評価可能 12（T 格子と組成範囲の内側）、exact 6、S = 0.68、precision = 0.72; 我々の相語彙にある相だけ: 評価可能 9, exact 6, S = 0.86

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 694 | 0.655 | Al3Ni5 | - | outside_T  (not in model: Al3Ni5) |
| 793 | 0.124 | NiAl3+fccAl | - | outside_T  (not in model: fccAl) |
| 825 | 0.621 | Al3Ni5+B2 | - | outside_T  (not in model: Al3Ni5) |
| 827 | 0.698 | Al3Ni5+L12 | - | outside_T  (not in model: Al3Ni5) |
| 900 | 0.309 | Ni2Al3+NiAl3 | - | outside_T  (not in model: Ni2Al3) |
| 977 | 0.389 | Ni2Al3 | B2+NiAl3 | T_grid=980 x (not in model: Ni2Al3) |
| 1009 | 0.159 | NiAl3+liquid | NiAl3 | T_grid=1010 x |
| 1015 | 0.425 | B2+Ni2Al3 | B2+NiAl3 | T_grid=1010 x (not in model: Ni2Al3) |
| 1026 | 0.815 | L12+fccNi | L12+fccNi | T_grid=1030 OK |
| 1166 | 0.746 | L12 | B2+L12 | T_grid=1170 x |
| 1253 | 0.286 | Ni2Al3+liquid | B2 | T_grid=1250 x (not in model: Ni2Al3) |
| 1255 | 0.923 | fccNi | fccNi | T_grid=1260 OK |
| 1261 | 0.681 | B2+L12 | B2+L12 | T_grid=1260 OK |
| 1317 | 0.539 | B2 | B2 | T_grid=1320 OK |
| 1602 | 0.385 | B2+liquid | B2+liquid | T_grid=1600 OK |
| 1753 | 0.653 | B2+liquid | liquid | T_grid=1750 x |
| 1811 | 0.187 | liquid | liquid | T_grid=1810 OK |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1040–1050 | other | B2+NiAl3 | {"NiAl3": 0.25, "B2": 0.49} | 0 | - | - | 0 | - | - | not compared |
| 1090–1100 | liquid_reaches | B2+liquid | {"liquid": 0.29, "B2": 0.493} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1180–1190 | liquid_reaches | B2+liquid | {"liquid": 0.3, "B2": 0.494} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1280–1290 | artefact | B2+B2 | {"B2": 0.49} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1290–1300 | liquid_reaches | B2+liquid | {"liquid": 0.313, "B2": 0.471} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1580–1590 | reaction | B2+L12+liquid | {"B2": 0.611, "L12": 0.781, "liquid": 0.693} | 8 | 1642 (1633–1653) | -57 | 8 | 1642 | {"L": 0.752, "γ′": 0.76, "bcc": 0.7, "B2": 0.71, "L12": 0.76, "γ'": 0.76} | matched |
| 1650–1660 | liquid_reaches | fccNi+liquid | {"fccNi": 0.985, "liquid": 0.995} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1680–1690 | other | L12+fccNi | {"L12": 0.781, "fccNi": 0.884} | 0 | - | - | 0 | - | - | not compared |
| 1720–1730 | melting | fccNi+liquid | {"liquid": 0.923, "fccNi": 0.924} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1790–1800 | liquid_reaches | fccNi+liquid | {"liquid": 0.898, "fccNi": 0.897} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1800–1810 | melting | L12+liquid | {"liquid": 0.781, "L12": 0.781} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1810–1820 | melting | fccNi+liquid | {"liquid": 0.897, "fccNi": 0.897} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1850–1860 | artefact | B2+B2 | {"B2": 0.487} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- NiAl3+fccAl+liquid: 913 K (4/7); represented=False; in_T_grid=False
- NiAl3+fccNi+liquid: 913 K (1/1); represented=True; in_T_grid=False
- Al4Ni3+B2+Ni2Al3: 973 K (1/1); represented=False; in_T_grid=True
- Al3Ni5+B2+L12: 973 K (4/9); represented=False; in_T_grid=True
- Ni2Al3+NiAl3+liquid: 1127 K (7/8); represented=False; in_T_grid=True
- B2+Ni2Al3+liquid: 1406 K (7/8); represented=False; in_T_grid=True
- L12+fccNi+liquid: 1645 K (8/8); represented=True; in_T_grid=True
- B2+liquid: 1915 K (6/8); represented=True; in_T_grid=True

## nial_sevenn_0  (AL-NI, x = x_Ni)

相: B2, L12, Ni2Al3, NiAl3, fccAl, fccNi, liquid; T 格子 950–2000 K（二相対は 950–2000 K）; 組成範囲 0.00–1.00; 純 AL は格子上限 2000 K まで融けない (ORCHID unary AL: 933.5 K)

### 相領域の内部点（ORCHID-Assemblages）

点 17、評価可能 12（T 格子と組成範囲の内側）、exact 6、S = 0.84、precision = 0.73

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 694 | 0.655 | Al3Ni5 | - | outside_T  (not in model: Al3Ni5) |
| 793 | 0.124 | NiAl3+fccAl | - | outside_T  |
| 825 | 0.621 | Al3Ni5+B2 | - | outside_T  (not in model: Al3Ni5) |
| 827 | 0.698 | Al3Ni5+L12 | - | outside_T  (not in model: Al3Ni5) |
| 900 | 0.309 | Ni2Al3+NiAl3 | - | outside_T  |
| 977 | 0.389 | Ni2Al3 | Ni2Al3+NiAl3 | T_grid=980 x |
| 1009 | 0.159 | NiAl3+liquid | NiAl3+fccAl | T_grid=1010 x |
| 1015 | 0.425 | B2+Ni2Al3 | B2+Ni2Al3 | T_grid=1010 OK |
| 1026 | 0.815 | L12+fccNi | L12+fccNi | T_grid=1030 OK |
| 1166 | 0.746 | L12 | B2+L12 | T_grid=1170 x |
| 1253 | 0.286 | Ni2Al3+liquid | Ni2Al3+NiAl3 | T_grid=1250 x |
| 1255 | 0.923 | fccNi | fccNi | T_grid=1260 OK |
| 1261 | 0.681 | B2+L12 | B2+L12 | T_grid=1260 OK |
| 1317 | 0.539 | B2 | B2 | T_grid=1320 OK |
| 1602 | 0.385 | B2+liquid | B2+liquid | T_grid=1600 OK |
| 1753 | 0.653 | B2+liquid | B2+L12 | T_grid=1750 x |
| 1811 | 0.187 | liquid | fccAl+liquid | T_grid=1810 x |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1240–1250 | artefact | B2+B2 | {"B2": 0.497} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1250–1260 | reaction | B2+Ni2Al3+NiAl3 | {"NiAl3": 0.25, "Ni2Al3": 0.4, "B2": 0.471} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1350–1360 | reaction | NiAl3+fccAl+liquid | {"fccAl": 0.008, "NiAl3": 0.25, "liquid": 0.197} | 4 | 913 (913–913) | +442 | 7 | 915 | {"L": 0.027, "γ1": 0.25, "Al3Ni": 0.25, "fcc": 0.001} | matched |
| 1440–1450 | reaction | B2+NiAl3+liquid | {"liquid": 0.244, "NiAl3": 0.25, "B2": 0.471} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1450–1460 | other | L12+fccNi | {"L12": 0.781, "fccNi": 0.915} | 0 | - | - | 0 | - | - | not compared |
| 1490–1500 | liquid_reaches | L12+liquid | {"L12": 0.781, "liquid": 0.953} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |
| 1680–1690 | artefact | B2+B2 | {"B2": 0.502} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- NiAl3+fccNi+liquid: 913 K (1/1); represented=True; in_T_grid=False
- Al4Ni3+B2+Ni2Al3: 973 K (1/1); represented=False; in_T_grid=True
- Al3Ni5+B2+L12: 973 K (4/9); represented=False; in_T_grid=True
- Ni2Al3+NiAl3+liquid: 1127 K (7/8); represented=True; in_T_grid=True
- B2+Ni2Al3+liquid: 1406 K (7/8); represented=True; in_T_grid=True
- B2+L12+liquid: 1642 K (8/8); represented=True; in_T_grid=True
- L12+fccNi+liquid: 1645 K (8/8); represented=True; in_T_grid=True
- B2+liquid: 1915 K (6/8); represented=True; in_T_grid=True

## nial_sevenn_0_ti  (AL-NI, x = x_Ni)

相: B2, L12, Ni2Al3, NiAl3, fccAl, fccNi, liquid; T 格子 950–2000 K（二相対は 950–2000 K）; 組成範囲 0.00–1.00; 純 AL は格子上限 2000 K まで融けない (ORCHID unary AL: 933.5 K)

### 相領域の内部点（ORCHID-Assemblages）

点 17、評価可能 12（T 格子と組成範囲の内側）、exact 6、S = 0.84、precision = 0.73

| T_K | x | observed | predicted | note |
|---|---|---|---|---|
| 694 | 0.655 | Al3Ni5 | - | outside_T  (not in model: Al3Ni5) |
| 793 | 0.124 | NiAl3+fccAl | - | outside_T  |
| 825 | 0.621 | Al3Ni5+B2 | - | outside_T  (not in model: Al3Ni5) |
| 827 | 0.698 | Al3Ni5+L12 | - | outside_T  (not in model: Al3Ni5) |
| 900 | 0.309 | Ni2Al3+NiAl3 | - | outside_T  |
| 977 | 0.389 | Ni2Al3 | Ni2Al3+NiAl3 | T_grid=980 x |
| 1009 | 0.159 | NiAl3+liquid | NiAl3+fccAl | T_grid=1010 x |
| 1015 | 0.425 | B2+Ni2Al3 | B2+Ni2Al3 | T_grid=1010 OK |
| 1026 | 0.815 | L12+fccNi | L12+fccNi | T_grid=1030 OK |
| 1166 | 0.746 | L12 | B2+L12 | T_grid=1170 x |
| 1253 | 0.286 | Ni2Al3+liquid | Ni2Al3+NiAl3 | T_grid=1250 x |
| 1255 | 0.923 | fccNi | L12+fccNi | T_grid=1260 x |
| 1261 | 0.681 | B2+L12 | B2+L12 | T_grid=1260 OK |
| 1317 | 0.539 | B2 | B2 | T_grid=1320 OK |
| 1602 | 0.385 | B2+liquid | B2+liquid | T_grid=1600 OK |
| 1753 | 0.653 | B2+liquid | B2+L12 | T_grid=1750 x |
| 1811 | 0.187 | liquid | liquid | T_grid=1810 OK |

### 不変反応（ORCHID-Values, INVARIANT_TEMPERATURE）

| T_run (K) | kind | phases | x_run | n_exp | T_exp median (range) | dT_exp | n_model | T_model median | x_lit (exp, printed) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1130–1140 | reaction | NiAl3+fccAl+liquid | {"fccAl": 0.031, "NiAl3": 0.25, "liquid": 0.154} | 4 | 913 (913–913) | +222 | 7 | 915 | {"L": 0.027, "γ1": 0.25, "Al3Ni": 0.25, "fcc": 0.001} | matched |
| 1240–1250 | artefact | B2+B2 | {"B2": 0.497} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1250–1260 | reaction | B2+Ni2Al3+NiAl3 | {"NiAl3": 0.25, "Ni2Al3": 0.4, "B2": 0.471} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1270–1280 | artefact | B2+B2 | {"B2": 0.493} | 0 | - | - | 0 | - | - | same-phase segment appears/vanishes (fit noise), not compared |
| 1440–1450 | reaction | B2+NiAl3+liquid | {"liquid": 0.236, "NiAl3": 0.25, "B2": 0.471} | 0 | - | - | 0 | - | - | no literature record with this phase set |
| 1470–1480 | other | L12+fccNi | {"L12": 0.781, "fccNi": 0.994} | 0 | - | - | 0 | - | - | not compared |
| 1490–1500 | liquid_reaches | L12+liquid | {"L12": 0.781, "liquid": 0.953} | 0 | - | - | 0 | - | - | liquid first touches this solid here (no reaction identified), not compared |

文献にあって run に現れない不変反応（相集合, T_lit 中央値, n_exp/n_model, 相が全部モデルにあるか, T が格子内か）:

- NiAl3+fccNi+liquid: 913 K (1/1); represented=True; in_T_grid=False
- Al4Ni3+B2+Ni2Al3: 973 K (1/1); represented=False; in_T_grid=True
- Al3Ni5+B2+L12: 973 K (4/9); represented=False; in_T_grid=True
- Ni2Al3+NiAl3+liquid: 1127 K (7/8); represented=True; in_T_grid=True
- B2+Ni2Al3+liquid: 1406 K (7/8); represented=True; in_T_grid=True
- B2+L12+liquid: 1642 K (8/8); represented=True; in_T_grid=True
- L12+fccNi+liquid: 1645 K (8/8); represented=True; in_T_grid=True
- B2+liquid: 1915 K (6/8); represented=True; in_T_grid=True

