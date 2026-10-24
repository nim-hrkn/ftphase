# 使える MLIP と、補間関数を使わない経路での可否（2026-10-24 確認）

確認方法：3 つの LAMMPS バイナリの `lmp -h`（pair style・fix style）、各 Python 環境の import。長い版は `docs/mlip.html`。

## LAMMPS 経由（calphy の TI、LAMMPSlib での QHA）

| MLIP | pair style | CPU（`env/ftphase/bin/lmp_mpi`、mygardenx1） | GPU calphy `env/lammps-gpu/bin/lmp_gpu` | GPU calphy `env/lammps-gpu-grace/bin/lmp_gpugrace` |
|---|---|---|---|---|
| ACE（pacemaker） | `pace`, `pace/kk` | ○ | ○（検証済み、`pace product`） | ○ |
| GRACE FS | `grace/fs`, `grace/fs/kk` | ○ | × | ○（検証済み） |
| GRACE 1L/2L/3L（Kokkos 版、kokkos.npz） | `grace/1l/kk` など | ○（`/cpu/kk`） | × | ○（1L 検証済み） |
| GRACE（TensorFlow 版） | `grace` | mygardenx1 のみ（tensorpotential） | × | × |
| SNAP | `snap`, `snap/kk` | ○ | ○ | ○ |
| MTP（MLIP-2） | `mlip` | ○ | × | × |
| n2p2（HDNNP） | `hdnnp` | ○ | × | × |
| M3GNet | `m3gnet` | ○（conda 版のみ） | × | × |
| ML-IAP（PyTorch/NequIP 等のモデル） | `mliap`, `mliap/kk` | ○（conda 版のみ、要モデル） | × | × |
| RANN | `rann` | × | ○ | × |

- GPU の calphy は `hybrid/scaled/kk` が要るので自前ビルドの 2 つだけ。conda 版 LAMMPS は GRACE の kk 版を持つが calphy の GPU 実行には使えない。`calculation_block(gpu=True)` が `<style>/kk` の有無で弾く。
- ASE 経由のみ（QHA・0 K 検証に使える、calphy には使えない）：`alamode` 環境の MatterSim・SevenNet、mygardenx1 の tensorpotential（GRACE 全モデル）・pyace。env/ftphase には torch・pyace は無い。
- 手元のポテンシャル：ACE Al–Li（`AlLi-6gen-18May.yace`）、`potentials/grace/`（GRACE-FS-OAM.yaml、GRACE-1L-OMAT-medium-base-fp64 kokkos.npz；他 44 モデルは `grace_models download`）、EAM（Al–Li、Ni–Al Mishin 2009、Ag–Cu Williams 2006、Cu）。
- 使えないもの：MACE、SevenNet の LAMMPS 版（`e3gnn`）、NequIP/Allegro、CHGNet、DeePMD、UF3、POD（pair style が無い。別ビルドが要る）。
- 推奨：系専用の精度は ACE（pacemaker、mygardenx1 で学習可）。学習なしで多元素は GRACE-FS-OAM（GPU で calphy まで通る唯一の基盤モデル）。

## float32 と float64（2026-10-24 測定、`env/lammps-gpu-grace/test/prec/`）

MACE・SevenNet の既定 float32 が TI の精度（1 meV/atom）に足りるかを測った。結論：**足りる**。float32 の丸めは 1 評価あたり 0.1〜0.2 µeV/atom で、TI の統計誤差（0.1〜1 meV/atom）より 3 桁小さい。

