# 例 8. AiiDA ワークフロー：工程 01–07 を `TxDiagramWorkChain` で（ACE Al–Li、Slurm + GPU、2026-10-23）

例 5（`alli_ace_txdiagram/`）と同じ物理（ACE `AlLi-6gen-18May.yace`、Al 側 x_Li ≤ 0.5、fcc ランダム固溶体、B32 反サイト、L1₂ Al₃Li 点相、calphy 液相 1100 → 700 K を GPU）を、
Slurm の依存チェーンではなく **AiiDA の WorkChain** として走らせる。投入後は AiiDA デーモンが WorkChain を進め、Slurm が CalcJob を走らせるので、
Claude のセッションやログインシェルを閉じてよい。すべての入出力（spec、ポテンシャル、各セル、QHA の配列、calphy の sweep、REPORT.md、図）が provenance 付きで DB に残る。

## 構成

```
run_aiida.py  ──submit──▶  TxDiagramWorkChain (entry point ftphase.txdiagram)            [デーモン worker]
                              │
                              ├─ prepare_cells (calcfunction)        01 緩和 + 0 K 凸包 / 02A 固相セル / 02B 液相セル   数十秒、worker 内
                              │     └─ 出力: hull, solid_params, liquid_params, solid_<key>, liquid_<tag> (StructureData)
                              ├─ QhaCalculation × N_solid  (ftphase.qha)     03A  Slurm CPU 4 コア  `ftphase-qha-run input.json`
                              │     └─ 出力: results (Dict), arrays (ArrayData: T, G, V, hw_eV, weights, volumes, e0, f_vib)
                              ├─ CalphyCalculation × N_liq (ftphase.calphy)  03B  Slurm GPU 1 枚    `calphy_kernel -i input.yaml -k 0`
                              │     └─ 出力: results (report.yaml), sweep (ArrayData: temperature, free_energy, error)
                              ├─ inspect     失敗した CalcJob を報告して除外（固相 0 → exit 402、液相 0 → exit 401）
                              └─ assemble_diagram (calcfunction)     04A/04B/05/06/07  → summary, report (REPORT.md), figure (png), free_energies,
                                                                       regions, invariants, sensitivity, fit_residuals (SinglefileData)   数秒
fetch_results.py <pk|name>   出力ノードを out/<name>/ にファイルとして書き出す
```

- `ftphase/src/ftphase/aiida/`：`calculations.py`（CalcJob 2 種）、`parsers.py`、`functions.py`（calcfunction 2 種）、`workchains.py`、`runners.py`（計算ノードで動く `ftphase-qha-run`）。entry point は `ftphase/pyproject.toml`。
- 計算ノードでは **同じ `env/ftphase`** を使う（コードの prepend_text が `conda activate`）。calphy の入力ではパスを `__WORKDIR__/...` と書き、ジョブスクリプト先頭の `sed` で `$PWD` に置換する（AiiDA はジョブ dir を事前に決めないため）。
- 重い計算は CalcJob（Slurm）、軽い処理は calcfunction（デーモン worker 内）。prepare_cells の緩和は ACE の 4 候補で約 15 秒。

## AiiDA の設定（`setup_aiida.sh`、1 回だけ）

| もの | 値 |
|---|---|
| プロファイル | `ftphase`（`verdi presto`：SQLite ストレージ + 動いていれば RabbitMQ）。**既定プロファイルは `alamode_pg` のまま**なので `verdi` は常に `-p ftphase` |
| verdi | `env/ftphase/bin/verdi -p ftphase`（aiida-core 2.9.3 は `env/ftphase` に入っている。conda env `alamode` の verdi とは別物） |
| 計算機 | `mygarden5`：core.local + core.slurm、作業 dir `~/aiida_run/ftphase`、prepend_text `unset PYTHONPATH PYTHONHOME`（下の落とし穴 2） |
| コード | `ftphase-qha@mygarden5`（`env/ftphase/bin/ftphase-qha-run`、plugin `ftphase.qha`）、`calphy@mygarden5`（`env/ftphase/bin/calphy_kernel`、plugin `ftphase.calphy`） |
| デーモン | `verdi -p ftphase daemon start 2`。ログ `~/.aiida/daemon/log/aiida-ftphase.log` |

