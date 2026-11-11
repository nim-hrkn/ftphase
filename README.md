# PhaseDiagram / ftphase

MLIP（機械学習原子間ポテンシャル）＋フォノン QHA＋calphy 熱力学積分で有限温度の二元系相図（固溶体・線状化合物・組成幅を持つ規則相・液相）を
計算するための設計書・実行例・Python パッケージです。文書の作業言語は日本語です。

![Al-Li: CALPHAD assessment vs MLIP phase diagrams](docs/img/alli_hero.png)

Al–Li の相図。左が実験に基づく CALPHAD 評価（AlLi-20Lon、SGTE、ORCHID-Diagrams 経由）、右の 3 枚が ftphase で MLIP から計算した T–x 図
（系専用 ACE、汎用 MLIP の SevenNet-MF-ompa と SevenNet-0；固相は QHA、液相は calphy の熱力学積分、補間関数への当てはめなし。
黒線は評価の相境界、破線は不変反応）。x_Li > 0.5 は固相だけの計算（Al₂Li₃・Al₄Li₉・bcc Li、液相なし）。
12 種の MLIP 全部を並べた版は [`docs/img/alli_overlay_13mlip.png`](docs/img/alli_overlay_13mlip.png)、
作図は `ftphase/examples/orchid_calphad/hero_alli.py` / `sgte_diagrams.py`、各 MLIP の数値と ORCHID との照合は
[開発状況ページ](https://claude.ai/artifact/NZEKsthcgzmVw4QppWjifk)（日本語 / English / Indonesia）の第 4 節。

- `ftphase/` — 本プロジェクトのパッケージ（工程 01〜07、AiiDA WorkChain、実行例）。**MIT License**（`LICENSE`）。
  使い方は `ftphase/README.md`、設計と検証結果は `docs/ftphase.html`。
- `docs/`, `skills/` — 設計書・判断規則・参照メモ（MIT）。
- `calphy-examples/` — calphy（ICAMS）上流の `examples/` を Slurm 用に書き換えて実行した複製。
  calphy の **Academic Software Licence v1.0（非商用）** に従います（変更点は同フォルダの README に記載）。
- `pycalphad-examples/` — pycalphad 0.11.2 上流の `examples/` の実行複製（pycalphad の MIT License）。
- `pyiron-examples/` — pyiron potentials-workshop-2022 と Menon et al. 2024 の Al–Li 例の実行記録。
  上流のポテンシャルファイル（EAM / ACE / HDNNP）はこのリポジトリに含めません。各 README の出所から取得して
  `resources/lammps/potentials/` に置いてください。
- `env/` — conda 環境と LAMMPS ビルドの再現手順（環境本体はコミットしません）。
- 含めないもの：`資料/`（原典 PDF）、`potentials/`（第三者のポテンシャル）、`papers/`、`data/orchid-*`（Zenodo から再取得）。

`CLAUDE.md` は Claude Code 用の作業メモで、環境・計算機・実行済みの計算の記録を兼ねています。