| 量 | GRACE-1L kokkos fp32 − fp64（2,048 原子、GPU） | GRACE-1L mixed − fp64 | SevenNet-0 float32 の丸め（256 原子、CPU、並進・置換不変性からの推定） |
|---|---|---|---|
| エネルギー | < 0.001 meV/atom | < 0.001 meV/atom | 標準偏差 0.12 µeV/atom、最大 0.24 µeV/atom |
| 力 | RMS 差 0.01 meV/Å、最大 0.1 meV/Å（力の RMS 0.67 eV/Å） | 0 | 不変性からの力の揺らぎ 0.00 meV/Å、合力 0.001 meV/Å |
| 圧力 | −0.1 bar | −0.1 bar | — |
| NVE 200 ステップ（2 fs）の全エネルギー漂動 | −0.257 meV/atom（fp64 と同一） | 同一 | — |
| 速度（200 ステップ） | 9.3 s（fp64 30.2 s、**3.3 倍速**） | 11.5 s | — |

SevenNet の有限差分（h = 0.01 Å）の力誤差 2.5 meV/Å は 1 評価あたりのエネルギー丸め 0.05 meV（256 原子の総和）/0.02 Å の値で、解析力そのものの誤差ではない。SevenNet を float64 で動かすことは試したが、`sevenn` 0.12 の checkpoint 互換パッチと fx 定数が float32 固定で失敗した（`model.double()` では直らない）。GRACE の fp32 版は径方向 MLP だけを cuBLAS の fp32 にする設計で、エネルギー総和は倍精度。

結論：calphy の TI（NVT/NPT、サーモスタット付き）では float32 で問題ない。**運用（2026-10-25、ユーザー決定）：MLIP 比較は全工程を単精度で行う**（GRACE nL は QHA も calphy も `grace/<n>l/kk/fp32`、MACE は QHA も `default_dtype float32`、SevenNet は元から float32）。fp64 しか無いのは ACE（`pace`）と GRACE-FS（`grace/fs/kk`）。float64 が要るのは長い NVE（エネルギー保存）と、エネルギー差 1e-5 eV 級を直接使う構造最適化・フォノン有限差分（QHA の 03A で変位 0.01 Å を使うときは、SevenNet の有限差分力誤差 2.5 meV/Å が効くので float64 か変位 0.03 Å 以上にする）。

## Matbench Discovery（2026-10-24 時点、43 モデル）のユニバーサルモデルと、この経路での可否

κ_SRME はフォノン熱伝導の誤差（小さいほど振動の記述が良く、QHA・TI に効く）。順位は leaderboard の CPS 順。

| 順位 | モデル | F1 / κ_SRME | LAMMPS 接続 | 導入作業 | この経路での可否 |
|---|---|---|---|---|---|
| 1–4 | Prophet-OAME-MBD、TECE-OAM-RRA、EquFlashV2、EquiformerV3+DeNS-OAM | 0.93 / 0.07–0.12 | 公開 LAMMPS インターフェースを確認できず | — | 現状不可（ASE で 01・03A のみ） |
| 5 | GRACE-3L-OAM-L | 0.925 / 0.121 | `grace/3l/kk`（`lmp_gpugrace` に導入済み） | kokkos.npz を `grace_models download --kokkos` | 今すぐ可（GPU） |
| 6 | PET-OAM-XL | 0.924 / 0.119 | `pair_style metatomic`（lammps-metatomic、conda 導入可） | 別ビルド 1〜2 時間 | 可（libtorch 型、Kokkos 不要） |
| 8 | eSEN-30M-OAM（fairchem） | 0.925 / 0.170 | `mliap unified`（Python を LAMMPS 内で呼ぶ方式；fairchem 側の変換は要確認） | 1 日 | △ |
| 10, 13 | Nequip-OAM-XL / -L | 0.906 / 0.125 | `pair_nequip`（libtorch） | 別ビルド 1〜2 時間 | 可 |
| 12 | SevenNet-Omni-i12 | 0.906 / 0.192 | `e3gnn`（SevenNet 付属パッチ）または `mliap unified`（公式手順あり） | 別ビルド 1〜2 時間、Python は alamode 環境に導入済み | 可 |
| 14, 18 | GRACE-2L-OAM-L / -OAM | 0.88 / 0.17–0.29 | `grace/2l/kk`（導入済み） | ダウンロードのみ | 今すぐ可 |
| 15 | ORB v3 | 0.905 / 0.210 | 公式の LAMMPS 対応は未確認 | — | △ |
| 16, 20 | DPA-4.0.1-Pro、DPA-3.1-3M-FT | 0.86–0.88 / 0.21–0.47 | `deepmd`（conda-forge の deepmd-kit に同梱） | conda 1 コマンド | 可（最も簡単） |
| 17 | Allegro-OAM-L | 0.895 / 0.319 | `pair_allegro`（libtorch、Kokkos 版あり） | 別ビルド | 可 |
| 22, 36 | MACE-MPA-0、MACE-MP-0 | 0.85 / 0.41、0.67 / 0.68 | `mace`（ACEsuit の LAMMPS fork）または `mliap unified`（公式手順あり） | 別ビルド 1〜2 時間 | 可 |
| 25 | MatterSim v1 5M | 0.862 / 0.575 | 公式の pair style なし | 導入済み（ASE、alamode 環境） | 01・03A のみ |
| 26 | GRACE-1L-OAM | 0.824 / 0.517 | `grace/1l/kk`（導入済み；kokkos 版は medium-base 系） | 導入済み | 今すぐ可（検証済み） |
| 41, 42 | M3GNet、CHGNet | 0.57 / 1.41、0.61 / 1.72 | `m3gnet`（conda 版にあり）、CHGNet は未確認 | — | 精度不足、対象外 |
| — | GRACE-FS-OAM（表外、FS 型） | — | `grace/fs/kk`（導入済み） | 導入済み | 実行中（pk 1469、Al–Li 比較） |

