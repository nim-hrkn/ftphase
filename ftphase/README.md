# ftphase — MLIP の自由エネルギーから有限温度相図を組む Python パッケージ

`docs/workflow.html` の工程のうち、calphy・pycalphad・pyiron の公開例が覆っていなかった部分
（`docs/examples.html`、`docs/public-sources.html` 参照）を、公開コードの上に薄く実装したものです。
作成日 2026-10-21。版 0.1.0。ライセンス MIT（依存パッケージは各自のライセンスに従う。calphy は Academic Software Licence）。

## 何ができるか（工程との対応）

| 工程 | モジュール | 内容 | 依拠する公開コード・出典 |
|---|---|---|---|
| 01 候補相と MLIP 検証 | `ftphase.validate` | ASE で緩和（空間群の変化を検出）、0 K 凸包と生成エネルギー、既知基底状態との照合（黙って置換しない）、Vinet EOS、calphy の融点入力生成 | ASE、pymatgen `PhaseDiagram`（Ong 2013）で相互検証、spglib |
| 02A 組成・副格子・空孔系列、SQS | `ftphase.structures` | 整数原子数のランダム置換系列（seed・実組成・副格子ごとの占有数を記録）、空孔は「原子の欠損」として生成、icet の SQS（副格子・空孔 `X` 対応、クラスターベクトルの残差を記録）、sqsgenerator ラッパ、LAMMPS data 出力 | icet（Ångqvist 2019）、sqsgenerator（Gehringer 2023） |
| 03A 固相 phonon/QHA | `ftphase.qha` | 式 (D1) の調和自由エネルギー（量子／古典、虚振動は既定で例外）、Vinet / Birch–Murnaghan / 多項式 EOS、式 (D2) の QHA（最小が走査範囲外なら例外）、phonopy + 任意の ASE 計算器による体積走査、anphon `.thermo` の読み込み | phonopy（Togo 2023）、ALAMODE / aiida-alamode（Tadano 2014） |
| 03B 液相 TI（補助経路の固相 TI） | `ftphase.calphy_io` | calphy 2.x の入力生成（組成系列、Slurm `queue`、`gpu=True` で KOKKOS/CUDA）、結果の読み込み（古典・配置項の有無をフラグ化） | calphy（Menon 2021）、LAMMPS KOKKOS |
| 04A 配置自由エネルギー | `ftphase.configurational` | 理想混合 (E1)/(E14)、厳密な数え上げ (E9)、副格子モデル (E10)–(E12)（空孔・基準の選択）、状態密度からの F_conf (E13)（icet / smol の Wang–Landau 出力） | pycalphad の CEF 規約（Otis 2017）、icet mchammer |
| 04B 量子固相と古典液相の整合 | `ftphase.quantum` | 同じ振動数から F_q − F_cl を計算し、calphy の古典 G を量子側へ、または QHA を古典側へそろえる。高温極限は Wigner–Kirkwood 項で検証 | — |
| 05 基準統一 | `ftphase.records`, `ftphase.assemble` | 1 行 = (相, x, T, P, G) の表（単位 eV/atom、基準状態、方法、配置項・量子の有無、出典を必須列に）、純元素基準 (G1)、配置項の加算（二重計上は例外）、温度補間、calphy `PhaseDiagram.from_df` への受け渡しと TDB 出力、pycalphad での再計算 | calphy 2.3 `phase_diagram.py`、pycalphad |
| 06 凸包・共通接線 | `ftphase.equilibrium` | 点相（line compound）と限定組成相を含む全相の下側凸包（単調鎖）、式 (H3) の共通接線を fsolve で精密化、混和ギャップ検出、化学ポテンシャル (H4)、てこの法則 (H5)、対称正則溶体の解析解 | pyiron workshop `helpers.find_common_tangent` の一般化、pymatgen の凸包と同じ考え方 |
| 07 T–x 図・不変反応・誤差・記録 | `ftphase.diagram` | 温度走査、共存相の組の変化で不変反応を挟み込む、Monte Carlo による G の不確かさの伝播、温度ごとの帯で描画、TSV + JSON の記録 | — |

式番号は `docs/workflow.html` のラベルです。

## 導入

```bash
# 専用環境（calphy 2.3.0 GitHub 版、LAMMPS 2025.07.22 conda-forge、phonopy、pymatgen、icet 4.0、sqsgenerator 0.5.6、pycalphad 0.11.2）
mamba create -p ./env/ftphase -c conda-forge python=3.12 "lammps=2025.07.22=cuda129*mpi_openmpi*" "cuda-cudart>=12.9,<13" \
  "pyscal3>=4.0" ase pylammpsmpi mendeleev pydantic tqdm pyyaml scipy pandas matplotlib-base phonopy pymatgen icet sqsgenerator \
  spglib seekpath h5py pyarrow pytest "python-symengine>=0.9.2,<0.14" xarray pint pyparsing tinydb runtype typing_extensions setuptools_scm numpy jinja2
./env/ftphase/bin/pip install --no-deps "git+https://github.com/ICAMS/calphy.git@67caa5b" pycalphad==0.11.2
./env/ftphase/bin/pip install -e ./ftphase
```

必須依存は numpy, scipy, pandas, ase, pyyaml, matplotlib だけで、phonopy / icet / calphy / pycalphad / pymatgen は使う関数で初めて import します。

### GPU（ACE を LAMMPS KOKKOS/CUDA で走らせる）

