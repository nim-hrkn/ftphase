# Pt–Rh を汎用 MLIP で（工程 01–07、2026-11-04 開始）

目的: Saengdeejing ほか, npj Comput. Mater. 12, 362 (2026)（Matlantis PFP と DFT から Thermo-Calc で組んだ Pt–Rh の TDB、
`papers/s41524-026-02212-9.pdf`、比較メモ `../orchid_calphad/npj_ptrh/COMPARISON.md`）の表 7（規則化温度）と図 11（液相込みの相図）を、
本プロジェクトの経路（QHA/TI 固相 + calphy 液相 TI + 凸包）で、手元の汎用 MLIP について再現・比較する。

## 系の定義（`aiida_txdiagram/run_aiida.py --system ptrh --mlip <name>`）

- 候補構造: fcc Pt (a 3.924)、fcc Rh (3.803)、PtRh「40」(NbP 型, I4₁/amd, tI8; 論文 Table 1 の PtRh-I4₁/amd)、PtRh₃ D0₂₂ (I4/mmm)、Pt₃Rh D0₂₂（反構造）。pymatgen `Structure.from_spacegroup` で生成。
- 固相: fcc 固溶体 0 ≤ x_Rh ≤ 1 の 13 組成 × 乱数 2 配置（32 原子、phonopy 2×2×2 = 256 原子、メッシュ 60 Å）；規則相 3 つは 2×2×1（32 原子）の反サイト欠陥セル（±1〜3 個）で組成幅を持たせ、組立では副格子の解析エントロピー（`b32_antisite`、`@0.75`、`@0.25`）+ 枝ごとの線形欠陥エネルギー（`entropy_models`）。論文の CEF 2 副格子・理想副格子混合と同じ近似（短距離秩序なし）。
- 液相: 256 原子、x_Rh = 0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0、calphy ts 2500 → 1900 K（Rh 側は 2000/2100 K 止め）、UFM、10k + 10k×3 反復。
- QHA: 0–2400 K、スケール 0.96–1.12。組立: 100–2400 K、10 K 刻み、古典水準（QHA を F_q − F_cl で下げる）。
- 制約: (1) 規則化反応は 146–258 K（論文）で、組立は古典水準なので量子（調和）水準での再組立が要る（04B の補正は QHA ノードから後計算できる）。(2) 融点付近は QHA が過安定化するので、終わったら `mlip_solids_ti.py` で 2,000 原子の固相 TI（Pt 2041 K、Rh 2237 K の端セル）を足す。(3) 規則相の温度は Bragg–Williams 型近似で、CE+MC（`ftphase.ce`、Ag–Cu で実行済み）が短距離秩序込みの対照になる。

## 0 K スクリーニング（`screen_0K.py`、CPU、2026-11-04）

生成エネルギー（meV/atom、緩和後、fcc 端成分基準）。論文 Table 2 の PFP / DFT と比較。

| 構造 | PFP (論文) | DFT (論文) | GRACE-2L† | MACE-MPA-0 | SevenNet-MF-ompa | SevenNet-0 | MatterSim-5M | MatterSim-1M |
|---|---|---|---|---|---|---|---|---|
| PtRh 40 (I4₁/amd) | −37.6 | −23.6 | −31.6 | −26.8 | −31.2 | −30.3 | −19.5 | −8.2 |
| PtRh₃ D0₂₂ | −28.0 | −20.0 | −25.3 | −19.7 | −23.6 | −19.6 | −21.9 | −11.7 |
| Pt₃Rh D0₂₂ | −23.5 | −20.0 | −21.0 | −16.6 | −18.5 | −26.0 | −10.4 | −7.9 |
| PtRh₃ L1₂ (Pm-3m) | −27.0 | −15.6 | — | −17.8 | −19.1 | −18.8 | −21.5 | −13.5 |
| Pt₃Rh L1₂ (Pm-3m) | −19.7 | −9.0 | — | −12.1 | −13.8 | −22.3 | −8.7 | −8.9 |
| PtRh L1₀ (P4/mmm) | — | — | — | −18.6 | −21.5 | −26.7 | −17.7 | −11.5 |

† GRACE-2L は AiiDA の smoke run（pk 8702、工程 01、fp32 GPU）の値。PFP は DFT より 10–14 meV/atom 負に寄る（論文 p. 2 の指摘どおり）のに対し、MACE-MPA-0・GRACE-2L・SevenNet-MF-ompa は DFT の 0〜8 meV 内で、PtRh 40 > PtRh₃ D0₂₂ > Pt₃Rh の順序も DFT と同じ。MatterSim-1M は秩序化エネルギーが 1/3 で、SevenNet-0 は Pt₃Rh を最も安定にする。Pt₃Rh D0₂₂ は GRACE-2L でも凸包上（PFP と同じ、DFT ではわずかに上）。

## 実行記録

| run | MLIP | 計算機 | pk | 状態 |
|---|---|---|---|---|
| ptrh_grace_2l_smoke | GRACE-2L-OMAT fp32 | mygarden6 | 8702 → 8858 | 8702 は計算 7 本成功・組立のみ失敗（液相 2 組成では組立格子が空）。spec を液相 3 組成に直した 8858 が 11-05 01:19 に Finished [0]（T 格子 2200–2400 K） |
| ptrh_nequip_oam_m_smoke | NequIP-OAM-M | mygarden6 | 8750 → 8929 | 8750 は同じ組立失敗、8929 を自動再投入（11-04 21:45） |
| ptrh_mace_mpa_0_smoke | MACE-MPA-0 cueq | mygarden6 / QHA mygardenx2 | 8764 → 9006 | 同上（11-04 23:31） |
| ptrh_grace_2l | GRACE-2L-OMAT fp32 | mygarden6 | 9105 | 本番、11-05 01:21 自動投入（fcc 26 + 規則相 16 セルの QHA、液相 7 本） |

`autosubmit.sh`（切り離して常駐）が smoke の終了を 2 分ごとに見て、組立失敗なら修正 spec で smoke を再投入、exit 0 なら本番を投入する。ログ `out/autosubmit.log`。

mygarden5 の GPU は Stage-2 の固相 TI ジョブが 20 本待ちなので、Pt–Rh は mygarden6 で回す。mygarden6 には ML-IAP（`env/lammps-gpu-mliap`、env/torch の cupy・nequip・mattersim、env/mace の cuequivariance、potentials/nequip）が無かったので rsync で配備中（2026-11-04）。
