# Zhang ほか (2027) 汎用 MLIP 相図の精度と不確かさ定量 — 読書メモ（2026-11-11）

W. Zhang (NIMS ICYS), M. Forti, T. Hammerschmidt (ICAMS), J.-C. Crivello (CNRS-Saint-Gobain-NIMS), T. Koyama, T. Abe (NIMS),
"Accuracy and uncertainty quantification of phase diagrams calculated from universal machine learning interatomic potentials",
Scripta Materialia 289 (2027) 117663, doi:10.1016/j.scriptamat.2026.117663（受理 2026-11-02、公開 11-04；`papers/2027ScriptaMater_MLIP(Zhang).pdf`、
本文 5 ページ + 補足 S1–S5；データとノートブックは Zenodo 10.5281/zenodo.20918696）。

## 何をしたか

- 系: CPDDB（NIMS 計算状態図データベース）から 6 二元系。固溶体主体 Al–Zn・Mo–Rh、組成幅の広い金属間化合物 Re–W（σ、χ）・Cu–Pt（L1₁、L1₂）、線化合物 Cu–Mg・Ru–Si。温度域 400 K（Al–Zn）〜3000 K（Re–W）。
- 方法（Fig. 1）: 固相はすべて CALPHAD 枠組みで記述。固溶体は SQS（smol）、金属間化合物は CEF、自由エネルギー = 生成エンタルピー + 調和フォノン（phonopy）の振動エントロピー + 理想混合（Bragg–Williams）。DFT（VASP PBE）と各 UMLIP で同じ手順。**液相は CPDDB の評価の記述を借り、各モデルの固相自由エネルギーに合うよう液相線を再最適化**（液相を計算していない）。緩和は ASE（GoodOldQuasiNewton + FrechetCellFilter）、相図は pycalphad。
- UMLIP 8 種: GRACE（OMAT+SMAX、OAM、MP）、SevenNet-omni、NequIP（OAM、MP）、eSEN、ORB-v3。
- 評価指標: (1) 相ラベル分類精度（Hardcastle / Zhu らの指標）— 100 × 100 の (x, T) 格子で、平衡相の集合が実験評価と一致する点の割合。液相はモデルごとに液相線へ合わせているので事実上固相平衡の精度。(2) 分解エネルギー ΔF(T) = ΔH − TΔS（凸包または最近接の準安定分解に対する差）の DFT に対する RMSE。
- 不確かさ定量（UQ）: δH_MLIP→DFT ≈ 1 kJ/mol、δS ≈ 1 J/mol/K を DFT 固有誤差（同程度と仮定）と配置エントロピーのモデル誤差 1 J/mol/K に合成 → δH_MLIP = 1.41 kJ/mol、δS_MLIP = 1.73 J/mol/K。熱力学パラメータの分布から 1000 組を引いて相図を重ね描き（Ru–Si、eSEN、Fig. 4a）。ESPEI の MCMC で実験点 3 つ（1250・1550・1900 K）を取り込みベイズ更新（Fig. 4b）。

## 結果（Table 1、Fig. 2–4、Table 2）

| モデル | 分類精度（6 系平均、CPDDB 基準） | RMSE ΔH (kJ/mol) | RMSE ΔS (J/mol/K) |
|---|---|---|---|
| DFT | 0.784 | — | — |
| GRACE (OMAT+SMAX) | 0.805 | 0.957 | 0.826 |
| GRACE (OAM) | 0.794 | 1.034 | 1.000 |
| SevenNet-omni | 0.791 | 0.861 | 1.031 |
| NequIP (OAM) | 0.790 | 1.087 | 1.074 |
| eSEN | 0.711 | 0.923 | 0.984 |
| GRACE (MP) | 0.651 | 3.215 | 1.656 |
| ORB-v3 | 0.643 | 1.347 | 1.505 |
| NequIP (MP) | 0.494 | 3.740 | 1.488 |