conda-forge の LAMMPS 22 Jul 2025 は KOKKOS/CUDA ビルドで `pace/kk` を持ちますが、calphy が固相 Frenkel–Ladd 以外のすべての段（reversible scaling、液相の UFM 切り替え、alchemy、dcci）で使う `pair_style hybrid/scaled` の KOKKOS 版 `hybrid/scaled/kk` がありません（`-k on` を付けると "Must use pair_style hybrid/scaled/kk with Kokkos" で停止）。`hybrid/scaled/kk` は LAMMPS stable 30 Sep 2026 にあるので、`env/lammps-gpu/build.sh` が env/ftphase のツールチェーン（cuda-nvcc 12.9、gxx 14、OpenMPI 5）で KOKKOS/CUDA（sm_86）+ ML-PACE の `lmp_gpu` をビルドします。

```bash
mamba install -p ./env/ftphase -c conda-forge "cuda-nvcc=12.9" "cuda-cudart-dev=12.9" "cuda-version=12.9" cxx-compiler c-compiler cmake make
git clone --depth 1 --branch stable_30Sep2026 https://github.com/lammps/lammps.git env/lammps-gpu/src
env/lammps-gpu/build.sh          # → env/lammps-gpu/bin/lmp_gpu
```

`calculation_block(..., gpu=True, lammps_executable=".../lmp_gpu")` が calphy 入力を GPU 用にします：`md.cmdargs: -k on g 1 -sf kk -pk kokkos newton on neigh half`、`queue.cores: 1`（GPU 1 枚につき MPI 1 ランク）、`#SBATCH --gres=gpu:1`、`pair_style pace` → `pace product`（`pace/kk` は product 評価しか受け付けない）。`gpu_capability(lmp)` が `lmp -h` から `pace/kk`／`hybrid/scaled/kk` の有無を読み、走らせられないモードは入力生成の時点で `ValueError` にします。検証結果は「実行した例」の 4 を参照（GPU 1 ランクが CPU 4 ランクの 1.7〜3.3 倍速、エネルギー・圧力は全桁一致）。

注意点：GPU 1 枚ではジョブが直列になるため、総スループットは CPU 8 コアと同程度です。利点は 1 本の待ち時間短縮と、CPU を QHA に空けられることです。

## 計算ホスト mygardenx1（CPU、2026-10-22 設定）

| 項目 | 値 |
|---|---|
| ハード | AMD EPYC 9554 64 コア（SMT なし、AVX-512）、377 GB、GPU なし |
| Slurm | 単一ノード `localhost`、パーティション `debug`、64 CPU、時間制限なし |
| conda | `/home/kino/miniconda3`（conda 25.1、conda-forge）。環境は `/home/kino/kino/Claude/Projects/PhaseDiagram/env/ftphase`（`setup_env_mygardenx1.sh` で作成：mygarden5 と同じ構成から CUDA を除き、LAMMPS は `cpu_py312*mpi_openmpi*`、tensorpotential 0.6.2.1 を追加） |
| LAMMPS | 22 Jul 2025 Update 6、CPU、OpenMPI（環境内）。`pace`、`grace/fs`、`mliap`、`hybrid/scaled`、`ufm` あり。KOKKOS なし |
| MPI | conda の OpenMPI。システムの Intel MPI / apt の openmpi は使わない |
| 同期 | `ftphase/tools/sync_to_host.sh mygardenx1`（パッケージ、例題スクリプト、ACE ポテンシャルを同じパスへ。out_* と calphy ジョブは除外） |
| 動作確認 | pytest 38 件合格。LJ 32k 原子：16 ランク 0.60 s、1 ランク 7.9 s。calphy fe（fcc Al ACE、800 K、2000+2000 ステップ、16 ランク）53 s で G = −3.7119 eV/atom（mygarden5 の ts 結果 −3.7115 と一致） |

使い方：`calphy_io.slurm_queue(env_prefix, cores=16)` は conda.sh の場所を自動で選ぶ（miniforge3 → miniconda3、または環境変数 `CONDA_SH`）。`run_*.sh` も同じ探索をするので、例題ディレクトリを同期して mygardenx1 上で `./run_pipeline.sh` を実行すればよい（GPU 用の `gpu=True` ブロックは使えないので、液相は `cores=16` の CPU ブロックにする）。64 コアなので calphy 16 ランク × 4 本を同時に流せる。

## 使い方の骨格

```python
from ftphase.records import FreeEnergyTable
from ftphase.assemble import add_configurational_term, interpolate_T, builder_from_table, fit_residuals
from ftphase.configurational import b32_antisite_site_fractions
from ftphase.diagram import scan, invariants, sensitivity, plot_tx, write_records

t = FreeEnergyTable.from_tsv("free_energies.tsv")        # 相, kind(solution/point/limited), x, T, P_GPa, G, G_err, ...
assert not t.check()                                       # 基準状態・圧力・量子/古典の混在を検査
t = add_configurational_term(t, "fcc", "ideal")            # (E2)。液相 TI には加えない（フラグで拒否される）
t = add_configurational_term(t, "B32", "sublattice", site_model=b32_antisite_site_fractions)  # (E10)
ti = interpolate_T(t, range(600, 1001, 5))
b = builder_from_table(ti, fit="spline")                   # spline / poly / rk
print(fit_residuals(b, 800.0))
reg = scan(b, ti.temperatures())                          # 二相域の表
print(invariants(reg))                                     # 共晶などを温度で挟み込む
sens = sensitivity(b, ti.temperatures()[::4], {"fcc": 0.002, "B32": 0.002, "liquid": 0.002}, n_samples=50)
plot_tx(reg).figure.savefig("Tx.png"); write_records("two_phase.tsv", reg, {"fit": "spline"})
```

コマンドライン：`ftphase check table.tsv`、`ftphase diagram table.tsv --tmin 600 --tmax 1000 --dt 5 --png Tx.png`、`ftphase hull0k hull.tsv --known fcc-Al,bcc-Li`。

## 検証

`tests/`（pytest、50 件 + skip 1、約 7 秒；AiiDA 層 8 件 `test_aiida.py` を含む）。解析解との比較を中心にしています。