スクリプトは冪等（既にあるものは作らない）。環境変数 `AIIDA_FTPHASE_PROFILE / _COMPUTER / _WORKDIR / _WORKERS`、`CONDA_SH` で変えられる。

**プラグイン（`ftphase/src/ftphase/aiida/*.py`）や `ftphase` 本体を変えたら必ず**

```bash
./env/ftphase/bin/pip install -e ./ftphase --no-deps && ./env/ftphase/bin/verdi -p ftphase daemon restart
```

worker は起動時のコードを掴んだままなので、再起動しないと古いコードで走り続ける（calcfunction は worker 内で動くため特に）。

## 投入・監視・取り出し

```bash
cd PhaseDiagram
env/ftphase/bin/python ftphase/examples/aiida_txdiagram/run_aiida.py --smoke      # 煙試験（fcc 2 + B32 3 セル、液相 2 本 × 1000 steps、約 5 分）
env/ftphase/bin/python ftphase/examples/aiida_txdiagram/run_aiida.py              # 本番 alli_ace（QHA 13 セル、GPU 液相 6 本）
env/ftphase/bin/python ftphase/examples/aiida_txdiagram/run_aiida.py --dry-run    # spec を表示するだけ
env/ftphase/bin/python ftphase/examples/aiida_txdiagram/run_aiida.py --no-gpu --cpu-cores 4   # GPU の無いホスト
env/ftphase/bin/verdi -p ftphase process status <pk>     # 木（各 CalcJob の exit code）
env/ftphase/bin/verdi -p ftphase process report <pk>     # WorkChain の報告（凸包の判定、失敗したセル、組立結果）
env/ftphase/bin/verdi -p ftphase process list -a -p 1    # 直近 1 日の全プロセス
env/ftphase/bin/python ftphase/examples/aiida_txdiagram/fetch_results.py alli_ace   # out/alli_ace/{REPORT.md,07_phase_diagram.png,*.tsv,*.json,calcjobs.tsv}
```

`run_aiida.py` は投入直後に `out/<name>.pk.json`（pk、uuid、時刻）を書き、`out/submissions.log` に追記する。`fetch_results.py` は pk でも名前でもよい。

## spec の書き方（`run_aiida.py` の `make_spec`）

WorkChain の入力は `spec`（Dict）、`potential`（SinglefileData）、`candidates`（名前 → StructureData。名前の非英数字は `_` にする）、`qha_code`、`calphy_code`、`qha_options` / `calphy_options`（CalcJob の `metadata.options`：`resources`、`queue_name`、`custom_scheduler_commands` に `#SBATCH --gres=gpu:1`）、`calphy_extra`（全 calphy ブロックに混ぜる `gpu`、`lammps_executable`、`cores`）、`skip_liquids`。

| spec のキー | 意味 |
|---|---|
| `elements`, `masses`, `x_element` | 元素順（LAMMPS の型順）、質量、組成軸の元素 |
| `pair_style`, `pair_coeff`（`{potential}` を含む）, `atom_types` | LAMMPS の設定。`{potential}` は計算ノード上の絶対パスに置換される |
| `candidates: {name: x}`, `known_ground_states: [name]` | 01 の候補と既知の基底状態。凸包上なのに既知リストに無い相は「MLIP ground state not in known list」と報告（止めない） |
| `relax: {fmax, cell}` | 01 の緩和 |
| `solids: [ {phase, kind, base, repeat, x, n_configs, series, seed, supercell, mesh, antisites, icet} ]` | 02A。`kind` は solution / limited / point。`antisites: true` で基底セルと x ∓ 1/N の反サイトセル、`series: sqs` で icet SQS、既定はランダム置換。`supercell` と `mesh`（長さ Å か [n,n,n]）は QHA の設定 |
| `liquids: {base, repeat, x, seed, T_sweep, T_override, n_repeats, n_equilibration_steps, n_switching_steps, n_iterations, mode, pressure}` | 02B/03B。`T_override: {"0.1": 800}` で特定組成の終端温度を変える（凝固する組成） |
| `qha: {T_max, T_step, scales, eos, imaginary, relax}` | 03A。`scales` は長さ比。1100 K では 1.05 以上が要る（下の落とし穴 1） |
| `assemble: {T_min, T_max, T_step, fits, poly_order(s), config_terms, entropy_models, sigma, hull, drop_edge_beyond_liquid, sensitivity_samples, title, xlabel, liquid_sigma_floor}` | 04–07。`config_terms` は `ideal` か `sublattice:<site model>`（`b32_antisite`、`b2_triple_defect`） |