- SOTA（OMAT/OAM/SMAX 学習）の UMLIP は ΔH の RMSE ≈ 1 kJ/mol（≈ 10 meV/atom）、ΔS ≈ 1 J/mol/K（≈ 0.12 k_B）で、分類精度は DFT（0.784）と同等。MPtrj だけで学習した世代（GRACE-MP、NequIP-MP）は 3 kJ/mol 超で明確に劣る。SMAX（非平衡構造を多く含む）学習の GRACE が ΔS で最良。
- DFT 自体の限界: Cu–Pt の L1₁ の組成幅と合致温度を過小評価、W–Re の σ の自由エネルギーを過大評価、Al–Zn の fcc ミシビリティギャップの臨界温度を大きく過小評価、Mo–Rh の fcc/hcp 境界を再現しない（fcc の振動エントロピーが大きい）、Ru₂Si（高温相）は DFT でも UMLIP でも出ない。UMLIP はこれを引き継いだ上で ML 誤差が乗る。
- 質的な失敗例: GRACE・eSEN・SevenNet は Cu–Mg の Mg 側に fcc 固溶体を出す。eSEN は fcc Mg を hcp Mg より 0.116 kJ/mol 安定と予測（元素基底状態の誤り）。「小さな自由エネルギー誤差が質的な違いを生む」例。
- 0 K 凸包（補足 S3、Alexandria の構造集合）では新しい安定相は出ず、相の集合を変える必要はなかった。
- 誤差伝播（Table 2）: |ΔH| = 1 kJ/mol の化合物が安定である確率は 0.54、2.5 kJ/mol で 0.78、5 kJ/mol で 0.95。エントロピー安定化の転移温度 T_c = 1000 K の誤差 δT は |ΔH| = 1 / 2.5 / 5 / 10 kJ/mol で 2236 / 894 / 447 / 223 K。組成幅 0.1 の金属間化合物の幅の誤差は |ΔH| = 2.5 kJ/mol で 0.09。
- UQ の効用（Ru–Si）: eSEN の点推定では Ru₄Si₃・RuSi・Ru₂Si₃ だけが安定だが、1000 サンプルの重ね描きでは実験で存在する高温相 Ru₂Si が誤差内で安定になり得る（Ru₅Si₃ も出るがこれは実在しない）。実験点 3 つのベイズ更新で Ru₂Si が高確率の高温相になり Ru₅Si₃ は消える。DFT では Ru₂Si は安定にならないので、「UQ 付き UMLIP + 少数の実験点」は DFT より良い相図を与え得る。
- 限界（著者自身）: 二元系のみ、調和フォノン、Bragg–Williams の配置エントロピー。fine-tuning、多元系、より高度な有限温度自由エネルギー（文献 52–55: フォノン fine-tuning、calphy、格子 MC）が今後の課題。

## 本プロジェクト（ftphase）との対応

| 項目 | Zhang 2027 | ftphase（本プロジェクト） |
|---|---|---|
| 固相の有限温度 | 調和フォノン（0 K 体積、QHA でない）+ Bragg–Williams | QHA（phonopy）、または 2,000 原子以上の calphy 固相 TI（非調和込み）；理想混合・副格子・Wagner–Schottky・CE+MC |
| 液相 | 計算せず、CPDDB 評価の液相を各モデルの固相に合わせて再最適化 | calphy の UFM 熱力学積分（組成ごと・温度掃引、MLIP から直接）|
| 相図の求め方 | CALPHAD パラメータに当てはめ → pycalphad | 自由エネルギー表の下側凸包（補間なし）；CALPHAD 化は任意（工程 05 の TDB、Pt–Rh の Saengdeejing 経路）|
| 比較基準 | CPDDB の評価（相ラベル分類精度、100 × 100 格子） | ORCHID の文献不変反応（温度差）と SGTE 評価境界の重ね描き（図 8）|
| 誤差の扱い | δH・δS を仮定してパラメータ分布からサンプリング（UQ）、ESPEI でベイズ更新 | 工程 07 の Monte Carlo 誤差伝播（自由エネルギーの σ から二相境界の幅）、run 間 seed 差；UQ としての体系化は未 |
| MLIP | GRACE SMAX/OAM/MP、SevenNet-omni、NequIP OAM/MP、eSEN、ORB-v3 | ACE、GRACE-FS/1L/2L、SevenNet-0/MF-ompa、MACE-MPA-0、MatterSim 1M/5M、NequIP-OAM-M/S、DPA4-Plus、（DPA-4.1-Air 実行中）|
| 系 | Al–Zn、Mo–Rh、Re–W、Cu–Pt、Cu–Mg、Ru–Si | Al–Li、Ni–Al、Ag–Cu、Pt–Rh |