- 配置項：workflow の数値例 (E3)–(E8)、(E15)–(E17) を再現。厳密数え上げ (E9) が Stirling に収束。副格子モデルが単一副格子で理想混合に一致、B32 の反サイトモデルが「全格子点理想混合の半分」になる。空孔を含む組成換算 (E11)/(E12)。2 準位系の状態密度から F と S。
- QHA：Einstein 結晶の量子・古典 F、S = −dF/dT、虚振動の例外、Vinet の係数回復、二次 E0(V) と線形 F_vib の解析解（圧力項も）、anphon `.thermo` の整合性、phonopy の F が入力セルあたりに正しく規格化されること（基本胞と立方胞で一致）。
- 相平衡：対称正則溶体の混和ギャップが解析解の binodal に 1e-6 で一致、点相への接線条件、限定組成相を外挿しない、同じ x に複数相がある凸包、共晶型の温度走査と不変反応、Monte Carlo 感度。
- 表と橋渡し：スキーマ検査、純元素基準、配置項の二重計上の拒否、温度補間、calphy `PhaseDiagram.from_df` への受け渡し。
- 構造・検証・入出力：整数原子数の系列と seed 再現性、空孔の占有率、icet SQS（fcc 16 原子）、EMT Al の緩和と EOS、calphy 入力の往復（calphy 自身の検証パーサ）、`calphy-examples/example_03` の読み込み。

## 実行した例（`examples/`）

### 1. Al–Li EAM（pyiron workshop 2022 の 18 本の calphy 結果）— `alli_eam_workshop.py` → `out_alli_eam/`

同じ 6 組成 × 3 温度の自由エネルギーを、B32 の配置項（全格子点理想混合 vs 副格子反サイト）と fit（3 次多項式 vs スプライン）の 2×2 で処理した結果。実組成 x_actual を使用（チュートリアルは公称組成）。

| 変種 | 800 K の fcc+B32 | 液相が最初に現れる温度 | 不変反応の挟み込み |
|---|---|---|---|
| 理想混合・poly3（チュートリアル相当） | 0.158–0.222 | 906 K | 904–906 K：B32+fcc → B32+液, fcc+液（共晶） |
| 理想混合・spline | 0.139–0.250 | 820 K | 818–820 K |
| 副格子・poly3 | なし | 800 K（範囲の下端） | なし |
| 副格子・spline | なし | 800 K | 816–818 K：液+B32 が消える |

2 meV/atom の G の不確かさで境界は x で ±0.02〜0.04 動き、fit の形だけで共晶温度が約 85 K 動きます。6 点の組成格子と 5 ps のスイッチングでは共晶を決められない、という結論自体が workflow 第 8 節（境界付近の細分化、fit 誤差の評価）の要請を数値で示しています。B32 を副格子で扱うと（workflow 第 4 節の要請）、この EAM データでは 800 K で既に液相が fcc と B32 の間に入り、共晶は 800 K 未満になります。calphy 2.3 の `PhaseDiagram`（同じ表から `from_df` で構築）による相図も `calphy_phase_diagram_crosscheck.png` に出力。

### 2. Al–Li ACE（workshop の `AlLi-6gen-18May.yace`、Menon 2024）— `alli_ace_validate_qha.py` → `out_alli_ace/`

実際の MLIP で工程 01・02A・03A・04B を回したもの（CPU、約 10 秒）。

- 01：fcc Al（E = −3.4789 eV/atom, V = 16.54 Å³）、bcc Li、fcc Li、B32 AlLi（E_form = −0.179 eV/atom）、L1₂ Al₃Li（−0.094）。空間群は緩和で保持。**ACE では Al₃Li が凸包上に乗る**（B32–fcc の弦より 4.6 meV/atom 下）。既知基底状態の照合は「MLIP ground state not in known list」として報告（Menon 2024 は Al₃Li を準安定としている）。pymatgen の e_above_hull と一致（差 ≤ 0.6 meV は fcc-Li と bcc-Li のタイ処理）。Vinet：B₀ = 81.8 GPa（実験約 76）。
- 02A：32 原子ランダム Al₀.₈₇₅Li₀.₁₂₅ 2 配置（E = −3.2850, −3.2847）と icet の 16 原子 SQS（列挙、クラスターベクトル残差 0.203、E = −3.2879 eV/atom、未緩和）。
- 03A：phonopy 2×2×2、9 体積（長さ −3 %〜+5 %）、Vinet。fcc Al：V(0 K) = 16.69 → V(1000 K) = 18.13 Å³/atom、B(300 K) = 72.7 GPa、300–900 K の平均線膨張 32 ppm/K（実験 23–30）。B32 AlLi：B(300 K) = 43.5 GPa。
- 04B：F_q − F_cl（調和）= fcc Al 3.40 meV/atom（300 K）、1.03（1000 K）；B32 5.27 / 1.61 meV/atom。古典 TI の固相と量子 QHA を混ぜると融点付近で 1 meV/atom 級のずれが出る、という大きさの目安。

### 3. ACE Al の融点：calphy TI（古典）と QHA（量子）の整合 — `alli_ace_melting.py`

`calphy_ace/input_ace_ts.yaml`（本パッケージが生成、fcc Al 256 原子、固相 Einstein／液相 UFM、800–1000 K の reversible scaling、5000+5000 ステップ、Slurm 4 コア）を実行し、(a) calphy 固相 vs 液相、(b) QHA 固相 vs calphy 液相、(c) QHA を F_q − F_cl で古典側へ下げたもの vs 液相、の 3 通りで融点を比較します。結果（`out_alli_ace/melting_ace.json` / `.png`）：

| 比較 | 融点 |
|---|---|
| (a) calphy 固相 vs calphy 液相（古典同士） | 904 K（実験 933.5 K。別 seed の再実行では 902–927 K、例 4） |
| (b) QHA 固相（量子）vs calphy 液相 | 864 K（不整合） |
| (c) QHA を F_q − F_cl で古典化 vs calphy 液相 | 874 K |

