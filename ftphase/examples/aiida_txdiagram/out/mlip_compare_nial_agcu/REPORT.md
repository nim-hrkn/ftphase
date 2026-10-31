# Ni–Al / Ag–Cu: EAM vs 3 MLIPs (2026-10-31)

固相 QHA のみ（固相 TI なし）、液相 calphy TI、0 GPa。図: `panels.png`（上段 Ni–Al, 下段 Ag–Cu; 左端が EAM 基準 = 図4/図5）。
WorkChain pk: nial_grace_fs 4784, nial_grace_1l 4798, nial_sevenn_0 4813, agcu_grace_fs 4869, agcu_grace_1l 4900, agcu_sevenn_0 4928（全て Finished [0]）。

## 純物質・B2 の固液交点（05 表の G 交点, K）

| | 実験 | EAM (TI) | GRACE-FS-OAM | GRACE-1L fp32 | SevenNet-0 |
|---|---|---|---|---|---|
| Al | 933 | 1040 | > 2000 | 870 | > 2000 |
| Ni | 1728 | 1703 | 1751 | 1694 | < 1500 |
| B2 NiAl | 1911 | 1808 | > 2000 | > 2000 | > 2000 |
| Ag | 1235 | 1278 | 判定不可 (QHA 固相が 1050 K で切れる) | 1093 | 判定不可 (固相 950 K まで) |
| Cu | 1358 | 1326 | 1345 | 1347 | 液相なし |

## 何が起きたか

* GRACE-FS / SevenNet-0 の fcc Al: 1000 K で S_solid (9.35 / 9.21 k_B) が S_liquid (9.06 / 8.80 k_B) を上回る。融解エントロピーが負なので Al は融けない。Al–Li で見た「fcc フォノンが軟らかすぎて固相を過剰安定化」と同じ。GRACE-1L は ΔS_m = 1.45 k_B で正常。
* B2 NiAl は 3 MLIP とも 2000 K まで融けない（QHA のみ。EAM でも QHA は T_m 近傍で 20–45 meV/atom 高すぎた。ここは逆向きで、QHA の非調和誤差だけでは説明できない大きさ: ΔG(2000 K) = +6..+118 meV）。固相 TI なしでは B2 側の結論は出せない。
* Ag–Cu: Cu の融点は FS / 1L とも 1345–1347 K で実験・EAM と合う。Ag 側は QHA の固相が 950–1050 K で不安定化（体積発散）して表が切れ、融点が出ない（1L だけ 1250 K まで残り 1093 K = 実験 −140 K）。共晶は 3 MLIP とも再現しない。
* GRACE-FS Ag–Cu の liquid+liquid 帯 (1110–1320 K) は液相フィットの偽物（x 0.2–0.6）。
* 失敗: nial_grace_1l の液相 x=0.90 が SolidifiedError（pk 5039）。agcu_sevenn_0 の液相 x=0.6, 0.8, 1.0 は `nedges exceeded nedges_upper_bound (pair_e3gnn.cpp:163)` で落ち、x=0.5 も無い → Cu 側に液相なし。
* B2+B2 の細い帯（1L, SevenNet-0）は欠陥系列のフィット雑音。

## 結論

QHA のみの固相では、Al–Li で既に見えた MLIP のフォノン軟化がそのまま融点に出て、Ni–Al / Ag–Cu の相図は EAM 基準（図4/5）とは比べられる形にならない。比較を成立させるには (1) 固相を 2000 原子以上の calphy TI にする（`solids_ti`）、(2) SevenNet-0 の e3gnn `nedges_upper_bound` を上げるか ML-IAP 経路（`mliap unified`）に移す、(3) Ag–Cu の液相掃引を 900 K 付近まで下げる、が必要。

## 段階 1: 融点セルの固相 TI（2026-10-31〜11-01, `mlip_solids_ti.py`）

利用者の判断（2026-10-31）: 全セルの TI は 3〜4 日かかるため、先に純物質と化学量論セル（fcc Al, fcc Ni, B2, L1_2, fcc Ag, fcc Cu）だけ、2048 原子（B2 3456 原子）の calphy ts で TI。液相は元の WorkChain の calphy 液相（Ni–Al の x=0 だけは同じ MLIP の Al–Li 実行の純 Al 液相を 700 K まで併用: 両者の差 0.6 meV/atom 以下。L1_2 は x=0.7 と 0.8 の液相を x で線形補間）。数値は `melting_ti.tsv`。

