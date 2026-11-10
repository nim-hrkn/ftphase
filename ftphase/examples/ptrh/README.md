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
| ptrh_grace_2l | GRACE-2L-OMAT fp32 | mygarden6 | 9105 | 本番、11-05 01:21 自動投入 → 11-05 17:32 Finished [0]（52 本すべて成功）、`aiida_txdiagram/out/ptrh_grace_2l/` |
| ptrh_nequip_oam_m | NequIP-OAM-M | mygarden6 | 9348 | 本番、11-05 02:07 自動投入 → Finished [0]、`out/ptrh_nequip_oam_m/` |
| ptrh_mace_mpa_0 | MACE-MPA-0 cueq | mygarden6 / QHA mygardenx2 | 9585 | 本番、11-05 02:50 自動投入 → 11-06 Finished [0]、`out/ptrh_mace_mpa_0/` |
| ptrh_sevenn_mf_ompa | SevenNet-MF-ompa | mygarden6 / QHA mygardenx2 | 10674 (smoke) → 10792 | 本番 11-06 22:28 自動投入 → 11-08 Finished [0]、`out/ptrh_sevenn_mf_ompa/`（Pt 2400+ K、規則相なし 1910–2400 K；lowT: PtRh 270 K、Pt₃Rh 490 K、PtRh₃ 860 K；AiiDA の乱雑セルでは PtRh の規則化エネルギー −2 meV と浅く、CPU スクリーン −10.6・CE −7.1 とばらつく＝32 原子乱雑セルの SRO ノイズ ±5 meV） |
| ptrh_*_solid_ti | 3 MLIP | mygarden6 / MACE QHA x2 | 11345 / 11358 / 11372 | 固相だけ + 端成分 TI の WorkChain（11-08 投入 → 11-08 全部 Finished [0]、`out/ptrh_<mlip>_solid_ti/`、組立 100–2400 K・231 点）。Pt 端の TI（1700→2150 K）は 3 つとも後退掃引で融けて exit 320：Pt の MLIP 融点は 2150 K より下。上限 1980 K で単独再投入（`mlip_solids_ti.py submit --only s00_fcc --T-hi s00_fcc=1980`、pk 12349/12354/12359、11-08）。Rh 端（1900→2350 K）は実行中 |

`autosubmit.sh`（切り離して常駐）が smoke の終了を 2 分ごとに見て、組立失敗なら修正 spec で smoke を再投入、exit 0 なら本番を投入する。ログ `out/autosubmit.log`。

mygarden5 の GPU は Stage-2 の固相 TI ジョブが 20 本待ちなので、Pt–Rh は mygarden6 で回す。mygarden6 には ML-IAP（`env/lammps-gpu-mliap`、env/torch の cupy・nequip・mattersim、env/mace の cuequivariance、potentials/nequip）が無かったので rsync で配備中（2026-11-04）。

## 結果 1: 0 K の規則化エネルギー（`screen_0K.py` の乱雑セル追加版、2026-11-06）

E(規則相) − E(乱雑 fcc、同じ組成、32 原子乱数 2 配置の平均)、meV/atom。これが T > 0 で規則相が存在するかを決める量。
論文の値は Table 2 の ΔH_f と fcc の ⁰L（x(1−x)·L0 を乱雑の混合エンタルピーとみなす）から出した概算。

| 相 | 論文 PFP | 論文 DFT | MACE-MPA-0 | SevenNet-MF-ompa | SevenNet-0 | MatterSim-5M | MatterSim-1M | GRACE-2L (AiiDA) | NequIP-OAM-M (AiiDA) |
|---|---|---|---|---|---|---|---|---|---|
| PtRh 40 (x 0.5) | ≈ −15 | ≈ −11 | −11.7 | −10.6 | −16.5 | −3.1 | −12.5 | +0.9 | 0.0 |
| PtRh₃ D0₂₂ (0.75) | ≈ −11 | ≈ −10 | −5.7 | −5.1 | −3.8 | −4.2 | −8.8 | +0.3 | +1.5 |
| Pt₃Rh D0₂₂ (0.25) | ≈ −7 | ≈ −10 | −5.5 | −5.3 | −18.8 | −1.2 | −10.8 | −0.6 | −3.6 |
| 乱雑 fcc の ΔH_mix(0.5) | −23 | −13 | −15 | −21 | −14 | −16 | +4 | −32 | −29 |

