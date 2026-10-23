# Handoff: AiiDA 化（branch `aiida`）の続き — 2026-10-23 11:25 JST

対話セッションから切り離された headless Claude（`claude -p`）が、このファイルを読んで続きを行う。
作業言語は日本語。プロジェクト規約は `CLAUDE.md`。**課金やネットワーク公開を伴う操作は無い**。

## 目的（ユーザーの指示）

「AiiDA を用いた workflow にせよ。処理は Claude を閉じてもいいように background で行う。」
→ ftphase の工程 01–07 を AiiDA の WorkChain として実装し、ACE Al–Li（例 5 と同じ物理：Al 側 x_Li ≤ 0.5、
GPU の calphy 液相）を AiiDA デーモン + Slurm で本番投入し、文書化して branch `aiida` にコミットする。

## 出来ていること（コミット済み）

- `env/ftphase` に aiida-core 2.9.3 を追加（mamba、pandas 3.0 → 2.3.3 に下がったが pytest 42 件合格）。
- プラグイン `ftphase/src/ftphase/aiida/`：
  - `calculations.py` `QhaCalculation`（entry point `ftphase.qha`、実行ファイル `ftphase-qha-run input.json`）、
    `CalphyCalculation`（`ftphase.calphy`、`calphy_kernel -i input.yaml -k 0`、パスは `__WORKDIR__` を prepend_text の sed で `$PWD` に置換）
  - `parsers.py` `QhaParser`（`qha_results.json`/`qha_arrays.npz` → `results` Dict, `arrays` ArrayData）、
    `CalphyParser`（`*/report.yaml` → `results`、`*/temperature_sweep.dat` → `sweep` ArrayData；exit 300/310/320）
  - `functions.py` calcfunction `prepare_cells`（01 緩和 + 凸包、02A 固相セル、02B 液相セル；`spec` Dict の仕様は docstring）、
    `assemble_diagram`（04A/04B/05/06/07 → summary Dict、REPORT.md、png、tsv の SinglefileData）
  - `workchains.py` `TxDiagramWorkChain`（`ftphase.txdiagram`）：prepare → run_calculations（QHA と calphy を並列投入）→ inspect → assemble
  - `runners.py` `ftphase-qha-run`（計算ノードで relax + `phonopy_volume_scan`）
  - `pyproject.toml` に entry points（`pip install -e ./ftphase --no-deps` 済み）
- `ftphase/examples/aiida_txdiagram/`：
  - `setup_aiida.sh`（済み：プロファイル `ftphase`（SQLite + RabbitMQ）、計算機 `mygarden5`（core.local + core.slurm、
    workdir `~/aiida_run/ftphase`）、コード `ftphase-qha@mygarden5`・`calphy@mygarden5`、デーモン 2 worker 起動済み。
    既定プロファイルは `alamode_pg` のまま。`verdi` は `env/ftphase/bin/verdi -p ftphase`）
  - `run_aiida.py`（`--smoke` 煙試験、`--dry-run`、`--no-gpu`；投入後 `out/<name>.pk.json` に pk）
  - `fetch_results.py <pk|name>`（出力を `out/<name>/` に書き出す）

## 煙試験の状態（pk 13、`verdi -p ftphase process status 13`）

- `prepare_cells` 成功（凸包：fcc-Al、bcc-Li、B32 が hull 上、L1₂ Al₃Li も hull 上で「known list に無い」判定 = 既知の挙動）。
- QHA 5 本すべて exit 300：原因は煙試験の体積走査が 3 点で `fit_eos` が「need at least 4 volumes」を出したこと。
  **`run_aiida.py` の煙試験を 5 点（0.97, 0.985, 1.0, 1.015, 1.03）に直した（未投入）。**
