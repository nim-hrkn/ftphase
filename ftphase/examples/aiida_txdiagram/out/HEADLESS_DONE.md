# headless セッションの記録（2026-10-23、HANDOFF.md の残り作業 1–6）

状態：作業 1–6 すべて完了。本番 WorkChain **pk 191** は 12:27 に Finished [0]（53 分、19 CalcJob すべて exit 0）。結果は `out/alli_ace/REPORT.md`、比較は下の「結果」節。

## 終えたこと

1. 煙試験：pk 67（QHA 5 本が exit 300：1100 K の EOS 最小が走査範囲 0.97–1.03 の外）→ `run_aiida.py --smoke` の scales を 0.97–1.07 の 6 点に直し、pk 118 が 11:31 投入 → 11:34 に `assemble_diagram` まで完走。`fetch_results.py alli_ace_smoke` → `out/alli_ace_smoke/REPORT.md`、`07_phase_diagram.png`。
   - `SRE module mismatch` の原因：AiiDA デーモン worker が自分の `sys.path` を `PYTHONPATH` に書き出し、Slurm ジョブが継承 → miniforge3 の `conda`（python 3.14）が `env/ftphase/lib/python3.12` を読んで死に、`conda activate` が失敗していた。計算機 `mygarden5` の prepend_text に `unset PYTHONPATH PYTHONHOME` を設定（`setup_aiida.sh` も更新）。以後の `_scheduler-stderr.txt` は空。
2. 本番：`run_aiida.py` → **pk 191**（`out/alli_ace.pk.json`、11:34:50 投入、12:27:14 完了）。prepare_cells 成功、QHA 13 本（pk 216–240）すべて exit 0（4 分）、GPU 液相 6 本（pk 242–252）exit 0（8.5 分ずつ直列）、assemble_diagram pk 271 付近 exit 0。`fetch_results.py alli_ace` → `out/alli_ace/`。
3. テスト：`ftphase/tests/test_aiida.py`（8 件）追加、`conftest.py` に `aiida.tools.pytest_fixtures` 登録。`pytest ftphase/tests -q` → 50 passed, 1 skipped（skip は従来の「LAMMPS バイナリが PATH に無い」）。
4. 文書：`examples/aiida_txdiagram/README.md`（新規）、`ftphase/README.md`（AiiDA 節 + 例 8 + 検証件数）、`docs/ftphase.html`（3.8 節、検証件数、制限）、`skills/phase-diagram/references/ftphase.md`（AiiDA 層、使い方、事実）、`CLAUDE.md`（「AiiDA (profile ftphase)」節）。
5. コミット：branch `aiida`、dfd6f47「AiiDA workflow: smoke test passes end to end, tests, docs, production submitted (pk 191)」。`.gitignore` に `headless_claude.log` を追加。

## 守ったこと

- `verdi` は常に `-p ftphase`。既定プロファイル `alamode_pg` とそのデーモンには触れていない。
- kill したのは自分の WorkChain pk 67 と、その子で残った calphy pk 90 のみ（Slurm `aiida-90`）。他のジョブには触れていない。`rm -rf` は使っていない。
- 課金・外部送信なし。`env/` は変えていない。

## 未了・注意

- 未了は無し。残る改善点（やっていない）：fcc の配置ノイズ由来の fcc+fcc 帯（下）を消すには 64 原子 SQS か `fits={'fcc':'rk'}`（例 6 と同じ）。WorkChain の再開（失敗セルだけの再投入）とキャッシュは未実装。
- WorkChain を kill すると子 CalcJob が `Waiting` で残ることがある（pk 90 で発生）。`process status` で確認して個別に kill。
- HANDOFF.md 自体はそのまま（履歴として）。

## 結果（pk 191）と例 5 の比較

| 特徴 | AiiDA 版（メッシュ 60 Å） | 例 5（[4,4,4]） |
|---|---|---|
| 共晶 | 760–770 K、液相 x ≈ 0.32、fcc 0.164 + B32 0.482 | 760–770 K、x ≈ 0.30–0.31、fcc 0.157 + B32 0.480 |
| 純 Al の融点 | 880–890 K（HANDOFF の見込み「890 K 付近」どおり） | 860–870 K |
| B32 側の液相線の終わり | 850–860 K | 840–850 K |
| Al₃Li | 700 K 以上で現れない | 同じ |
| 新たな差 | 700–790 K に幅 ≤ 0.09 の fcc+fcc 帯（x = 0.03–0.12）：32 原子 2 配置の配置ノイズを過剰項の 3 次多項式が拾ったもの。物理ではない | 無し |

追加コミット：「AiiDA workflow: production pk 191 finished, results and comparison with example 5」。
