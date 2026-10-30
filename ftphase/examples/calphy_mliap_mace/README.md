# calphy_mliap_mace — calphy 液相 TI を ML-IAP unified（MACE-MPA-0 fp32）で流し、`pair_style mace` の結果と突き合わせる（2026-10-30）

例 8（AiiDA WorkChain pk 4293、`alli_mace_mpa_0`）の液相ジョブ pk 4356（`lqd_x0.00`：Al 256 原子、mode `ts` 1100→700 K、
P = 0、平衡化 10,000、switching 10,000 + 10,000、3 反復、`pair_style mace no_domain_decomposition` fp32、
`env/lammps-torch/bin/lmp_mace.sh`）と同じ系・同じ設定を、同じ MACE-MPA-0 fp32 の重みを ML-IAP 形式に書き出したモデル
（`potentials/mace/macempa0mediummodel.model-mliap_lammps-f32.pt`）で、`env/lammps-gpu-mliap/bin/lmp_mliap_mace.sh`
（`pair_style mliap unified <model> 0`、Kokkos coupling、`hybrid/scaled/kk`）から流した。calphy から ML-IAP を使う初回。

## 手順

```
../../../env/ftphase/bin/python make_input.py   # calculation_block(gpu=True, lammps_executable=lmp_mliap_mace.sh, pair_style="mliap unified <model> 0", pair_coeff="* * Al Li") → input.yaml
sbatch run.sbatch                                # 1 task, --gres=gpu:1, env/ftphase, run 0 の precheck → calphy_kernel -i input.yaml -k 0（AiiDA の CalcJob と同じ資源）
../../../env/ftphase/bin/python compare.py       # pk 4356 の report.yaml / temperature_sweep.dat と比較 → compare.md
```

`calculation_block(gpu=True)` は `gpu_capability` でバイナリの `mliap/kk` と `hybrid/scaled/kk` を確認し、`md.cmdargs`
（`-k on g 1 -sf kk -pk kokkos newton on neigh half`）を書く。`atom_modify map yes` は不要（precheck：plain と
`hybrid/scaled/kk` λ=1 で pe −957.44065 / −957.44066 eV）。時間測定のため、投入時に保留中の AiiDA GPU ジョブ 45 本を
`scontrol hold` し、本ジョブが走り出した直後に release した（以後は本ジョブの後ろに並ぶだけ）。GPU には AiiDA デーモンの
worker 2 プロセス（stage 01 の GRACE 計算器が作った CUDA コンテキスト、各 186 MiB、利用率 0 %）が常駐していたが、計算には関与しない。

## 結果（Slurm 22990、RTX 3060 専有；`compare.md`、`report_22990.yaml`）

| | `pair_style mace` fp32（pk 4356） | ML-IAP unified fp32（22990） | 差（meV/atom） |
|---|---|---|---|
| G(1100 K) | −4.187605 | −4.187613 | −0.01 |
| G(1000 K) | −4.110988 ± 0.00015 | −4.110843 ± 0.00006 | +0.15 |
| G(900 K) | −4.037360 ± 0.00012 | −4.037227 ± 0.00010 | +0.13 |
| G(800 K) | −3.967606 ± 0.00015 | −3.967502 ± 0.00010 | +0.10 |
| G(700 K) | −3.901996 ± 0.00017 | −3.901848 ± 0.00008 | +0.15 |
| work / reference_system（1100 K） | 4.070026 / 0.909432 | 4.071203 / 0.910534 | +1.18 / +1.10（相殺） |
| 体積（Å³/atom、1100 K） | 19.4262 | 19.4139 | |
| ts_dissipation（eV/atom） | 0.00098（flag false） | 0.00105（flag true：`tolerance.dissipation` 既定 0.001 をわずかに超過） | |
| LAMMPS s/step（10,000 ステップ区間の中央値） | 0.157 | 0.085 | 1.84 倍速 |
| calphy 壁時計 | 9.57 h | 5.14 h | 1.86 倍速 |

- 自由エネルギーは 1100 K で 0.01 meV/atom、掃引全域で 0.10〜0.15 meV/atom の差。乱数種が異なる独立な 2 run なので、
  この差は液相 TI の run 間ばらつき（例 6 で 0.1〜0.5 meV/atom）の範囲。ML-IAP 経由の力・ビリアルが `pair_style mace` と
  同じであることの calphy レベルの確認になる。
- 速度は約 1.85 倍。参照ジョブは期間中に GPU を他の AiiDA ジョブと共有した可能性があるので、`pair_style mace` 側の数字は
  上限（単体ベンチマークの 0.177 s/step @256 原子より速い値が出ている）。それでも ML-IAP の 0.085 s/step は
  専有ベンチマークの 0.090 s/step と一致する。
- `ts_dissipation_high: true` は 0.00105 > 0.001 のぎりぎりの超過で、参照（0.00098）と同じ水準。掃引を 10,000 → 20,000 ステップ
  にすれば消える。

## ファイル

`make_input.py`、`run.sbatch`、`compare.py`、`input.yaml`、`precheck.lmp`/`precheck.log`、`run.22990.out`、`compare.md`、
`report_22990.yaml`。ジョブフォルダ `lqd_x0.00-ts-*/` と `*.data` は .gitignore（他の calphy 例と同じ）。
最初の投入 22989 は sbatch スクリプト内の `cd "$(dirname "$0")"` が slurmd のコピー先に移って失敗した（`SLURM_SUBMIT_DIR` を使う）。

## 次

WorkChain の `MLIPS["mace-mpa-0"]` を `lammps_executable=lmp_mliap_mace.sh`、`pair_style="mliap unified {potential} 0"`、
`pair_coeff="* * Al Li"`、`gpu=True` に切り替えれば例 8 の液相 6 本が半分の時間で済む（`run_aiida.py --mlip mace-mpa-0` の
再実行はキャッシュを使わないので 6 本すべて流れる）。SevenNet は `e3gnn` の方が速いので切り替えない。