- 「今すぐ可」は GRACE 系だけ（Kokkos 版が `lmp_gpugrace` にある）。層数の比較 FS → 1L → 2L → 3L は追加ビルドなし。
- libtorch 型（PET、NequIP、Allegro、SevenNet、MACE、DeePMD）は pair style 自身が GPU で動くので Kokkos も `hybrid/scaled/kk` も不要。通常ビルドに組み込めば calphy の全モードが GPU で走る。導入順：DeePMD（conda）→ SevenNet（Python 導入済み）→ MACE / NequIP → PET。
- 上位 4 つ（Prophet、TECE、EquFlash、EquiformerV3）は LAMMPS 接続が見つからず、ASE 経由の 01・03A まで。ORB v3 と eSEN は要確認。
- 精度（float32）は制約にならない（上節）。制約は速度：2 層以上の等変モデル（MACE-MPA、SevenNet-Omni、eSEN）は GRACE-FS の 5〜20 倍遅く、例 8 規模で 1 本数時間〜半日。
- 出典：Matbench Discovery leaderboard（https://matbench-discovery.materialsproject.org/）、lammps-metatomic（franken の interface_metatomic）、LAMMPS pair_style mliap、SevenNet / MACE / CURATOR の ML-IAP ガイド。

## libtorch 系 MLIP を calphy で回すときの注意（2026-10-24、SevenNet で実際に起きた）