- MACE-MPA-0 と SevenNet-MF-ompa は規則化エネルギーが DFT と同程度（PtRh −11、A₃B 型 −5）。Bragg–Williams 型の目安 T_c ≈ ΔE/(k_B ΔS_conf)（ΔS = 0.69 k_B at x 0.5、0.56 k_B at 0.75）では PtRh ≈ 180–200 K、PtRh₃/Pt₃Rh ≈ 100–120 K で、論文の表 7（PFP −15 °C = 258 K、DFT −63 °C = 210 K；PtRh₃ 235 / 156 K）と同じ桁。PFP の −15 meV に同じ目安を当てると 250 K で、論文の 258 K と一致する。
- **GRACE-2L と NequIP-OAM-M は規則化エネルギーが 0 ± 2 meV**。乱雑 fcc の混合エンタルピーが −30 meV と過大で、規則相と同じ深さにある。したがってこの 2 つでは T > 0 の規則相は原理的に出ず、工程 07 に規則相が現れるのは反サイト欠陥セル（32 原子に 1〜3 個）の配置ノイズ（数 meV）を線形 fit した結果で、物理ではない。
- MatterSim-5M は規則化が弱すぎ（−1〜−4）、MatterSim-1M は乱雑 fcc の混合が正で規則相だけ負という、論文 Fig. 7 の DFT と逆の傾向。SevenNet-0 は Pt₃Rh を最も安定にする（DFT では準安定）。

## 結果 2: 工程 07 の組立（GRACE-2L、NequIP-OAM-M）

- WorkChain の組立は液相 3 組成以上ある温度しか格子に入れないので、出力は 1910–2400 K だけ（`out/ptrh_grace_2l/REPORT.md`）。GRACE-2L: Pt 融点括弧 2400–2410 K（実験 2041）、Rh は 2400 K まで融けない、fcc+液相の二相域の幅は x 0.26（SGTE 評価は最大 0.037）。NequIP-OAM-M: Pt 2300–2310 K、fcc+液相 0.17。QHA 固相の過安定化（Al–Li・Ni–Al と同じ）で、融点側は 2,000 原子の固相 TI を足すまで比較にならない。
- 低温側は `assemble_lowT.py`（固相のみ、100–1900 K、同じ fit と副格子エントロピー）で再組立した（`out/<run>/lowT/`）。GRACE-2L: PtRh は 240 K まで、Pt₃Rh 630 K、PtRh₃ 920 K（さらに 1690 K 以上に再出現）；NequIP: PtRh 200 K、PtRh₃ 1180 K、Pt₃Rh 1900 K まで、fcc+fcc の広い二相分離。結果 1 のとおり規則化エネルギーが 0 の MLIP なので、これらはすべて fit ノイズ。規則相が CEF 近似で生き残る温度は論文と同じ 200 K 前後になるはずで、MACE-MPA-0（本番待ち）で再評価する。

## 論文の表 7 との比較で言えること（暫定）

1. 汎用 MLIP で Pt–Rh の規則相を扱えるかは、0 K の生成エネルギー（結果 0: DFT と 0–8 meV）ではなく、**規則相と乱雑配置の差（5–15 meV）** を再現できるかで決まる。MACE-MPA-0・SevenNet-MF-ompa は再現し、GRACE-2L・NequIP-OAM-M・MatterSim は再現しない。Al–Li で振動・液相が差を生んだのと別の、0 K の配置エネルギーの精度の問題。
2. 論文の PFP は乱雑も規則相も DFT より負に寄るが差は保っており、PFP 版 TDB の規則化温度が DFT 版より 50 K 高いのはその差（−15 vs −11 meV）に対応する。
3. 本プロジェクトの規則相の扱い（欠陥セル + 副格子エントロピー、論文の CEF と同等）は、規則化エネルギーが配置ノイズ（~5 meV）を下回る MLIP では使えない。その場合は CE+MC（`ftphase.ce`）で ECI を直接評価する方が筋がよい。
4. 融点側（図 11）は固相 TI が要る。液相 TI 自体は 7 組成とも完走（GRACE-2L・NequIP）。

## 結果 3: MACE-MPA-0 の低温組立と論文の表 7（2026-11-06）

