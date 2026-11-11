# data/Zhang2027 — Zhang ほか (2027) の Zenodo 公開データ（ユーザーが 2026-11-11 に配置）

出典: W. Zhang, "Collections of phases diagrams obtained from universal machine learning interatomic potentials in six binary systems",
Zenodo, doi:10.5281/zenodo.20918696（concept DOI 10.5281/zenodo.20918695、公開 2026-06-26、2026-08-09 に zip → tar.gz 差し替え）。
論文: Zhang, Forti, Hammerschmidt, Crivello, Koyama, Abe, Scripta Mater. 289 (2027) 117663（読書メモ `ftphase/examples/orchid_calphad/zhang2027/NOTES.md`）。

- ファイル: `zenodo-phase-diagrams.tar.gz`（1,484,928,890 bytes、sha256 `5ae7b3f1d4300bb588c7f7c94dc56b806af23bd81b7b3ac100261a14c411963a`）、展開先 `zenodo-phase-diagrams/`（3.7 GB、6,260 ファイル）。
- **ライセンス: CC BY 4.0**（Zenodo レコードのメタデータ `license: cc-by-4.0`）。デポジット全体（TDB・計算出力・Python スクリプト・ノートブック）に一括で付いていて、別のコード用ライセンスファイルや著作権表示はスクリプト内に無い。
  再配布・改変は出典表示（Zhang 2027 と Zenodo DOI）で可。ただし同梱の第三者データは元の条件に従う:
  - `data/unary50.tdb` = SGTE Unary Database v5.0（2009-06-02）。SGTE の配布物で、CC BY の対象ではない（本プロジェクトは espei.refdata の SGTE91 を使っているので不要）。
  - `CPDDB/*.tdb.txt` = NIMS 計算状態図データベース CPDDB（Abe, Hashimoto, Sawada；doi:10.48505/NIMS.3060）の評価 TDB 6 件（Al–Zn Mey、Cu–Mg Liang、Cu–Pt Abe、Mo–Rh Gürler、Ru–Si Liu、Re–W Liu）。CPDDB の利用条件に従う。`Modified_CPDDB/` はそれを論文の比較用に改変したもの。
- このフォルダは git に入れない（`.gitignore` の `data/Zhang2027/*`、この README だけ追跡）。再取得は Zenodo から。

## 中身

| 場所 | 内容 |
|---|---|
| `DFT/<系>/*.json`（19–20 構造/系） | DFT（VASP PBE）の緩和構造・エネルギー・フォノン（`phase`, `cell`, `positions`, `symbols`, `energy_per_atom_eV`, `ph_qweights`, `ph_omega`（q 点ごとの振動数）, `ph_displacement`, `supercell_matrix`, `primitive_matrix`）。固溶体は SQS（例 `fcc-Al10Zn6`）、化合物は `compound-*`。 |
| `<MLIP>/<系>/*.json`, `<MLIP>/<系>/results/` | 同じ構造集合を各 UMLIP で再計算したもの（8 モデル: `grace-2L-SMAX`, `grace-2L-OAM-L`, `grace-2L-MP`, `SevenNet-omni`, `SevenNet-MF-ompa`, `Nequip-OAM-XL`, `Nequip-MP-L`, `eSEN-uma-s-1p1`, `ORB-v3`；各 235–320 MB）。`get_calculator.py` にモデルの読み込み（例 `grace_fm("GRACE-2L-SMAX-OMAT-large")`）。 |
| `<MLIP>/<系>.tdb`, `DFT/<系>.tdb` | 論文の方法で組んだ TDB（SGTE unary + 多項式に fit した端成分 + CEF + 液相は CPDDB の記述を再最適化）。pycalphad で読める。 |
| `CPDDB/`, `Modified_CPDDB/` | 実験評価の TDB（上記）。 |
| `data/liquid_description.json` | 系ごとの液相パラメータの雛形（CPDDB 由来、`optimized` 印付き）。 |
| `phase_diagrams/*.png`, `enthalpy/` | 論文図 2 の各パネルと生成エンタルピーの図。 |
| `00-run_foundation_model.py` … `07-plot_enthalpy.ipynb`, `mlip.py`, `dft.py`, `tdb.py` | ワークフロー（`benchmark` パッケージとして import；`mlip.py`/`dft.py`/`tdb.py` がその本体）。 |

## 本プロジェクトで使えるもの

1. **TDB の直接比較**: 6 系 × 9 モデル + DFT の TDB を `orchid_calphad/espei_alli/tdb_invariants.py` / pycalphad で読み、相ラベル分類精度（論文 Fig. 3）を再計算できる。本プロジェクトの系（Al–Li、Ni–Al、Ag–Cu、Pt–Rh）は含まれないので、直接の重ね描きはできない。
2. **同じ構造集合で本プロジェクトの MLIP を評価**: `DFT/<系>/*.json` の構造とフォノン（調和、DFT）があるので、MACE-MPA-0・MatterSim・DPA4 など論文に無い MLIP で ΔH・ΔS の RMSE（論文 Table 1 の指標）を計算し、同じ表に並べられる。
3. **液相の扱いの違いの定量**: 論文は液相を CPDDB から借りて液相線を再最適化している。Cu–Mg や Al–Zn で本プロジェクトの calphy 液相 TI を回せば、「液相を計算した場合」との差を同じ TDB の枠で示せる。
4. **誤差伝播（UQ）の手順**: `05-enthalpy_entropy_error.ipynb` と `06-compare_phasediagram.ipynb` にパラメータ分布からのサンプリングと分類精度の実装がある。工程 07 の Monte Carlo 誤差伝播に「MLIP → DFT の系統誤差」を事前分布として足す参考になる。
