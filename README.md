# PhaseDiagram / ftphase

MLIP（機械学習原子間ポテンシャル）＋フォノン QHA＋calphy 熱力学積分で有限温度の二元系相図（固溶体・線状化合物・組成幅を持つ規則相・液相）を
計算するための設計書・実行例・Python パッケージです。文書の作業言語は日本語です。

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