| 融点 (K) | 実験 | EAM (TI) | GRACE-FS | GRACE-1L | SevenNet-0 |
|---|---|---|---|---|---|
| Al | 933 | 1040 | ~630（外挿; 液相のある 700–780 K では液相の G が常に低い） | 874 | 784 |
| Ni | 1728 | 1703 | 1654 | 1715 | ~1460（外挿; 液相は 1500 K まで） |
| B2 NiAl | 1911 | 1808 | 1670 | 1797 | 1964 |
| L1_2 Ni3Al (液相 x=0.75 との交点; 実際は包晶) | 1645 | ~1631 | 1512 | 1615 | 1567 |
| Ag | 1235 | 1278 | ~930（外挿; 液相は 1050 K まで） | ~990（外挿） | ~950（外挿） |
| Cu | 1358 | 1326 | 1190 | 1310 | 1182 |

QHA − TI（掃引の中点, meV/atom）: B2 は −37 (FS) / −17 (1L) / −88 (S0)、SevenNet-0 fcc Al −53、それ以外は −12〜+2（Ni の S0 だけ +24）。QHA だけの段階で出た「Al・B2 が 2000 K でも融けない」は QHA 固相の過安定化で、TI では消える。

* GRACE-1L が全体に最も実験に近い（Al −59, Ni −13, B2 −114, Cu −48 K; Ag は約 −245 K）。
* GRACE-FS は全体に 70〜300 K 低い（Al は約 −300 K）。fcc Al は 920 K、860 K と 2 回、掃引の途中で fcc でなくなった（860 K の掃引では体積の跳びがなく連続に膨張しており、格子が力学的に不安定になっている）。
* SevenNet-0 は元素ごとにばらつく（Al −149, Ni 約 −270, Cu −176 K、B2 だけ +53 K）。
* Ag は 3 MLIP とも 930〜990 K（実験 1235 K）。液相を 1050 K までしか計算していないので外挿値。

### 途中の失敗と直したこと

* 掃引の上限を 1.2 T_m(実験) にした初回（pk 6503-6595）は GRACE-FS fcc Al が約 1000 K で融けて MeltedError → 1.05 T_m に下げて再投入（pk 6613-6702）。それでも融けたセル（GRACE-FS Al 920→860→780 K, GRACE-FS / SevenNet-0 Ag 1250→1150 K）は個別に上限を下げた。
* SevenNet-0 の Cu 固相 TI と Ag–Cu の Cu 側液相（x ≥ 0.5）は `nedges exceeded nedges_upper_bound`（pair_e3gnn.cpp:163）で落ちた。SevenNet の LAMMPS pair style の不具合（前のステップの辺数 × 1.2 で配列を確保し、上限を上げる前にエラーにする; fcc Cu を加熱するとカットオフのすぐ外の殻が内側に入り 20 % 以上増える）。`env/patches/sevenn-0.13-pair_e3gnn-nedges-bound.patch` で全近接リスト長を上限にし、配列をヒープに移した（2048 原子 Cu 1400 K NVT でエネルギー・圧力は旧版と一致）。直した `lmp_sevenn` で液相 4 本（pk 6769-6772）と Cu 固相 TI（pk 6786）は全て通った。
* 停止した CalcJob 6726 の kill が AiiDA の投入の再試行と重なり、Slurm ジョブが 5 本残った（aiida_zombies.py では見つからない: ノードに job id が記録されていない）。job id を指定して取り消した。

### TI を入れた相図（`panels_ti.png`, `out/<name>_ti/`）

端のセルだけ TI、合金セルは QHA のままなので、一つの相の中で TI と QHA が混ざり、相図としては使えない（参考図）。Ag–Cu は Ag の融点が液相の最低温度（1050 K）より下にあるため、液相の掃引を 850 K 付近まで下げないと共晶が出ない。

### 次の段階（未実行）

相図を描き直すには: (1) 合金セル全部の TI（Ni–Al 17 セル、Ag–Cu 11 セル（1 配置）、3 MLIP で約 85 本、GPU 2 枚で約 3 日）、(2) Ag–Cu の液相を 850 K まで（7 組成 × 3 MLIP）。GRACE-1L だけに絞れば約 1 日。
