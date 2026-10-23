# 欠けている工程を補う公開ソースコード（2026-10-21 調査）

[examples.md](examples.md) で「例に無く自作が要る」とした工程を、公開コードで補えるかの調査結果。長い版と出典はプロジェクトの `docs/public-sources.html`。動作を本ホストで確認したのは「導入済み」のものだけ。

## 結論

- 欠けている工程はすべて公開コードで補える。統合パッケージは無く、工程ごとに組み合わせる。
- **導入済み calphy 2.3.0 の `calphy.phase_diagram.PhaseDiagram` が 05・06 の大半を持つ**：`build_calphad_surface` で G(x,T) を GHSER + 理想混合 + Redlich–Kister に分解、`to_tdb(line_compounds=[...])` で line compound と限定組成相を含む TDB を書き、pycalphad で読める。upstream に入力例は無い（2026-05〜07 の commit）。
- 主軸：icet（02A/04A）＋ aiida-alamode と phonopy（03A）＋ calphy PhaseDiagram（03B/05/06）＋ pycalphad（06/07）。参照実装は exaPD と Menon 2024。
- 自作が避けられないのは、(a) QHA の G(T,V,x) と calphy TI の G(T,P,x) を同じ表形式・基準に揃える変換層（04B/05）、(b) SQS → aiida-alamode → calphy PhaseDiagram を結ぶドライバ、(c) 境界の誤差感度（07）。

## 工程 → コード

| 工程 | コード | 要点 | 状態 |
|---|---|---|---|
| 01 | matcalc（BSD-3）、mlipx、pymatgen | EOS・弾性・phonon・QHA の計算器とベンチマーク、MLIP 比較。融点は calphy melting_temperature | 未導入 |
| 02A | icet 4.0、sqsgenerator 0.5.6（MIT） | icet は副格子 `[['Al','Li'],['Li','X']]` と空孔 `X` を直接扱う。`generate_sqs_by_enumeration` は最適解を逃さない。pyiron `SQSJob` は sqsgenerator を使う | pip 取得可を確認、未導入。ATAT mcsqs は CC BY-ND で優先しない |
| 03A | aiida-alamode（手元）、phonopy `run_qha` / `phonopy-qha`、matcalc QHACalc | anphon DOS の `thermo` で体積ごとの F(T)、phonopy で EOS フィット（5 体積以上、`--pressure`） | コードは揃う。組成系列の反復と calphy への受け渡しが自作 |
| 04A | icet mchammer（TI、温度積分、Wang–Landau）、smol（BSD）、CLEASE（GPL） | CE から F_conf を直接出す。F_conf は配置エネルギー込みなので静的エネルギーを再加算しない | CE の学習データ生成は自作 |
| 02A/04A 別解 | exaPD（github.com/ML-AMD/exa-pd） | SGC MC で Δμ(x) → Redlich–Kister、line compound は Einstein 結晶 TI、液相 UFM TI、TDB → pycalphad。Parsl、Perlmutter 前提 | 参照実装として読む |
| 04B | 無し | 量子調和と古典調和の差で補正、method 欄に記録 | 自作 |
| 05 | calphy PhaseDiagram（導入済み）、ESPEI 0.9.1（MIT） | calphy は TDB 往復可。ESPEI は熱化学・相境界データから CEF パラメータ生成と MCMC | ESPEI 未導入、要件未確認 |
| 06 | calphy `PhaseDiagram.calculate`（`composition_intervals`、`ideal_configurational_entropy`、`calphad_surface`）、pycalphad、OpenCalphad（GPL） | 二元は calphy で完結、三元以上は TDB → pycalphad Mapping | 導入済み |
| 07 | ESPEI MCMC、pycalphad Metastability、AiiDA provenance | calphy の `error` を G に伝播させる感度評価は自作 | 自作が最多 |

## 使うときの注意

- calphy は Academic Software Licence（非商用）、ATAT は改変配布不可、CLEASE と OpenCalphad は GPL。
- aiida-alamode の ASE 計算器は MatterSim / SevenNet のみ組み込み。calphy 側と同じ MLIP（pace 等）で QHA を回すには ASE の LAMMPS 計算器を足す。
- Menon 2024 の配置エントロピーは理想混合の後付け（論文も限界と明記）。そのまま踏襲しない。
- 未確認：ESPEI の最新要件、exaPD の正式なライセンス名、Menon 2024 の pyiron ワークフローのリポジトリ名。