## 失敗の診かた

1. `verdi -p ftphase process status <pk>` で exit code を見る。QHA 300 = 出力無し（`qha.err` にトレースバック）、calphy 300 = report.yaml 無し、310 = 融解/凝固で停止、320 = ts なのに sweep 無し。WorkChain 401/402 = 液相/固相が 1 本も終わらなかった、410 = 組立で例外（`process report` に `assembly failed: ...`）。
2. 取得済みファイルは `verdi -p ftphase calcjob outputcat <pk> -p qha.err`（`calphy.err`、`_scheduler-stderr.txt`、`input.yaml`、`*/calphy.log`）。ジョブ dir は `verdi -p ftphase calcjob res <pk>` か Python で `load_node(pk).get_remote_workdir()`。`calcjob gotocomputer` は対話シェルを開くのでスクリプトからは使わない。
3. 失敗したセルは WorkChain が報告して除外し、残りで組み立てる（REPORT.md の `missing`）。直してから再投入する（AiiDA のキャッシュは使っていない）。
4. WorkChain を止めるときは `verdi -p ftphase process kill <pk> -F -t 60`。子の CalcJob が `Waiting` で残ることがあるので `process status` で確認して個別に kill する（Slurm 側の `aiida-<pk>` も消える）。
5. `process report` に出る `could not parse scheduler output: return value of detailed_job_info is non-zero` は Slurm の `sacct`（会計が無効）由来の警告で無害。

### 見つかった落とし穴

1. **QHA の体積走査範囲**：煙試験の 0.97–1.03（長さ）では fcc Al の 1100 K の最小体積が範囲外（`EOS minimum V0 outside sampled range`）。例 5 と同じ 0.97–1.05 でも B32 は 1100 K で際どい。走査は広めに（煙試験は 0.97–1.07）。外挿はしない。
2. **デーモンが `PYTHONPATH` を書き出す**：AiiDA の worker は自分の `sys.path` を `PYTHONPATH` に入れて起き、Slurm ジョブ（`--get-user-env` でも `sbatch` の既定 `--export=ALL`）がそれを継ぐ。すると miniforge3 の `conda`（python 3.14）が `env/ftphase/lib/python3.12` を読んで `AssertionError: SRE module mismatch` で死に、`conda activate` が失敗する。コードは絶対パスなので走るが、計算機の prepend_text に `unset PYTHONPATH PYTHONHOME` を入れて止めた（`setup_aiida.sh` も同じ）。
3. **プラグインを変えたらデーモン再起動**（上）。
4. `verdi presto` の既定プロファイルの付け替え：スクリプトが `alamode_pg` に戻すが、`verdi profile list` で `*` を確認する。
5. RabbitMQ 4.x の「version not supported」警告：長い WorkChain で稀に二重投入の恐れ。ここでは 2 時間以内の WorkChain なので放置。心配なら `verdi -p ftphase config set broker.consumer_timeout 3600000`（RabbitMQ 側の設定が本筋）。

## 煙試験（pk 118、2026-10-23 11:31 投入、11:34 完了）

fcc 4 原子 x = 0, 0.25、B32 16 原子 x = 7/16, 1/2, 9/16（phonopy [4,4,4] 固定メッシュ、T 刻み 100 K、6 体積）、液相 108 原子 x = 0, 0.2（1000 + 1000 ステップ、1 反復、1100 → 900 K）。
QHA 5 本すべて exit 0、calphy 2 本 exit 0、`assemble_diagram` が REPORT.md と png を出した（`out/alli_ace_smoke/`）。数値は粗い設定なので物理的な意味は無い（900 K で liquid(0.055)+fcc(0.167)）。
最初の 2 回（pk 13、67）は走査範囲の不足で QHA が exit 300（上の落とし穴 1）。