- **`pair_style hybrid/scaled` の中でビリアルが消える**：LAMMPS はサブスタイルに F·r 方式のフラグ（VIRIAL_FDOTR）を渡さない。サブスタイルが自前のビリアルを `no_virial_fdotr_compute = 1` で宣言していないと（SevenNet 0.13 の `pair_e3gnn` がそう）、`if (vflag)` の分岐が飛んで圧力がゼロになり、calphy の NPT（液相の平衡化・reversible scaling）で箱が 12.9 → 91.6 Å に膨張、エネルギーが −10²² eV に発散する。単独の `pair_style e3gnn` では圧力が正しいので plain の MD では気づかない。修正：両コンストラクタに `no_virial_fdotr_compute = 1;` を入れる（`env/lammps-torch/build_sevenn.sh` が自動適用）。修正後は hybrid/scaled 下の軌道が plain と一致し、λ 倍の圧力になる。`pair_mace` は元から宣言済み。
- **検査の手順（新しい pair style を calphy に載せる前に必ず）**：同じ構造で (1) plain、(2) `hybrid/scaled v_lam <style>`（λ = 1）、(3) λ = 1.222 の `run 0` の圧力を比べる（`env/lammps-torch/test/in.seq2`、`in.npt`）。(2) が (1) と一致し、(3) が 1.222 倍なら可。NPT 200〜500 ステップで体積が plain と同じ推移をすることも見る。
- `pair_style mace` は `atom_modify map yes` と `newton on` が要る（無いと segfault）。calphy には `md.init_commands` で渡す（`calphy_block_extra`）。
- SevenNet は OpenEquivariance 無しだと 1 s/step（256 原子）で calphy に使えない。`sevenn patch_lammps --oeq` でビルドし、モデルも `get_model -oeq` で展開する（16 倍速）。
- 同じモデルを ASE（QHA 側）と LAMMPS（calphy 側）の 2 実装で評価することになるので、1 セルでエネルギーを突き合わせる：SevenNet-0 −835.881592（ASE）/ −835.88159180（LAMMPS）、MACE-MPA-0 float64 −831.078825 / float32 −831.07881959、GRACE-2L −830.201231 / −830.20123104 eV（256 原子）。

## 補間関数（CALPHAD 型）を使わない経路（B 系）での可否

| 手法 | 使える MLIP | 条件・計算量 |
|---|---|---|
| 半大正準 MC（`fix atom/swap` + MD） | すべて | 試行ごとに全系エネルギーを前後 2 回計算。EAM の Ag–Cu（2,048 原子、36 点 × 3 温度）は 8 ランクで 25 分/等温線。ACE・GRACE-FS は 1 回のエネルギーが 50〜100 倍重く、GPU で 2,048 原子 0.05 s/回として同じ試行数なら 1 点 1〜2 時間、1 系 100〜200 GPU 時間。試行数と Δμ 点数を絞れば日単位。GPU + `pace/kk` の組合せは未検証（Al–Li ACE で 1 点を流して時間を測るのが最初）。 |
| 分散拘束 SGC（`fix sgcmc`、VCSGC） | 高速な実装は EAM のみ（eam/alloy、eam/fs） | 他の pair style は「全エネルギー再計算・直列 1 プロセス」に落ちるので実質不可。VCSGC が要るなら CE 上の mchammer で代替。 |
| 二相共存 MD（界面法） | すべて、GPU 可 | 通常の MD。EAM の例（6,144 原子 × 400 ps）を ACE で GPU なら 1 本 15〜20 時間、2,048 原子なら数時間。融点・液相線向き。 |
| Gibbs–Duhem 積分 | すべて | 共存 2 相の MD から ΔH・Δx。自作が要る。 |
| CE + MC（icet、SGC / VCSGC、`ftphase.ce`） | 学習エネルギーの計算に ASE で呼べるものすべて（LAMMPSlib 経由の全部、MatterSim・SevenNet、tensorpotential） | MC は CE 上で走るので MLIP の重さは学習だけ（Ag–Cu 631 構造で 3 分）。CE の打ち切り誤差（Ag–Cu で 9 meV/atom）と振動項の欠落が残る。 |
| calphy TI + 離散凸包（A-1、関数なし） | 上表の全部、GPU は ACE・GRACE・SNAP | 現行経路から補間関数を外すだけ。 |

- 「補間式を使わない」こと自体は MLIP を選ばない。EAM でしか安くないのは `fix sgcmc` だけ。
- MLIP で B 系を回す順序：(1) 共存 MD で融点・液相線（GPU、ACE / GRACE-FS）、(2) 固溶限は `fix atom/swap` を GPU で試行数を減らして、または CE+MC（短距離秩序が本質の系）。固溶限の温度依存に振動が効く系（Ag–Cu 型）では MD 込みの `fix atom/swap` が必要で、CE+MC では出ない。