x_Li = 0.1016（256 原子、ランダム置換）の fcc と液相も同じ入力で計算し、900 K で fcc が液相より 29.7 meV/atom 高い（古典同士）。(b)−(c) の 10 K が量子／古典の取り違えの大きさ、(c)−(a) の 30 K が 900 K で QHA（古典化後）が Einstein 結晶 TI より 3.7 meV/atom 高いこと（QHA に無い非調和項と TI の統計誤差）の大きさです。

### 4. GPU と CPU の calphy 比較（03B）— `alli_ace_gpu_compare.py` → `out_alli_ace/gpu_vs_cpu.{json,png}`

例 3 と同じ 4 本（fcc／液相 × x = 0, 0.1、800–1000 K、5000+5000 ステップ）を、`calphy_ace_gpu/make_input.py` が書いた GPU 入力（`lmp_gpu`、KOKKOS、`pace product`、`--gres=gpu:1`）で再実行し、さらに純 Al の 2 本を CPU・GPU それぞれ別 seed で繰り返しました（`calphy_ace_repeat/`、`calphy_ace_gpu_repeat/`）。

| 項目 | 結果 |
|---|---|
| 1 本の所要時間 | CPU 4 ランク 235–412 s（負荷による）、GPU 1 ランク 125–149 s |
| 1 点のエネルギー・圧力（ti/spring、hybrid/scaled、hybrid/scaled+ufm の 3 設定） | GPU と CPU で全桁一致 |
| G(T) の差 GPU − CPU（同じ入力、別 seed） | −1.4〜+3.2 meV/atom |
| G(T) の差 CPU 再実行 − CPU | +0.4〜+1.1 meV/atom |
| 900 K の G の標準偏差（4 サンプル） | fcc 1.4、液相 1.3 meV/atom |
| 純 Al の融点（固相・液相の 4 通りの組合せ） | 902–927 K |

GPU の値は CPU の値を挟んで両側に散らばり（GPU 初回 +2.8、GPU 再実行 −0.3 meV/atom at 900 K）、系統差はありません。差はすべて 5000 ステップ切り替え・1 反復の統計ばらつきで、これが例 3 の融点 904 K に ±10 K 程度の不確かさを与えます。calphy は `n_iterations: 1` では `G_err = 0` を返すので、実用では `n_iterations ≥ 3` にして `G_err` を `sensitivity` に渡してください。

### 5. 01 から出発した T–x 図：ACE Al–Li、Slurm + GPU — `alli_ace_txdiagram/` → `out/`

`pipeline.py` と `run_pipeline.sh`（再開は `run_resume.sh`）。投入後はすべて Slurm が管理するので、起動したセッションを閉じても最後まで走る。

| 段 | 実行 | 内容 | 時間 |
|---|---|---|---|
| 01/02A/02B `prepare` | ログインノード | fcc Al、bcc Li、B32、L1₂ Al₃Li の緩和と 0 K 凸包（4 相とも凸包上、Al₃Li は ACE では安定）。fcc 32 原子セル x = 0.0625–0.25（各 2 配置）、B32 反サイト x = 7/16, 1/2, 9/16、液相 256 原子 x = 0–0.5 の 6 組成、calphy GPU 入力 | 15 s |
| 03A `tx_solids` | CPU 4 コア | 13 セルの phonopy 体積走査（9 体積）+ QHA、振動数を保存 | 149 s |
| 03B `lqd_x*` | GPU 6 本（直列） | calphy ts 1100→700 K（x = 0.1 は 700 K で凝固したため 800 K まで）、UFM、3 反復、`lmp_gpu` | 485–517 s / 本 |
| 04–07 `tx_assemble` | CPU、`--dependency=afterany` | QHA を F_q − F_cl で古典水準へ、fcc に理想混合、B32 に副格子項、1 表 → 凸包 → 不変反応 → Monte Carlo 誤差帯 → T–x 図 | 5 s |

結果（`out/07_phase_diagram.png`、`07_two_phase_regions.tsv`、`07_sensitivity.tsv`、`summary.json`、古典水準、0 GPa）：

| 特徴 | ACE（本計算） | 実験 |
|---|---|---|
| 共晶 | 760–770 K、液相 x ≈ 0.30–0.31、fcc 0.157 + B32 0.480 | 875 K、x ≈ 0.24、fcc ≈ 0.14 |
| 純 Al の融点 | 860–870 K | 933.6 K |
| B32 側の液相線の終わり（x = 0.5） | 840–850 K | AlLi 融点 975 K |
| Al₃Li | 700 K 以上で不安定（30 回の誤差サンプル中 1 回だけ現れる） | 準安定 δ' |
| 誤差帯（固相 2、液相 1.4 meV/atom） | fcc 固溶限 ±0.01、800 K の液相側境界 ±0.03–0.05、共晶温度 ±15 K 程度 | — |

実験欄の出典：H. Okamoto, J. Phase Equilib. Diffus. 33, 500 (2012) Fig. 1（Hallstedt & Kim 2007 の評価、読み取り値は `資料/10.1007/s11669-012-0119-8/Fig1_readings.md`）。

組成の特徴（共晶組成、固溶限、Al₃Li の不安定化）は実験と合い、温度は約 100 K 低い。原因の候補は、ポテンシャル自体、32 原子セルの配置ノイズ（最大 2.6 meV/atom）、古典水準での比較、5000–10000 ステップの切り替え。この例で分かった実装上の注意：3 次多項式を G にそのまま当てると x ln x の形を再現できず偽の二相域（fcc+fcc、liquid+liquid）が出る。`PhaseCurve.from_points(ideal_T=T)` で理想混合項を解析的に分離し過剰項だけをフィットする（`builder_from_table(ideal_excess_fit=True)` が既定、正則溶体の解析解で検証）。