AiiDA の fcc 乱雑セル基準の規則化エネルギー（0 K）: PtRh 40 −7.0、PtRh₃ D0₂₂ −1.0、Pt₃Rh D0₂₂ −4.2 meV/atom（CPU スクリーンの別 seed では −11.7 / −5.7 / −5.5；乱雑セル 2 配置の差がそのまま効く）。
`assemble_lowT.py`（固相のみ、古典 QHA、CEF 型副格子エントロピー）の結果（`out/ptrh_mace_mpa_0/lowT/`）:

| 反応 | 論文 PFP（表 7） | 論文 DFT | MACE-MPA-0（本研究） | GRACE-2L / NequIP-OAM-M |
|---|---|---|---|---|
| fcc ↔ PtRh（規則化） | −15 °C = 258 K | −63 °C = 210 K | PtRh が二相域から消える 230–240 K | 240 K / 200 K（規則化エネルギー 0 なのでノイズ） |
| fcc ↔ PtRh₃ | −38 °C = 235 K | −117 °C = 156 K | 910 K まで残るが組成 0.81 の欠陥セル側（ノイズ） | 920 / 1180 K（ノイズ） |
| fcc ↔ Pt₃Rh | −127 °C = 146 K | 不安定 | 390 K | 630 / 1900 K（ノイズ） |
| 共析 fcc ↔ PtRh + PtRh₃ | −62 °C (x 0.65) | −124 °C (0.69) | 150 K で PtRh(0.56)+PtRh₃(0.81) の二相域、200 K 以上で消える | — |

- PtRh「40」の規則化温度 230–240 K は論文の PFP 258 K・DFT 210 K の間に入る。規則化エネルギー −7 meV と ΔS_conf = 0.69 k_B の Bragg–Williams の目安（≈ 120 K）より高いのは、乱雑 fcc の RK fit が x = 0.5 付近で乱雑セルの実エネルギーより上にあるため。配置ノイズ（±3 meV）が温度に ±50 K で効く精度。
- PtRh₃ と Pt₃Rh は規則化エネルギーが 1–4 meV でノイズと同程度。PtRh₃ が 910 K まで残るのは化学量論セルより欠陥セル（x 0.66–0.72）の方が 6–8 meV 低いためで、32 原子セルでの D0₂₂ の基底状態が怪しい（MACE では D0₂₂ と乱雑の差が無い）。論文側でも PtRh₃ の DFT 値は PFP より 80 K 低く、この相は一番不確かな所。
- 540 K 以上の fcc+fcc（x 0–0.35）は fcc の RK fit の人工物（x 0.125 と 0.25 の乱雑セルが −11.5 / −12.7 meV で平坦）。SGTE 評価も論文もギャップ無し。
- 融点側（図 11 相当）: MACE の工程 07 は Pt 2400–2410 K、fcc+液相幅 0.21 で、GRACE-2L・NequIP と同じく QHA 固相の過安定化。固相 TI 待ち。

結論: 汎用 MLIP のうち MACE-MPA-0（と 0 K スクリーンの SevenNet-MF-ompa）は PtRh の規則化温度を論文と同じ 200–260 K に置くが、A₃B 型の 2 相は規則化エネルギーが配置ノイズ以下で決まらない。GRACE-2L・NequIP-OAM-M は規則化を再現しない。論文の「MLIP と DFT で同程度」という結論は PFP には当てはまるが、汎用 MLIP 一般には成り立たず、どのモデルを使うかで規則相の有無そのものが変わる。

## 結果 4: 量子（調和）水準での低温再組立（2026-11-06）

`assemble_lowT.py --quantum` は AiiDA の QHA ノードから古典化前の自由エネルギー（零点振動 + Bose–Einstein）を取って同じ組立を行う（`out/<run>/lowT_quantum/`）。
規則相が二相域から消える温度は古典水準と同じ（MACE: PtRh 230 K、Pt₃Rh 390 K、PtRh₃ 910 K；GRACE-2L: 240 / 630 / 1900 K；NequIP: 200 / 1900 / 1180 K）。
規則相と乱雑 fcc のフォノンがほぼ同じなので 04B の補正は相間で打ち消し、規則化温度には効かない。論文の Fig. 4–5（PtRh の F_vib の MLIP–DFT 差 5.5 meV/atom at 1000 K）も生成自由エネルギーには数 meV しか残らないことと整合する。

## 結果 5: CE + 正準 MC の規則化温度（2026-11-07、`ce_mc.py`、`out_ce_<mlip>/`）