## 本番（pk 191、2026-10-23 11:34 投入）

`out/alli_ace.pk.json`。QHA 13 セル（fcc 32 原子 x = 0, 0.0625–0.25 × 2 配置、Al₃Li 4 原子、B32 16 原子 × 3；supercell 2×2×2 か 3×3×3、密度メッシュ 60 Å、9 体積、T 0–1100 K 25 K 刻み）、
calphy GPU 液相 6 本（256 原子、1100 → 700 K、x = 0.1 は 800 K まで、10000 + 10000 ステップ、3 反復）。
QHA 13 本は 2 本ずつ（4 コア × 2）走り、runner 時間 3–24 秒/セル、投入から約 4 分で全完了（exit 0）。GPU 液相は 1 本ずつ（`--gres=gpu:1`）。
結果と例 5 との比較は `out/alli_ace/REPORT.md` と末尾の「結果」節（終了後に追記）。

## 結果（pk 191、2026-10-23 11:34 投入 → 12:27 完了、約 53 分；`out/alli_ace/`）

全 CalcJob が exit 0（QHA 13、calphy 6）。所要時間の内訳は QHA 4 分、GPU 液相 6 本 × 8.5 分（直列）、組立 10 秒。例 5（同じ物理、Slurm チェーン版、phonopy 固定メッシュ [4,4,4]）との比較（古典水準、0 GPa、格子 700–1100 K、10 K 刻み）：

| 特徴 | AiiDA 版（密度メッシュ 60 Å） | 例 5（[4,4,4] メッシュ） | 実験 |
|---|---|---|---|
| 共晶 | 760–770 K、液相 x ≈ 0.32、fcc 0.164 + B32 0.482 | 760–770 K、x ≈ 0.30–0.31、fcc 0.157 + B32 0.480 | 873 K、x ≈ 0.30、fcc ≈ 0.14 |
| 純 Al の融点 | 880–890 K | 860–870 K | 933.5 K |
| B32 側の液相線の終わり（x = 0.5） | 850–860 K | 840–850 K | 973 K |
| 800 K の二相域 | fcc(0.136)+liquid(0.257)、liquid(0.364)+B32(0.487) | fcc(0.128)+liquid(0.250)、liquid(0.360)+B32(0.484) | — |
| Al₃Li | 700 K 以上で現れない | 同じ | 準安定 δ' |
| fit 残差（900 K） | fcc 0.2、liquid 0.4 meV/atom | — | — |

- Al 融点が +20 K、B32 側が +10 K 上がったのは HANDOFF の見込みどおり、密度メッシュ 60 Å で純 Al の F_vib が正しくなった分（例 6 と同じ向き）。共晶温度・組成・固溶限は例 5 と 0.01 以内で一致し、AiiDA 化で物理は変わっていない。
- **新たに出た差**：700–790 K に幅 ≤ 0.09 の fcc+fcc 区間（x = 0.03–0.12、REPORT.md の「Same-phase segments」、tsv では `miscibility gap`）。Monte Carlo の一様オフセットには動じない（700 K で 23/30）が、液相とも B32 とも無関係な Al 側の狭い帯で、物理ではなく 32 原子 2 配置の fcc 系列（x = 0.0625 の 2 配置はどちらも Cmcm、x ≥ 0.125 は P1）の配置ノイズを 3 次多項式の過剰項が拾ったもの。例 5 では [4,4,4] メッシュのノイズ配分が違って出なかった。対処は例 6 と同じ（64 原子 SQS、`fits={'fcc':'rk'}` か `poly_order` を下げる、`sigma['fcc']` を配置ばらつきに合わせる）。本 WorkChain の目的（AiiDA 化の検証）には影響しない。
- 図 `out/alli_ace/07_phase_diagram.png`、表 `07_two_phase_regions.tsv`、`07_sensitivity.tsv`、`summary.json`、各 CalcJob の pk と作業 dir は `calcjobs.tsv`。provenance は `verdi -p ftphase node graph generate 191`。
