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
