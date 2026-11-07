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

## 進行中（2026-11-06 21:10 投入、11-08 更新）

- 融点側 + 固相だけの組立を WorkChain 内で: `run_aiida.py --system ptrh --mlip <m> --computer mygarden6 --solid-only --ends-ti`（11-07/08 に実装: `assemble.allow_solid_only` で液相の無い温度も固相だけの凸包として格子に残す、`solids_ti` に `x` / `keys` / `one_per_x` の絞り込み、`skip_liquids`）。単独投入していた端成分 TI 6 本は kill して WorkChain に戻した。smoke pk 11014 で組立経路を確認（TI の smoke は 256 原子・1900 K で融けて exit 310、本番は 2,048 原子・1700 K 開始）。本番: MACE pk 11345、GRACE-2L 11358、NequIP 11372（`ptrh_<mlip>_solid_ti`、組立 100–2400 K）。工程 01 の緩和が前回と僅かに違う構造を返したため QHA はキャッシュに当たらず再計算（MACE は mygardenx2 の CPU、他は mygarden6 の GPU）。
- 規則化温度（短距離秩序込み）: `ce_mc.py --mlip mace-mpa-0|sevenn-mf-ompa`（icet で fcc 配置 631 個を列挙 → MLIP 環境のサブプロセスで緩和 → CE（ARDR）→ 8³ セルの正準 MC を 500→40 K 冷却、C_v ピークで T_c）。`out_ce_<mlip>/`。
- SevenNet-MF-ompa の工程 01–07: smoke pk 10674（QHA は mygardenx2）、通れば `autosubmit.sh` が本番を投入。