- calphy 2 本（pk 36, 38、GPU、1000 steps）は投入時点で実行中。結果は pk 13 の子として残る。
- Slurm の `_scheduler-stderr.txt` に `AssertionError: SRE module mismatch`（`re/_compiler.py`）が出ている。
  QHA の python 自体は走った（qha.err に ftphase の ValueError が出ている）ので、`#SBATCH --get-user-env` +
  `conda activate` の組み合わせでログインシェル側の別 python が呼ばれたノイズの可能性。要確認：
  `~/aiida_run/ftphase/f4/d6/4a48-80bf-4935-8e33-028aea74953a/_scheduler-stderr.txt` の全文を読み、
  致命的なら計算機の prepend か code の prepend で `unset PYTHONPATH PYTHONHOME` を入れる。

## 残り作業（この順）

1. 煙試験を再投入：`env/ftphase/bin/python ftphase/examples/aiida_txdiagram/run_aiida.py --smoke`。
   `verdi -p ftphase process status <pk>` / `process report <pk>` で追う（QHA 数分、calphy 数分）。
   失敗したら `verdi -p ftphase calcjob gotocomputer <pk>` の dir の `qha.err` / `calphy.err` / `*/calphy.log` を読んで直す。
   直したら `./env/ftphase/bin/pip install -e ./ftphase --no-deps && ./env/ftphase/bin/verdi -p ftphase daemon restart`（プラグインを変えたら必ず再起動）。
   `assemble_diagram` まで通り、`fetch_results.py alli_ace_smoke` で REPORT.md と png が出ることを確認。
2. 本番投入：`run_aiida.py`（名前 `alli_ace`、GPU 液相 6 本 × 約 8.5 分直列 + QHA 9 セル）。`out/alli_ace.pk.json` に pk。
   投入後は待たなくてよい（デーモンが完走させる）。待てる範囲で状態を確認し、終われば `fetch_results.py alli_ace` で
   `out/alli_ace/REPORT.md` を読み、例 5（`alli_ace_txdiagram/out/REPORT.md`：共晶 760–770 K、x ≈ 0.30、fcc 固溶限 0.157、
   Al 融点 860–870 K）と比べて差を記録する（メッシュが 60 Å 密度指定になっているので Al 融点は 890 K 付近に上がる見込み）。
3. テスト：`ftphase/tests/test_aiida.py` を追加（aiida の pytest fixture `aiida_profile_clean` は
   `pytest_plugins = ["aiida.manage.tests.pytest_fixtures"]`；`CalphyParser` を `alli_ace_txdiagram/calphy_liquid/lqd_x0.00-ts-*/`
   の実 `report.yaml`・`temperature_sweep.dat` で、`QhaCalculation.prepare_for_submission` を `generate_calc_job` 相当で検証）。
   `./env/ftphase/bin/python -m pytest ftphase/tests -q` が全部通ること。
4. 文書：`ftphase/examples/aiida_txdiagram/README.md`（日本語：構成図、spec の書き方、setup/run/fetch、
   失敗の診かた、デーモン再起動の規則）、`ftphase/README.md` に「AiiDA ワークフロー」節、`docs/ftphase.html` に 3.8 節、
   `skills/phase-diagram/references/ftphase.md` に要点、`CLAUDE.md` に「AiiDA (profile ftphase)」節
   （プロファイル名、verdi のパス、デーモン、コード、再起動の規則、`alamode_pg` と混ぜないこと）。
5. コミット（branch `aiida`、`git add -A`；`.gitignore` は env/ と aiida_run を除外済み。
   `ftphase/examples/aiida_txdiagram/out/` の pk.json と REPORT/png は小さいので入れる）。
   コミットメッセージ末尾に `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`。
6. 終了時に `ftphase/examples/aiida_txdiagram/out/HEADLESS_DONE.md` に、何を終えたか・本番の pk・未了のことを書く。

## 守ること

- 課金操作・外部送信は無い。`verdi` は必ず `-p ftphase`（`alamode_pg` の既定を変えない、そのデーモンに触らない）。
- `rm -rf` は `~/aiida_run/ftphase/` の自分のジョブ dir 以外に使わない。`env/` を作り直さない。
- Slurm のジョブは自分（aiida-* という名前）のものだけ扱う。他のジョブは cancel しない。
- 長い計算は投入して待つだけ（`sleep` を小刻みに）。終わらなくても文書とコミットは済ませる。