icet で fcc 配置 631 個（1–8 原子）を列挙し、MLIP 環境のサブプロセスで緩和（位置 + セル）、CE は最小二乗・カットオフ 9/6/5 Å・41 ECI（CV 0.7 / 0.5 meV/atom；ARDR は 3 ECI・CV 4 meV で規則化を表せず転移が出なかった）。
正準 MC は 8³ の慣用 fcc セル（2,048 サイト）を 500 → 20 K に冷却、各温度 40 + 80 スイープ、C_v = Var(E)/(k_B T²) のピークを T_c とする。短距離秩序込みで、WorkChain の CEF 型（理想副格子混合）近似より低い値になるのが普通。

| 反応 | 論文 PFP | 論文 DFT | Pohl & Albe MC | MACE-MPA-0 CE+MC | SevenNet-MF-ompa CE+MC | MACE CEF 型（結果 3） |
|---|---|---|---|---|---|---|
| fcc ↔ PtRh (x 0.5) | 258 K | 210 K | 238 K | 160 K（C_v 1.7 k_B） | 180 K（C_v 9 k_B、一次転移的） | 230 K |
| fcc ↔ PtRh₃ (0.75) | 235 K | 156 K | — | 140 K | 120 K | 決まらず |
| fcc ↔ Pt₃Rh (0.25) | 146 K | 不安定 | — | 100 K（弱い） | 120 K（弱い） | 390 K（ノイズ） |

CE の 0 K 規則化エネルギー（規則相 − CE 乱雑）: MACE −4.2 / −7.4 / −6.5、SevenNet-MF −5.2 / −7.1 / −6.2 meV/atom（Pt₃Rh / PtRh / PtRh₃）。
読み: (1) 両 MLIP とも PtRh の規則化は 160–180 K で、論文の DFT-CEF 値 210 K・PFP 258 K より 30–100 K 低い。規則化エネルギーが DFT の −11 より 3–4 meV 浅いことと、CEF（Bragg–Williams）が MC より T_c を高く見積もること（MACE 同士で CEF 230 K vs MC 160 K、+70 K）の両方が効く。文献 MC（Pohl & Albe、別の bond-order ポテンシャル）238 K との差も主に規則化エネルギーの差。(2) A₃B 型は欠陥セル法では決まらなかったが CE+MC では 120–140 K に明瞭なピークが出る。配置ノイズの無い ECI ベースの方法が、規則化エネルギー 5 meV 級の系では唯一の実用的な経路。(3) これは AiiDA 外の計算（ローカル CPU、約 1 時間 + MC 35 分/MLIP）。

## 進行中（2026-11-10 時点: なし。Pt–Rh の計算はすべて終了）

- 融点側 + 固相だけの組立を WorkChain 内で: `run_aiida.py --system ptrh --mlip <m> --computer mygarden6 --solid-only --ends-ti`（11-07/08 に実装: `assemble.allow_solid_only` で液相の無い温度も固相だけの凸包として格子に残す、`solids_ti` に `x` / `keys` / `one_per_x` の絞り込み、`skip_liquids`）。単独投入していた端成分 TI 6 本は kill して WorkChain に戻した。smoke pk 11014 で組立経路を確認（TI の smoke は 256 原子・1900 K で融けて exit 310、本番は 2,048 原子・1700 K 開始）。本番: MACE pk 11345、GRACE-2L 11358、NequIP 11372（`ptrh_<mlip>_solid_ti`、組立 100–2400 K）。工程 01 の緩和が前回と僅かに違う構造を返したため QHA はキャッシュに当たらず再計算（MACE は mygardenx2 の CPU、他は mygarden6 の GPU）。
- 規則化温度（短距離秩序込み）: `ce_mc.py --mlip mace-mpa-0|sevenn-mf-ompa`（icet で fcc 配置 631 個を列挙 → MLIP 環境のサブプロセスで緩和 → CE（ARDR）→ 8³ セルの正準 MC を 500→40 K 冷却、C_v ピークで T_c）。`out_ce_<mlip>/`。
- SevenNet-MF-ompa の工程 01–07: smoke pk 10674（QHA は mygardenx2）、通れば `autosubmit.sh` が本番を投入。

## 結果 6: WorkChain 内の固相だけの相図と端成分 TI（2026-11-09）