読み取れること:

1. **本プロジェクトの観測と整合する。** 「SOTA UMLIP の ΔH 誤差 ≈ 1 kJ/mol（10 meV/atom）」は、Al–Li の 0 K 生成エネルギーが MLIP 間でほぼ一致した観測と同じ。一方で本プロジェクトは共晶温度が ±150 K 散らばり、差の源が固相の振動と液相だと特定した。Zhang らは液相を実験評価から借りているので液相誤差は見えず、ΔS の RMSE 1 J/mol/K（0.12 k_B）は本プロジェクトの fcc Al の S(300 K) の MLIP 間差（1.5 k_B、GRACE-FS・SevenNet-0・NequIP-OAM-S の軟いフォノン）より一桁小さい。これは Zhang らの指標が「DFT の分解に対する ΔS」で、純元素端成分のフォノンの誤差は分解エネルギーから大部分相殺されるため。純元素の融点を決める絶対的な振動エントロピーの誤差は、この論文の RMSE には現れない。
2. **液相を借りると融点・共晶は評価できない。** 本プロジェクトの Al–Li 共晶 −150〜+60 K、Pt 融点 −550 K のような差は、液相を MLIP から計算して初めて見える。Zhang らの精度 0.8 は「液相線を合わせた後の固相平衡」の指標で、ORCHID の不変反応温度差とは測っているものが違う。
3. **誤差伝播の表（Table 2）は本プロジェクトの数値の裏付け。** T_c = 1000 K・|ΔH| = 2.5 kJ/mol（26 meV/atom）で δT ≈ 900 K、という桁は、Pt–Rh の規則化エネルギー 5–11 meV/atom が経路間で ±35 K・MLIP 間で「出る／出ない」に分かれたことと同じ構造。本プロジェクトの Al₃Li（準安定、0 K で凸包上かその近く）が MLIP によって 300–500 K まで出たり出なかったりするのも、|ΔH| ≈ 1 kJ/mol 級の相の「安定確率 0.54」そのもの。
4. **取り込めるもの。** (a) 相ラベル分類精度（100 × 100 格子）は ORCHID 照合の補助指標として `orchid_compare.py` / `sgte_diagrams.py` に実装できる（SGTE 評価の境界 JSON から各格子点の相集合を取れば計算可能）。(b) UQ: 工程 07 の Monte Carlo 誤差伝播は自由エネルギーの σ を使うが、Zhang らのように「MLIP → DFT の系統誤差 1 kJ/mol・1 J/mol/K」を事前分布として足し、安定確率の地図を描く形にすると、図 8 の「出たり出なかったりする相」を確率で示せる。(c) ESPEI によるベイズ更新は経路 2（`espei_alli/`）で試した手順と同じ。(d) 比較に加える価値のある MLIP: GRACE (OMAT+SMAX)、SevenNet-omni、eSEN。
5. **CPDDB** は NIMS の計算状態図データベース（doi:10.48505/NIMS.3060）で、ORCHID の SGTE 評価と同じ役割（評価済み TDB の集まり）。Al–Li・Ni–Al・Ag–Cu の評価があるなら本プロジェクトの第 2 の基準に使える。
