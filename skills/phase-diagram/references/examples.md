# 実行済みの例と工程の対応（2026-10-21、mygarden5）

workflow.svg の工程記号：01 候補相・MLIP 検証、02A 固相の組成・配置系列、02B 液相系列、03A 固相の振動自由エネルギー（phonon/QHA、補助経路 calphy の固相 TI）、03B 液相 TI、04A 固相の配置自由エネルギー、04B 液相の基準整合、05 全相の基準統一、06 凸包・共通接線、07 T–x 相図と記録、DB 既存 CALPHAD。詳細な表と結果は プロジェクトの `docs/examples.html`。欠けている工程を公開コードで補う方法は [public-sources.md](public-sources.md)。

## どの例を見るか

| 目的 | 見る例 | 場所 |
|---|---|---|
| calphy の入力形式、固相・液相 TI（03A 補助／03B） | calphy examples 01, 03, 06 | `calphy-examples/` |
| 純元素融点（06 の退化形）、融点自動探索の限界 | calphy 03, 04, 13 | 同上（04 は散逸警告で Tm 不確か） |
| P–T 融解線（07 の P–T 版） | calphy 05, 13 (dcci) | 同上 |
| 組成方向に固相 G を伸ばす（02A/04A 入口、配置項なし） | calphy 10 (ZrCu composition_scaling) | 同上 |
| 参照状態の付け替え（05） | calphy 07 (alchemy) | 同上 |
| 02A→03→04A→05→06→07 を一通り通す最小例 | pyiron workshop2022 tutorial_2（Al–Li EAM、実計算 18 本） | `pyiron-examples/workshop2022-phase-diagram/`（`run_calculations.py`, `analyze_phase_diagram.py`, `analysis/`） |
| calphy.phase_diagram による多相の凸包と相図描画（06/07） | Menon 2024 EAM データセットの後処理 | `pyiron-examples/menon2024-alli-eam/plot_phase_diagram_eam.py` |
| 既存 TDB から相図・固溶幅・参照状態（DB, 05, 06, 07） | pycalphad notebooks（Binary, Mapping, Screening, ReferenceState, Metastability） | `pycalphad-examples/executed/`, `figures/` |
| 副格子モデルの規則化度（04A の CALPHAD 側） | pycalphad EquilibriumWithOrdering | 同上 |

## 例に無く自作が要る工程

- 01：候補相の列挙と MLIP の凸包・融点検証。Menon 2024 の EAM データは検証無しで進むと液相が 700 K まで安定になる反面教師。
- 02A：SQS（icet/mcsqs）、副格子・空孔の系列。既存例はすべて単一ランダム配置。
- 03A 本線：aiida-alamode の phonon/QHA による G(T,P)。例にあるのは補助経路の calphy 固相 TI だけ。環境（conda env `alamode`、aiida-alamode スキル）は本ホストに有る。
- 04A：副格子ごとの配置項。workshop 例は B32 に全格子点の理想混合を適用しており、workflow.md 第 4 節の禁止事項に当たる。
- 04B：量子固相（QHA）と古典液相（TI）の基準整合。pycalphad ReferenceState 群は参照状態の付け替えを示すだけで、MLIP 計算での例は無い。
- 05：MLIP の G を TDB の参照状態へ変換する工程。
- 06：line phase・限定組成相を含む多相凸包。導入済み calphy 2.3.0 の `calphy.phase_diagram.PhaseDiagram` は `composition_intervals`（限定組成相）、`to_tdb(line_compounds=...)`、`ideal_configurational_entropy` の on/off を持ち二元ならこれで足りる（2026-10-21 訂正。旧記述「二元限定で line phase 非対応」は誤り）。入力例は upstream の examples/ にも docs/ にも無い。CLI 版 `calphy_phase_diagram -i` の `phases:` ブロックは element, lattice(data), reference_phase, phase_name, composition{reference_element, range/values, interval}, temperature{range/interval}。詳細は [public-sources.md](public-sources.md)。
- 07：境界の誤差感度。既存例はすべて 1 反復で error = 0。

## 実行時の落とし穴（確認済み）

- calphy `--validate` は dry run ではない（ジョブ投入まで行う）。パースのみは `calphy.input.read_inputfile(path, validate=True)`。
- calphy は `<mode>-conf.data-…data` をカレントディレクトリに書く。並列ジョブは cwd を分ける。同条件の入力はフォルダ名が衝突するので `folder_prefix`。
- calphy 2 系の融解・凝固検出（`tolerance.solid_fraction` / `liquid_fraction`）は、pyiron の Calphy ジョブでは有効だが calphy 2.3.0 の CLI 既定では無効（0 / 1）。ftphase の `calculation_block` は既定で 0.7 / 0.05 を書く。準安定端点が必要なら明示的に無効化し、記録する。
- calphy ≥ 2.2 は pyscal3 ≥ 4、2.1.x は pyscal3 < 4。conda-forge は 2.1.2 止まり、GitHub/PyPI は 2.3.0。
- 既定の Slurm 設定（`queue: {scheduler: slurm, queuename: debug, cores: 4, memory: 8GB, commands: [conda activate <prefix>]}`）で `--hint=nomultithread` が付き、4 タスクが 8 論理 CPU を占める。
- pyiron：設定は環境変数（`PYIRONRESOURCEPATHS`, `PYIRONDISABLE=True` または `PYIRONSQLFILE`, `PYIRONPROJECTCHECKENABLED=False`、真偽値は Python リテラル）。`pr.unpack` は `archive/{export.csv, <project path>}` 配置と sqlite が必要。
- calphy 2.3.0 の `plot_phase_diagram(tangents, T, tangent_types, phases)`。`get_phase_free_energy` はデータ外を 1.0 で埋めるので x=0, 0.5 に幅ゼロの偽セグメントが出る。
- GPU で calphy（ACE）を回す場合（2026-10-22、[ftphase.md](ftphase.md)）：注意点：GPU 1 枚ではジョブが直列になるため、総スループットは CPU 8 コアと同程度です。利点は 1 本の待ち時間短縮と、CPU を QHA に空けられることです。

## 今回の数値（教材設定、対象系の結果ではない）

- workshop Al–Li EAM：共晶 ≈ 863 K, x_Li ≈ 0.22、fcc+B32 二相域 x = 0.19–0.25（実験：約 870 K, x ≈ 0.26）。
- calphy Cu EAM：Tm 0 bar 1352 K（5³ セル）/ 1383 K（10³ セル、警告付き）、50 kbar 1547 K、dcci 100 kbar 1730 K。

## 01 から 07 を一本で通した例（2026-10-22）

`ftphase/examples/alli_ace_txdiagram/`（[ftphase.md](ftphase.md)）が、ACE Al–Li で 01（0 K 検証）→ 02A/02B（系列）→ 03A（QHA、CPU）→ 03B（calphy 液相、GPU）→ 04A/04B → 05 → 06 → 07（T–x 図）を Slurm ジョブの連鎖として実行した唯一の例。上の公開例はどれも途中の段から始まる。