### 6. 全組成の T–x 図と配置ノイズ低減：ACE Al–Li、64 原子 SQS、Slurm + GPU — `alli_ace_txdiagram/pipeline_full.py` → `out_full/`

2026-10-22 16:42 に投入（Slurm job 22546 固相、22547–22551 液相 GPU、22552 組立）。**結果は `out_full/REPORT.md` と `out_full/07_phase_diagram.png` に自動で書かれる**（投入したセッションには依存しない）。中断したら `run_resume_full.sh`。

例 5 との違い：(1) fcc 固溶体を 32 原子ランダム 2 配置から 64 原子 icet SQS（`sqs_icet(method='supercells')`、クラスターベクトル残差 0.04–0.10）に替えて配置ノイズを下げる。REPORT.md に例 5 との 800 K の G の差を出す。(2) Li 側を追加：bcc 固溶体 x_Li = 0.75–1（64 原子 SQS、Li は熱膨張が大きいので体積走査 0.96–1.14）、液相 x = 0.6–1.0（250 原子、GPU）。Al 側の液相 6 本は例 5 の結果を再利用。Al₂Li₃ と Al₄Li₉ は投入時には無かったが、後から追加した（下記）。

投入前に 5 セル（fcc 0・0.0625、bcc 1、Al₃Li、B32）の QHA と組立を通しで確認済み。64 原子 fcc 1 セルの QHA は CPU 4 コアで 55–85 s。

結果（**最終組立 2026-10-23 01:22**、Slurm 22620；REPORT.md の文面は 08:18 に再生成、`out_full/REPORT.md`、`07_phase_diagram.png`、古典水準、0 GPa、0 ≤ x ≤ 1、格子 650–1100 K）。入力：固相 16 セルは phonopy の密度メッシュ 60 Å で再計算した QHA（Slurm 22619、833 s）、液相は 11 組成 × 3–4 run（1100 → 700 K を seed 違いで 3 本、700 → 650 K または 500 K の掃引、Slurm 22553–22584・22622、計 32 本、20:54–01:15）を (x, T) ごとに平均。ユーザー提供の Materials Project 構造 Al₂Li₃（mp-16506、R-3m）・Al₄Li₉（mp-568404、C2/m）は点相（0 K 凸包上、生成エネルギー −183、−160 meV/atom）、液相は理想混合 + 4 項 Redlich–Kister。

| 特徴 | ACE 例 6（最終） | 中間組立（10-22 20:45、[4,4,4] メッシュ、液相 1 本） | 例 5（32 原子ランダム、x ≤ 0.5） | 実験 |
|---|---|---|---|---|
| 共晶（Al 側） | 760–770 K、液相 x ≈ 0.31–0.32、fcc 0.15 ± 0.02 + B32 0.482 | 760–770 K、0.31、fcc 0.11 | 760–770 K、0.30、fcc 0.157 | 875 K、0.24、fcc ≈ 0.14 |
| 純 Al 融点 | 890–900 K | 850–860 K | 860–870 K | 933.6 K |
| B32 の融点（合致溶融） | 850–860 K | 840–850 K | — | 975 K |
| Al₂Li₃ | 安定。710–720 K で B32 + 液相に分解 | 限界的（30 回中 9 回） | — | 包晶 793 K で生成 |
| Al₄Li₉ | 安定。670–680 K で Al₂Li₃ + 液相に分解 | 700 K 以上で不安定 | — | 543 K で生成（同じ組成域の AlLi₂₋ₓ は 608 K まで） |
| Li 側（650 K） | Al₄Li₉(0.69) + 液相(0.78)。bcc Li は格子（≥ 650 K）に現れない（Li 融点 453 K） | 700 K 以上は B32 + 液相のみ | — | Li 融点 453.8 K、Li 側共晶 452 K |
| 64 原子 SQS − 32 原子ランダム平均（fcc、800 K） | −0.9、−0.9、+0.5、−2.9 meV/atom（x = 0.0625–0.25） | 同左 | ランダム 2 配置の半幅 0–1.7 meV/atom | — |

実験欄の出典：H. Okamoto, J. Phase Equilib. Diffus. 33, 500 (2012) Fig. 1（Hallstedt & Kim 2007 の評価、読み取り値は `資料/10.1007/s11669-012-0119-8/Fig1_readings.md`）。

メッシュ収束の効果：fcc Al の QHA 自由エネルギーは [4,4,4]（基本胞では 64 q 点）→ 60 Å の密度指定で 700 K −6.0、900 K −8.8 meV/atom 下がった（bcc Li −1.7 / −3.4、B32 −0.3）。これで Al 融点が 850 → 890 K に上がり、calphy の固液 TI だけで求めた例 4 の 902–927 K（seed 違い）と整合する。液相の run 間のばらつきは平均 0.1–0.2 meV/atom（最大 0.55）で、Monte Carlo の σ には下限 1.4 meV/atom を使った。誤差帯（30 サンプル）：770 K の fcc + 液相は fcc 0.11 ± 0.03・液相 0.29 ± 0.02、850 K は 0.04 ± 0.02・0.13 ± 0.05、B32 の Al 側端 0.481 ± 0.001。Al₂Li₃・Al₄Li₉ の安定域は 690 K で 30 回中 16 回 / 8 回なので、分解温度には ±20 K 程度の幅がある。

