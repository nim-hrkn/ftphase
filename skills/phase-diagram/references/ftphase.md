# ftphase パッケージ（2026-10-21 作成、プロジェクトの `ftphase/`）

[examples.md](examples.md) で公開例に無かった工程と、[public-sources.md](public-sources.md) で挙げた公開コードを、薄く一本につないだ Python パッケージ。環境は `env/ftphase`（calphy 2.3.0、LAMMPS、phonopy、pymatgen、icet 4.0、sqsgenerator、pycalphad 0.11.2）。長い説明と実行結果は `ftphase/README.md` と `docs/ftphase.html`。

## 工程 → モジュール

| 工程 | モジュール | 主な関数 |
|---|---|---|
| 01 | `ftphase.validate` | `relax`（空間群変化を検出）、`hull_0K`、`compare_ground_states`（既知相を黙って置換しない）、`eos_scan`、`melting_check_inputs` |
| 02A | `ftphase.structures` | `composition_series`（整数原子数、seed、副格子占有数）、`vacancy_series`（空孔＝原子の欠損）、`sqs_icet`（副格子・空孔 X、クラスターベクトル残差）、`write_lammps_data` |
| 03A | `ftphase.qha` | `harmonic_free_energy`（量子/古典、虚振動は例外）、`fit_eos`、`qha_gibbs`（式 D2、最小が範囲外なら例外）、`phonopy_volume_scan`、`read_anphon_thermo` |
| 03B | `ftphase.calphy_io` | `calculation_block`（`gpu=True` で KOKKOS/CUDA、`pace` → `pace product`、gres）/ `write_series_input` / `slurm_queue`、`gpu_capability`（`lmp -h` から pace/kk・hybrid/scaled/kk を確認）、`read_calphy_results`（古典・配置項フラグ付き） |
| 04A | `ftphase.configurational` | `ideal_entropy`、`exact_entropy`、`sublattice_entropy`（E10–E12、空孔・基準）、`b32_antisite_site_fractions`、`free_energy_from_density_of_states`（E13） |
| 04B | `ftphase.quantum` | `quantum_minus_classical`、`lift_classical_to_quantum` / `lower_quantum_to_classical` |
| 05 | `ftphase.records`, `ftphase.assemble` | `FreeEnergyTable`（必須列と `check()`）、`relative_to_pure`（G1）、`add_configurational_term`（二重計上を拒否）、`interpolate_T`、`builder_from_table`、`fit_residuals`、`to_calphy_phase_diagram`（→ calphy `to_tdb`）、`check_with_pycalphad` |
| 06 | `ftphase.equilibrium` | `PhaseCurve` / `PointPhase`、`equilibrium_at_T`（点相・限定組成相を含む下側凸包＋H3 の精密化）、`Coexistence.mu` / `.lever`、`regular_solution_binodal` |
| 07 | `ftphase.diagram` | `scan`、`invariants`、`sensitivity`（Monte Carlo）、`plot_tx`（温度ごとの帯）、`write_records` |

CLI：`ftphase check`、`ftphase diagram`、`ftphase hull0k`。

AiiDA 層（`ftphase.aiida`、2026-10-23）：CalcJob `ftphase.qha`（1 セルの QHA、`ftphase-qha-run`）、`ftphase.calphy`（calphy 1 ブロック、`calphy_kernel`、パスは `__WORKDIR__` → `$PWD`）、WorkChain `ftphase.txdiagram`（calcfunction `prepare_cells` 01/02 → CalcJob 並列 03A/03B → `inspect` → calcfunction `assemble_diagram` 04–07）。例と手順は `ftphase/examples/aiida_txdiagram/README.md`。

## 使うときの判断

- 表の `kind` は solution / point / limited。限定組成相は `limited` にして外挿を防ぐ。点相（line compound）は `point`。
- `config_entropy` 列が `none` 以外の相には配置項を足せない（液相 TI は `liquid-ti`）。B32 型の規則相は `b32_antisite_site_fractions` のような副格子モデルを渡す。
- `quantum` 列が混在すると `check()` が警告する。calphy（古典）と QHA（量子）を混ぜるときは `ftphase.quantum` でどちらかにそろえ、`method` 列に書く。
- fit は `spline`（補間）、`poly`（チュートリアル互換。理想混合を含む相は過剰項だけが fit される）、`rk`（Redlich–Kister、端点が要る）。`fit_residuals` で残差を見る。Al–Li EAM の 6 点データでは fit の形だけで共晶温度が約 85 K 動いた。
- GPU で ACE：conda-forge の LAMMPS 22 Jul 2025 には `hybrid/scaled/kk` が無く、calphy は固相 fe 以外で `hybrid/scaled` を使うので `-k on` では止まる。`env/lammps-gpu/bin/lmp_gpu`（stable 30 Sep 2026、`build.sh`）を `lammps_executable` に渡す。1 GPU = MPI 1 ランク。 注意点：GPU 1 枚ではジョブが直列になるため、総スループットは CPU 8 コアと同程度です。利点は 1 本の待ち時間短縮と、CPU を QHA に空けられることです。
- `sensitivity` に calphy の `G_err` や QHA の見積もり誤差（meV/atom）を渡し、境界の標準偏差を必ず記録する。