`--solid-only --ends-ti` の 3 本はすべて Finished [0]（provenance 付き、`aiida_txdiagram/out/ptrh_<mlip>_solid_ti/07_phase_diagram.png`）。規則相の消える温度は外部スクリプトの再組立（結果 2・3）と同じ: MACE PtRh 230–240 K・Pt₃Rh 500 K・PtRh₃ 900 K、GRACE-2L 230 / 700 / 1330 K、NequIP 210 / 570 / 1190 K（PtRh 以外はノイズ）。

端成分の 2,048 原子 TI: Pt（1700→2150 K）は 3 MLIP とも後退掃引で融けて失敗（exit 320）、MACE は Rh（1900→2350 K）も融けた。GRACE-2L と NequIP の Rh TI は成功し、QHA（古典化）− TI は 1700 / 2025 / 2350 K で GRACE-2L −22 / −37 / −53、NequIP −53 / −78 / −103 meV/atom。QHA が高温の固相をこれだけ過安定化していたのが「Pt・Rh が 2400 K でも融けない」原因（Ni–Al の EAM と同じ）。

| 融点（TI 固相 × 液相の交点、2026-11-09） | 実験 | GRACE-2L | NequIP-OAM-M | MACE-MPA-0 |
|---|---|---|---|---|
| Rh (x = 1) | 2237 K | 2032 K | 2050 K | 1904 K |
| Pt (x = 0) | 2041 K | ≈ 1490 K | ≈ 1420 K | ≈ 1480 K |

Pt は 3 MLIP とも TI（1400–1700 K）と液相（1500 K まで）の交点が 1500 K のすぐ下で、値は 1500–1700 K の重なりからの短い外挿（±30 K 程度）。実験より 550–620 K 低く、Rh（190–330 K 低い）よりずれが大きい。液相を 1500 K より下へ延ばしても結論は変わらないので打ち切り。
| QHA − TI, fcc Rh, 2025–2050 K | — | −37 meV/atom | −78 | −100 |

Rh は液相を `liqext`（`mlip_solids_ti.py liqext --liq 1.0:2200:1900`、pk 12535/12537/12539）で 1900 K まで延ばし、`assemble`（`merge_sweeps` で接ぎ足し、重なり部のずれ 0.1–0.6 meV/atom）→ `melt` で直接の交点（`out/mlip_compare_ptrh/melting_ti.tsv`、`out/ptrh_<mlip>_ti/`）。3 つの MLIP とも Rh を 190–330 K 低く、Pt も 60 K 以上低く見積もる。論文の図 11（PFP の TDB、液相は理想溶体）と比べる土台はこれで揃うが、PFP 自身の融点は論文に数値が無い。Pt は上限 2150・1980 K（3 MLIP とも融解）、NequIP は 1850 K でも融解。1700–1850 K（GRACE-2L 12554、MACE 12601）、1700–1750 K（NequIP 12708）、1400–1700 K（GRACE-2L 12714、MACE 12732、NequIP 12737）の掃引と、Pt 液相の 1700 K（12561/12563/12565）・1500 K（12716/12718/12720）までの延長で交点を追った。`assemble` は複数段の延長を T_hi の高い順に接ぎ足すように直した（2026-11-10）。QHA − TI は fcc Pt で 1550–1775 K に −70〜−87 meV/atom。

## 結果 7: ノイズを外した固相図、論文の図、データベースの図（2026-11-10、ユーザー依頼）

- `solid_panels_filtered.py` → `out/solid_panels_filtered.png`：`out/<run>/lowT/07_two_phase_regions.tsv` から、規則相は結果 1 の 0 K 規則化エネルギーが −7 meV/atom 以下の MLIP でだけ残し（MACE-MPA-0・SevenNet-MF-ompa の PtRh のみ該当）、同一相区間（fcc+fcc、PtRh+PtRh）は落とした。残るのは PtRh+fcc 200–230 K（SevenNet は 270 K まで）だけ；GRACE-2L・NequIP-OAM-M は 0 区間。▼ は CE+MC の転移温度。
- 論文 Figs. 9–11（CC BY 4.0）を `papers/s41524-026-02212-9.pdf` p. 7–8 から切り出した：`out/paper_fig9.png`（DFT TDB）、`paper_fig10.png`（−200〜100 °C の MLIP vs DFT）、`paper_fig11.png`（MLIP TDB）、結合 `paper_figs_9_10_11.png`。
- データベースから描ける Pt–Rh 相図：ORCHID-Diagrams の SGTE 評価 3 件（fcc+液相のみ、不変反応なし）。`orchid_calphad/sgte_diagrams.py` に `ptrh` を追加（`out/sgte_ptrh.png`、`overlay_ptrh.png`：PtRh-98Jac の境界を WorkChain の 1910–2400 K 窓の MLIP 図に重ねた）。低温の規則化はどのデータベースにも無い。
- `overlay_full.py` → `out/overlay_ptrh_full.png`（図 10d の差し替え、2026-11-10）：縦軸を 100–400 K と 1700–2400 K で切り、上段に SGTE PtRh-98Jac の固液境界と WorkChain の液相窓、下段に論文の表 7 の不変反応（PFP 実線・DFT 破線）とノイズ除去後の固相図（`solid_panels_filtered.py` の規則）と CE+MC の転移温度を重ねた。