fit のノイズ：液相の下側凸包に幅 0.007（x = 0.47–0.48、850 K 以上）と幅 0.02–0.10（x = 0.88–0.98、650–750 K）の「liquid+liquid」区間が出る。Monte Carlo でも位置が動かない（標準偏差 0）ので、統計ノイズによる fit の曲率で、相境界ではない（REPORT.md に区間を列挙）。B32 の Li 側の端 x = 0.5625 は標本範囲の端。格子が 650 K で止まるのは、液相の run が全組成にある温度だけを使うため（x = 0.1 は 800 K、x = 0.5・0.6 は 700 K まで、650 K 以下は 8 組成）。REPORT.md の「Error bands」節は 01:22 の版では空だった（感度解析は格子を 1 つ飛ばしで評価するので 720/800/900 K が無い）。最寄りの温度を使うよう `write_report` を直して 08:18 に再生成した（数値は同じ）。所要時間：最初の連鎖 41 分（16:41–17:22）、追加液相 32 本 4.4 時間（GPU 直列）、密度メッシュ固相 14 分、組立 1 分未満。

### 7. Ni–Al（組成幅を持つ規則相）：Mishin 2009 EAM、mygardenx1 で Slurm 実行 — `nial_eam/` → `out/REPORT.md`

2026-10-22 22:06 に mygardenx1 へ投入（Slurm 14138 固相、14139–14171 液相 33 本、14172 組立）。**結果は `ftphase/examples/nial_eam/out/REPORT.md` と `out/07_phase_diagram.png`（mygardenx1 上）に自動で書かれる。**中断時は `run_resume.sh`。ポテンシャルは NIST の Purja Pun & Mishin 2009 EAM（`potentials/nial/`、B2 NiAl と Ni₃Al 向け）。

| 相 | セルと欠陥 | 配置項 |
|---|---|---|
| fcc(Al) | 64 原子 SQS、x_Ni = 0, 1/64, 2/64 | 理想混合 |
| fcc(Ni) | 64 原子 SQS、x_Ni = 0.75–1 | 理想混合 |
| B2 NiAl | 54 原子。Ni 過剰側は Ni 反サイト 1・2 個（x = 0.519, 0.537）、Al 過剰側は Ni 空孔 1・2 個（x = 0.491, 0.481） | 三重欠陥モデル `b2_triple_defect_site_fractions`（反サイト + 空孔、E10–E12） |
| L1₂ Ni₃Al | 108 原子、反サイト各 1 個（x = 0.741, 0.759） | 2 副格子反サイト（`b32_antisite_site_fractions(stoich_x=0.75)`） |
| Ni₂Al₃、NiAl₃ | 点相。この EAM では 0 K 凸包の 122、60 meV/atom 上（Al 側の金属間化合物は出ない） | なし |
| 液相 | 256 原子、x = 0–1（0.1 刻み）、calphy ts 2000 K → T_stop(x)（850–1500 K、組成で変える）、UFM、3 反復、別 seed 2 本を追加して平均 | TI に含まれる |

固相は QHA（0.97–1.09 の 13 体積、phonopy メッシュは密度指定 60 Å、低融点相は温度上限を下げ、最小が範囲外なら上限を 200 K ずつ縮めて続行）と、同じセルを 200 原子以上に複製した calphy TI（Einstein 結晶参照）の両方で評価し、組立は TI を使い QHA との差を報告する。組立は液相が 3 組成以上ある温度だけを使い、標本範囲の端で止まる境界には `edge=True` を付ける（幅の下限）。液相の fit は両端があれば理想混合 + Redlich–Kister、無い温度では多項式に自動で切り替える。投入前に、固相 6 セルの QHA と、合成液相を使った組立を手元で通して確認した。

結果（第 3 段、組立 2026-10-22 22:50、固相 25 セルは calphy TI、`out/REPORT.md`、`out_mygardenx1/` に複製）：

| 特徴 | EAM（本計算、古典） | 実験 |
|---|---|---|
| B2 NiAl の合致溶融 | 1880–1890 K | 1911 K |
| 純 Ni / 純 Al の融点 | 1740–1750 K / 921 K | 1728 / 933.5 K |
| L1₂ Ni₃Al の消失（B2 + L1₂ → B2 + 液相） | 1690–1700 K | 包晶 1668 K |
| B2 の組成幅 | x_Ni = 0.50–0.611（1000–1850 K）。Ni 側は標本の端 0.611 で頭打ち（幅はそれ以上）、Al 側は 0.50 で空孔による幅がほぼ出ない | 0.45–0.60 |
| L1₂ の幅 | 0.762–0.778（1000 K）、Ni 側は標本の端 | 0.73–0.77 |
| (Ni) の Al 固溶限 | x_Ni = 0.92（1000 K）→ 0.89（1700 K） | 0.79–0.87 |
| Al 側の液相線 | x_Ni = 0.155（1000 K）→ 0.45（1850 K）、liquid + B2（NiAl₃・Ni₂Al₃ は EAM で不安定） | NiAl₃、Ni₂Al₃ が存在 |

段階ごとの違い：第 1 段（QHA 固相）は Ni の融点が 1500 K 未満、B2 合致溶融 1739 K。第 2 段（固相を calphy TI に）で 1900 K・1745 K。第 3 段で B2 の反サイト 3〜6 個・空孔 3〜4 個と L1₂ の反サイト 2〜3 個を追加し、副格子エントロピーを解析的に分離して欠陥エネルギーを枝ごと（反サイト側・空孔側）に線形 fit する `entropy_models` を導入した。これで標本ノイズ由来の偽の B2+B2 二相域（0.52–0.60）が消え、残るのは化学量論組成の尖点に由来する幅 0.01 以下の B2+B2（1820–1880 K）だけになった。この尖点は単一欠陥種の副格子モデルの限界で、熱的な欠陥対を入れた Wagner–Schottky 型モデルが次の改良点。