## AiiDA で回すとき（profile `ftphase`）

- `verdi` は `env/ftphase/bin/verdi -p ftphase`。既定プロファイル `alamode_pg`（別プロジェクト）とそのデーモンには触らない。
- 計算機 `mygarden5`（core.local + core.slurm、`~/aiida_run/ftphase`）、コード `ftphase-qha@mygarden5`・`calphy@mygarden5`、デーモン 2 worker（`setup_aiida.sh`）。投入は `run_aiida.py`（`--smoke` / `--dry-run` / `--no-gpu`）、取り出しは `fetch_results.py`。
- プラグインを変えたら `pip install -e ./ftphase --no-deps` → `verdi -p ftphase daemon restart`。
- 失敗は `process status` の exit code（QHA 300 出力無し、calphy 300/310/320、WorkChain 401/402/410）→ `calcjob outputcat <pk> -p qha.err`。失敗セルは除外して組み立てるので、直したら再投入。
- 落とし穴：デーモンが `PYTHONPATH` を書き出して計算ノードの base `conda` を壊す（計算機 prepend に `unset PYTHONPATH PYTHONHOME`）。QHA の走査範囲は 1100 K で 1.05 以上。WorkChain を kill しても子が残ることがある。

## 検証済みの事実（2026-10-21）