## 結果 8: Saengdeejing の方法（CALPHAD 経路）で描いた Pt–Rh 相図（2026-11-11、MACE-MPA-0、ユーザー依頼「Saengdeejing の方法で Pt-Rh の相図を書く。MLIP は Claude に任せる」）

MLIP は MACE-MPA-0 を選んだ（0 K の規則化エネルギーが DFT に最も近く、CE+MC・欠陥セル法の両方の結果がある唯一の MLIP）。論文（Table 6、式 11–15）の手順を pycalphad で再現した：

- `calphad_params.py <run>`（env/ftphase、AiiDA の QHA ノードを読む）→ `out/calphad_<mlip>/params.json`。純元素は SGTE91（`espei.refdata`）。fcc 固溶体は理想混合 + Redlich–Kister で、L_k = a_k + b_k T の a_k を 32 原子乱雑セル（13 組成 × 2 配置）の 0 K 静的エネルギー（`E0_eV_per_atom`）の混合エンタルピーに、b_k を同じセルの調和フォノン自由エネルギー（phonopy、0 K 体積、量子）の過剰分の 300–1000 K の傾きに当てはめた（論文の「SQS の有限温度」に相当）。規則相 PtRh（I4₁/amd）と D0₂₂（PtRh₃ / Pt₃Rh）は 2 副格子 CEF (Pt,Rh)₀.₅(Pt,Rh)₀.₅・(Pt,Rh)₀.₇₅(Pt,Rh)₀.₂₅ で、端成分 Pt:Pt・Rh:Rh は GHSER、混合端成分は Neumann–Kopp 和 + ΔG_f = ΔH_f − TΔS_f（ΔH_f = 化学量論セルの 0 K 生成エネルギー、ΔS_f = 調和 F_vib の生成分の傾き）。液相は SGTE 液相の理想溶体（論文と同じく液相データ無し）。
- `calphad_tdb.py out/calphad_<mlip> [--model plain|partition] [--T 100 400 --dT 2]`（env/pycalphad）→ TDB、`grid*.tsv.gz`（T–x 格子の相集合と副格子占有）、`invariants*.json`、`diagram*.png`。SGTE 関数は下限を 1 K にして 100–300 K の規則化窓を計算した（298.15 K 以下は SGTE 多項式の外挿；固相はすべて同じ GHSER を使うので固相間の平衡では相殺する）。
- `calphad_figure.py` → `out/calphad_mace_mpa_0/calphad_vs_hull.png`：基準（SGTE PtRh-98Jac + 論文表 7）、同じ MLIP の凸包経路（工程 01–07 + 低温再組立 + CE+MC）、CALPHAD 経路を並べた（縦軸 100–400 K / 1700–2400 K）。

得られたパラメータ（J/mol-atom）と論文 Table 6 の比較：

| 量 | 論文 PFP | 論文 DFT | MACE-MPA-0（本経路） |
|---|---|---|---|
| fcc ⁰L | −8725 + 4.53 T | −5000 + 1.3 T | −6084 + 2.60 T |
| fcc ¹L | +1.25 T | +3000 | +477 + 0.32 T |
| fcc ²L | — | — | −226 − 1.19 T |
| ΔH_f PtRh (eV/atom) / ΔS_f (k_B) | −0.0376 | −0.0236 | −0.0268 / −0.154 |
| ΔH_f PtRh₃ / ΔS_f | −0.0280 | −0.0200 | −0.0197 / −0.087 |
| ΔH_f Pt₃Rh / ΔS_f | −0.0235 | −0.0200 | −0.0166 / −0.080 |