**この例で分かった最も重要なこと：準調和（QHA）の固相自由エネルギーは、この EAM では融点付近で calphy の TI より 20〜45 meV/atom 高い**（fcc Ni 1500 K で +43、L1₂ +36、B2 +5〜16 meV/atom。`REPORT.md` の QHA−TI 表）。原因の一部（Ni で約 18 meV）は phonopy の `primitive_matrix='auto'` と固定メッシュ `[4,4,4]` の組合せで純元素・規則相のセルだけ q 点が 64 個に減っていたこと（`MESH_LENGTH = 60`〔Å〕の密度指定に変更、例 6 も再計算中）、残りは非調和性。T_m の 0.8 倍を超える温度では固相も calphy TI（workflow の補助経路）で評価するのが正しい。

実験値（比較用）：NiAl 合致溶融 1911 K、B2 の幅 約 0.45–0.60、Ni₃Al 包晶 1668 K、L → Ni₃Al + (Ni) 共晶 1658 K（x ≈ 0.76）、(Ni) の Al 固溶 約 0.21、Al 側共晶 913 K。

## AiiDA ワークフロー（工程 01–07 を 1 本の WorkChain で、2026-10-23）

`ftphase.aiida`（`src/ftphase/aiida/`）は同じ工程を AiiDA 2.9 のプラグインにしたもの。entry point は `ftphase.qha`（CalcJob：1 セルの phonopy QHA、計算ノードで `ftphase-qha-run input.json`）、`ftphase.calphy`（CalcJob：calphy 計算 1 ブロック、`calphy_kernel -i input.yaml -k 0`）、`ftphase.txdiagram`（WorkChain：calcfunction `prepare_cells` → QHA と calphy を並列投入 → `inspect` → calcfunction `assemble_diagram`）。重い計算だけ Slurm、緩和・凸包・組立はデーモン worker 内。投入後はデーモンと Slurm が完走させ、入力・各セル・配列・REPORT.md・図が provenance 付きで残る。

- 環境は `env/ftphase`（aiida-core 2.9.3 追加）。プロファイル `ftphase`（SQLite + RabbitMQ）、計算機 `mygarden5`（core.local + core.slurm、`~/aiida_run/ftphase`）、コード `ftphase-qha@mygarden5`・`calphy@mygarden5`。`verdi` は必ず `env/ftphase/bin/verdi -p ftphase`（既定プロファイルは別プロジェクトの `alamode_pg`）。設定は `examples/aiida_txdiagram/setup_aiida.sh`（冪等）。
- プラグインを変えたら `pip install -e ./ftphase --no-deps` のあと `verdi -p ftphase daemon restart`。
- 投入は `examples/aiida_txdiagram/run_aiida.py`（`--smoke`、`--dry-run`、`--no-gpu`）、取り出しは `fetch_results.py <pk|name>`。spec の書き方・失敗の診かた・落とし穴（QHA 走査範囲、デーモンが書き出す `PYTHONPATH` が計算ノードの `conda` を壊す → 計算機 prepend に `unset PYTHONPATH PYTHONHOME`）は `examples/aiida_txdiagram/README.md`。
- テスト `tests/test_aiida.py`（一時 SQLite プロファイル、投入なし）：entry point、両 CalcJob の入力生成（`__WORKDIR__` の置換、GPU の `pace product`・KOKKOS 引数）、calphy パーサ（例 5 の実 `report.yaml` / `temperature_sweep.dat`）、QHA パーサと exit code、`prepare_cells` の実行（ACE で 01/02 を通す）。

### 8. AiiDA 版 T–x 図：ACE Al–Li、例 5 と同じ物理 — `aiida_txdiagram/` → `out/alli_ace/`

煙試験（pk 118）は 3 分で `assemble_diagram` まで通過。本番 pk 191（2026-10-23 11:34 投入、12:27 完了、53 分；QHA 13 セル・密度メッシュ 60 Å、GPU 液相 6 本 × 3 反復、全 19 CalcJob が exit 0）：共晶 760–770 K・液相 x ≈ 0.32・fcc 0.164 + B32 0.482、純 Al 融点 880–890 K（例 5 の 860–870 K から密度メッシュの分だけ上昇、例 6 と同じ向き）、B32 側の液相線の終わり 850–860 K、Al₃Li は 700 K 以上で現れない。共晶の温度・組成・固溶限は例 5 と 0.01 以内で一致。700–790 K に幅 ≤ 0.09 の fcc+fcc 帯（x = 0.03–0.12）が出るが、32 原子 2 配置の配置ノイズを過剰項の 3 次多項式が拾ったもの（例 6 の 64 原子 SQS / Redlich–Kister で消える種類）。詳細は `aiida_txdiagram/README.md` の「結果」節と `out/alli_ace/REPORT.md`。

### 02A 補足：sqsgenerator と icet の比較（Al–Li、ACE、2026-10-23）— `alli_sqs_compare.py` → `out_alli_ace/sqs_compare.{md,json}`

`structures.sqs_sqsgenerator` は sqsgenerator 0.5.6 に無い `sqs_optimize` を呼んでいて動かなかったので、0.5 の API（`parse_config` → `optimize` → `best()`、`structure()`・`sro()` はメソッド）に書き直した（テスト `test_sqs_sqsgenerator_counts_and_metadata`）。fcc Al–Li の 32・64 原子セル、x_Li = 1/16, 1/8, 1/4 で random 置換・icet（固定超格子 MC、cutoff 7.0/5.0 Å）・sqsgenerator（Warren–Cowley 5 殻、5 × 10⁵ 反復）を比較（Slurm 22731、14 分）：

| 指標 | icet | sqsgenerator | random |
|---|---|---|---|
| 生成時間 | 4–6 s | 0.1–0.3 s | 0 s |
| icet クラスターベクトル残差（64 原子） | 0.02–0.11 | 0.11–0.31 | 0.21–0.51 |
| 第 1 殻 α_AlLi | 0.00〜−0.02 | 0.00〜−0.07 | 0.00〜−0.07 |
| E0 − E0(icet)、64 原子 | 0 | +0.1〜+1.2 meV/atom | −1.3〜+0.7 meV/atom |
| G(800 K) − G(icet)、64 原子、x = 1/8 | 0 | +0.9 meV/atom | +0.7 meV/atom |
| 同、32 原子 | 0 | −1.7 meV/atom（E0 −2.9） | −0.5 meV/atom（E0 −1.2、x = 1/4 で −3.7） |