- pytest 50 件 + skip 1（2026-10-23；AiiDA 8 件を含む。解析解：正則溶体の binodal、Einstein 結晶、二次 E0(V) の QHA、Stirling、2 準位系の状態密度、phonopy の規格化）。
- Al–Li EAM（workshop データ）：理想混合＋poly3 で共晶 904–906 K、spline で 818–820 K。B32 を副格子で扱うと 800 K で既に液相が入る。
- Al–Li ACE：Al₃Li が ACE の凸包上に乗る（B32–fcc の弦より 4.6 meV/atom 下）。fcc Al の F_q − F_cl は 300 K で 3.4、1000 K で 1.0 meV/atom。
- 01 から 07 を通した例（2026-10-22、`examples/alli_ace_txdiagram/`、Slurm + GPU、セッション非依存）：ACE Al–Li の Al 側。共晶 760–770 K・x ≈ 0.30（実験 875 K・0.24、Okamoto 2012）、fcc 固溶限 0.157、純 Al 融点 860–870 K、Al₃Li は 700 K 以上で不安定。温度は実験より約 100 K 低いが組成の特徴は合う。1 時間（液相 GPU 6 本 × 8.5 分が支配）。
- 例 6（`pipeline_full.py`、2026-10-22 16:42 投入）：64 原子 SQS の fcc/bcc と Li 側液相で 0 ≤ x ≤ 1 の図。最終結果（2026-10-23 01:22、密度メッシュ 60 Å の固相 + 液相 11 組成 × 3–4 run の平均、格子 650–1100 K）：共晶 760–770 K・x ≈ 0.31（fcc 0.15 ± 0.02 + B32 0.482）、Al 融点 890–900 K（[4,4,4] メッシュでは 850–860 K：fcc Al の F が 900 K で 8.8 meV/atom 高かった）、B32 合致溶融 850–860 K、Al₂Li₃（mp-16506）は 710–720 K まで、Al₄Li₉（mp-568404）は 670–680 K まで安定（実験 ≈790 / ≈600 K）。64 原子 SQS にしても共晶温度は変わらず（温度の −100 K はポテンシャル側）。液相は `fits={'liquid':'rk'}` + `ideal_T`（理想混合 + Redlich–Kister）で fit する。幅 < 0.1 の liquid+liquid 区間は fit ノイズ。詳細 `examples/alli_ace_txdiagram/out_full/REPORT.md`。`sqs_icet(method='supercells', supercells=[...])` で固定 64 原子セルの SQS が 5 秒。bcc Li の QHA は体積走査 0.96–1.14 が要る（+5 % では最小が範囲外）。
- 例 9 Ag–Cu（2026-10-23、Williams 2006 EAM）：A（TI + 凸包、`aiida_txdiagram/reassemble_agcu.py`：端成分 fcc を fccAg/fccCu に分けて組み立てる）と B（SGC MC、`agcu_sgcmc/sgcmc.py`）の固溶限は 800–900 K で 0.015 以内。二相共存 MD（`coexist.py`）の融点 Ag 1265–1290 / Cu 1325–1350 K は原著者と一致し、calphy TI 経路は +35〜50 K 高い：1275 K で 256 原子・切り替え 10k の fe は G_s − G_l = −5.9 meV（切り替え 50k で +1.9 meV 戻る）。固液 TI は切り替え長とセルを増やす。
- 04A 熱的欠陥（2026-10-23）：`configurational.wagner_schottky_free_energy`（最大 4 種の点欠陥、組成拘束を線形消去して最小化）、`defect_energies_from_cells`（標本セルから各 T の有効欠陥自由エネルギー）、`builder_from_table(entropy_models={ph: ("wagner_schottky", (a, b))})`。Ni–Al 第 4 段（`nial_eam/reassemble_ws.py`）で化学量論組成の尖点と偽の B2+B2 区間が消えた。希薄・非相互作用、短距離秩序は CE+MC の範囲。
- 02A の生成法比較（2026-10-23、`examples/alli_sqs_compare.py`）：sqsgenerator 0.5.6 は `parse_config`→`optimize`（wrapper を移植済み）、0.1–0.3 s で生成、icet の固定超格子 MC は 4–6 s。64 原子では icet・sqsgenerator・random の 0 K/800 K 自由エネルギー差 ≤ 1.2 meV/atom、32 原子では最大 3.7 meV/atom。icet のクラスターベクトル残差は icet が最小（64 原子 0.02–0.11）。既定は icet。
- Al–Li の実験相図の基準：Okamoto 2012（J. Phase Equilib. Diffus. 33, 500、Fig. 1 = Hallstedt & Kim 2007 評価）：共晶 875 K・x_Li ≈ 0.24・(Al) 固溶限 ≈ 0.14、AlLi 合致溶融 975 K、Al₂Li₃ 包晶 793 K、AlLi₂₋ₓ 608 K、Al₄Li₉ 543 K、Li 側共晶 452 K。読み取り値は `資料/10.1007/s11669-012-0119-8/Fig1_readings.md`。
- 例 7 Ni–Al（`examples/nial_eam/`、Mishin 2009 EAM、mygardenx1）：B2 の三重欠陥モデル `b2_triple_defect_site_fractions`、L1₂ の反サイト、固相は QHA と calphy TI の両方。B2 合致溶融 1885 K（実験 1911）、Ni 1745 K、L1₂ は 1695 K まで（実験 1668）、B2 の幅 0.50–0.611（Ni 側は標本の端）。規則相の fit は `builder_from_table(entropy_models={phase: (site_model, stoich_x)})` で副格子エントロピーを分離し欠陥エネルギーを枝ごとに線形 fit する（スプラインだと標本ノイズで偽の二相域が出る）。**融点付近の QHA は TI より 20–45 meV/atom 高い**（非調和 + メッシュ）。T_m の 0.8 倍以上では固相も calphy TI にする。phonopy のメッシュは密度（`mesh=60.0` Å）で指定し、固定 [4,4,4] を基本胞の小さいセルに使わない。
- 多項式 fit は G にそのまま当てない：理想混合項を解析的に分離して過剰項だけを fit（`builder_from_table` の `ideal_excess_fit`、既定で有効）。そうしないと偽の fcc+fcc / liquid+liquid 帯が出る。
- GPU（2026-10-22）：calphy ts を `lmp_gpu`（LAMMPS 30 Sep 2026 KOKKOS/CUDA）で実行。1 ランク GPU が CPU 4 ランクの 1.7〜3.3 倍速、1 点のエネルギー・圧力は全桁一致。別 seed 4 サンプルの G の標準偏差は 900 K で 1.3〜1.4 meV/atom、純 Al の融点は 902–927 K に散る（5000+5000 ステップ、1 反復）。`n_iterations ≥ 3` にして `G_err` を使うこと。
- phonopy を `primitive_matrix='auto'` で使うと F は基本胞あたりになる。入力セルあたりへの換算を忘れると 4 倍小さくなる（修正済み、回帰テスト有り）。
- AiiDA 版（例 8、`examples/aiida_txdiagram/`、2026-10-23）：煙試験 pk 118 が 3 分で REPORT.md まで通過。本番 pk 191（例 5 と同じ物理、密度メッシュ 60 Å）は 53 分で完走（19 CalcJob すべて exit 0）：共晶 760–770 K・x ≈ 0.32・fcc 0.164 + B32 0.482、Al 融点 880–890 K（例 5 の 860–870 K からメッシュの分だけ上昇）、B32 側 850–860 K。例 5 と 0.01 以内で一致。700–790 K の幅 ≤ 0.09 の fcc+fcc 帯は 32 原子 2 配置の配置ノイズ（例 6 の 64 原子 SQS / rk で消える種類）。結果 `out/alli_ace/REPORT.md`。