相図の不変反応（`invariants_plain_lowT.json`、2 K・0.005 格子 + pycalphad mapping）：

| 反応 | 論文 PFP | 論文 DFT | MACE CALPHAD 経路（本節） | MACE 凸包経路（結果 3・4） | MACE CE+MC（結果 5） |
|---|---|---|---|---|---|
| fcc ↔ PtRh (x 0.5) | 258 K | 211 K | 176 K（x 0.46–0.52） | 230 K | 160 K |
| fcc ↔ PtRh₃ (0.75) | 235 K | 156 K | 146 K（0.75–0.79） | 決まらず | 140 K |
| fcc ↔ Pt₃Rh (0.25) | 146 K | 不安定 | ≤ 106 K | 決まらず | 100 K |
| fcc ↔ PtRh + PtRh₃ 共析 | 211 K (x 0.653) | 149 K (0.693) | 135 K（fcc 0.683 / PtRh 0.566 / PtRh₃ 0.747） | — | — |
| fcc ↔ Pt₃Rh + PtRh 共析 | 146 K (0.258) | — | 106 K（fcc 0.225 / Pt₃Rh 0.224 / PtRh 0.338） | — | — |
| fcc+液相の最大幅 | 「非常に狭い」 | 同 | Δx 0.045（2170 K）；Pt 2041.5 K・Rh 2237 K は SGTE のまま | 図 10d | — |

読み：

1. **同じ MLIP の入力から論文の方法で組むと、規則化温度は論文の DFT 版（211/156 K）より 30 K 低く、PFP 版（258/235 K）より 80–90 K 低い。** 差の源は 0 K の規則化エネルギー（規則相 − 乱雑 fcc：MACE PtRh −11、PtRh₃ −8、Pt₃Rh −5 meV/atom；論文 PFP ≈ −15/−11/−7、DFT ≈ −11/−10/−10）で、PtRh の MACE と DFT は同じ −11 meV だが MACE の fcc 過剰項の温度係数（⁰L の +2.6 T、振動の過剰エントロピーが負）が fcc を高温で相対的に安定にする分だけ下がる。
2. **同じ MLIP で経路を変えると 176 K（CALPHAD、Bragg–Williams 型 CEF）、230 K（凸包経路の欠陥セル + 副格子エントロピー）、160 K（CE + 正準 MC、短距離秩序込み）。** 経路差 ±35 K は MLIP 間差（GRACE-2L・NequIP では規則相が出ない）より小さいが、論文の PFP–DFT 差 50 K と同程度。論文の「MLIP と DFT で同程度の相図」という結論は、どの経路でも 0 K 規則化エネルギーが DFT に近い MLIP（MACE-MPA-0、SevenNet-MF-ompa）にだけ成り立つ。
3. **モデルの落とし穴 2 つ。**（a）論文と同じ「分割なしの 2 副格子 CEF」は、規則相の不規則状態（両副格子の占有が等しい状態）が fcc と別の相として競合する。MACE のパラメータでは 2100–2150 K で fcc の RK 過剰項（+2.6 T で消えていく）と D0₂₂ の不規則状態が数 J/mol 以内で縮退し、pycalphad の mapping が fcc+D0₂₂+液相の偽の 3 相点を返す。`calphad_tdb.py` は副格子占有差 |Δy| < 0.05 の頂点を fcc に付け替えて図を作る（`grid_plain.tsv.gz` の eta 列）。（b）標準の order–disorder 分割（`--model partition`、`DIS_PART FCC_A1`）にすると PtRh は 210–214 K に上がるが、非対称な (Pt,Rh)₀.₇₅(Pt,Rh)₀.₂₅ 相は端成分パラメータだけでは不規則状態が停留点にならず（dE/dη ≠ 0）、D0₂₂ の秩序度が転移なしに連続的に減衰する（|Δy| 0.05 を切るのが 640 K）。Ansara–Dupin 型の拘束付き相互作用パラメータが要る。本節の数値は論文と同じ分割なしモデルの値。
4. 液相は理想溶体 + SGTE なので固液側は MLIP の情報を含まない（論文も同じ）。MLIP の液相 TI を入れた固液側は図 10d（凸包経路、Pt 1480 K・Rh 1904 K、実験 2041/2237 K）。