結論：64 原子以上では生成法の差は約 1 meV/atom で配置ノイズ（半幅 ≤ 2 meV/atom）の内側。既定は icet（三体相関まで最適化し残差が最小）、多数の組成を素早く作るときは sqsgenerator でよい。32 原子では生成法で最大 3.7 meV/atom 動くので、例 5 の 32 原子ランダム 2 配置の平均は妥当な下限の扱いだった。

### 9. Ag–Cu（共晶 + fcc ミシビリティギャップ）：Williams–Mishin–Hamilton 2006 EAM、AiiDA、固相は calphy TI — `aiida_txdiagram/run_aiida.py --system agcu` → `out/agcu_eam/`

例 8 の WorkChain に固相の calphy TI（`spec["solids_ti"]`）を加えて、fcc 固溶体 1 相を全組成で標本化する系。ポテンシャルは NIST の `potentials/agcu/CuAg.eam.alloy`（Williams, Mishin, Hamilton, MSMSE 14, 817 (2006)、setfl の元素順 Cu Ag、`pair_coeff * * CuAg.eam.alloy Ag Cu`）。
固相：fcc 32 原子ランダムセル × 2 配置、x_Cu = 0, 1/32, 2/32, 4/32, 8/32, 12/32, 16/32, 20/32, 24/32, 28/32, 30/32, 31/32, 1（23 セル）。QHA（0–1400 K、密度メッシュ 60 Å、長さ比 0.96–1.08）と、同じセルを 2×2×2 に複製した 256 原子の calphy 固相 ts（900 K → 1360–1480 K、組成で補間）を並行して走らせ、組立では 900 K 以上を TI、以下を QHA にする。
液相：256 原子、x_Cu = 0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0、calphy ts 1500 → 950 K（純 Ag は 1050 K、純 Cu は 1100 K まで）、GPU。fit は fcc・液相とも理想混合 + 4 項 Redlich–Kister。格子 900–1400 K。

実験（NIST の Ag–Cu はんだ相図ページ、Hayes 1986 の評価；Subramanian & Perepezko 1993）：共晶 1052 K、液相 x_Cu ≈ 0.40、(Ag) の Cu 固溶限 0.133–0.141、(Cu) の Ag 固溶 0.045–0.049（x_Cu 0.95–0.955）、Ag 融点 1235 K、Cu 融点 1358 K。
他の理論：Nitol ら 2025（arXiv 2508.18129、MTP、二相共存 MC）：共晶 1001 K、液相 x_Ag = 0.57、固溶限 Cu in Ag 0.04・Ag in Cu 0.099、Ag 融点は実験より約 100 K 低い。

煙試験 pk 346（2026-10-23 16:13 投入）で WorkChain の新経路（固相 TI、TI だけのセル、QHA の温度範囲自動短縮）を確認。本番の投入・結果は下に追記する。

## 既知の制限

- calphy の `n_iterations: 1` では誤差が 0 と報告される。例 3・4 の融点には上の統計ばらつき（±10 K 程度）が付く。

- 二元系のみ（三元以上は TDB → pycalphad の経路）。例 5・8 は x ≤ 0.5 の Al 側だけ。
- AiiDA 版は WorkChain の再開（失敗セルだけの再投入）とキャッシュを使っていない。失敗したセルは除外して組み立てるので、直したら WorkChain 全体を再投入する。
- `sqs_sqsgenerator` は sqsgenerator 0.5 の API を仮定しており未テスト。icet 経路を使う。
- CE+MC そのもの（icet の学習・MC 実行）はラップしていない。状態密度・F_conf の受け取り口（E13）だけがある。
- 04B の補正は調和近似。液相側の量子効果は扱わない。
- 誤差伝播は相ごとの一様なオフセット（＋任意の傾き）のみ。

## 出典

- calphy: S. Menon, Y. Lysogorskiy, J. Rogal, R. Drautz, Phys. Rev. Mater. 5, 103801 (2021); https://github.com/ICAMS/calphy （`phase_diagram.py` の `PhaseDiagram` / `to_tdb`、2026-05〜07）
- pyiron potentials-workshop-2022 `phase_diagram/helpers.py`（共通接線の fsolve）: https://github.com/pyiron/potentials-workshop-2022 ；S. Menon et al., npj Comput. Mater. 10, 261 (2024)
- phonopy: A. Togo, J. Phys. Soc. Jpn. 92, 012001 (2023); https://phonopy.github.io/phonopy/qha.html
- ALAMODE: T. Tadano, Y. Gohda, S. Tsuneyuki, J. Phys.: Condens. Matter 26, 225402 (2014); aiida-alamode 1.1（本ホスト）
- icet: M. Ångqvist et al., Adv. Theory Simul. 2, 1900015 (2019); https://icet.materialsmodeling.org
- sqsgenerator: D. Gehringer, M. Friák, D. Holec, Comput. Phys. Commun. 286, 108664 (2023)
- pycalphad: R. Otis, Z.-K. Liu, J. Open Res. Softw. 5, 1 (2017)
- pymatgen: S. P. Ong et al., Comput. Mater. Sci. 68, 314 (2013)
- smol（Wang–Landau の状態密度の受け口）: L. Barroso-Luque et al., JOSS 7, 4504 (2022)
- 凸包: A. M. Andrew, Inf. Process. Lett. 9, 216 (1979)（単調鎖）
- 本プロジェクトの式: `docs/workflow.html`（eq-A1 … eq-J2）
