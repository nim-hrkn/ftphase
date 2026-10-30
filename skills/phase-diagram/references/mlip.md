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
| ML-IAP unified（MACE、SevenNet、MatterSim、NequIP、MatGL の Python モデル） | `mliap`, `mliap/kk` | ○（conda 版、Kokkos 結合あり） | × | × — **4 本目 `env/lammps-gpu-mliap/bin/lmp_gpumliap` で ○**（下の「LAMMPS が MLIP を使う仕組み」） |
| RANN | `rann` | × | ○ | × |

- GPU の calphy は `hybrid/scaled/kk` が要るので自前ビルドの 2 つだけ。conda 版 LAMMPS は GRACE の kk 版を持つが calphy の GPU 実行には使えない。`calculation_block(gpu=True)` が `<style>/kk` の有無で弾く。
- ASE 経由のみ（QHA・0 K 検証に使える、calphy には使えない）：`alamode` 環境の MatterSim・SevenNet、mygardenx1 の tensorpotential（GRACE 全モデル）・pyace。env/ftphase には torch・pyace は無い。
- 手元のポテンシャル：ACE Al–Li（`AlLi-6gen-18May.yace`）、`potentials/grace/`（GRACE-FS-OAM.yaml、GRACE-1L-OMAT-medium-base-fp64 kokkos.npz；他 44 モデルは `grace_models download`）、EAM（Al–Li、Ni–Al Mishin 2009、Ag–Cu Williams 2006、Cu）。
- 2026-10-24 時点で使えなかったもの：MACE、SevenNet の LAMMPS 版（`e3gnn`）、NequIP/Allegro、CHGNet、DeePMD、UF3、POD。その後 MACE・SevenNet は専用ビルド `env/lammps-torch`（10-24）と ML-IAP unified の `lmp_gpumliap`（10-30）で使える。残り：fairchem（UMA/eSEN）は `fix external` のみで `hybrid/scaled` に入らず calphy 不可、ORB・CHGNet は公式経路なし。
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

## MLIP 比較の結果（ACE Al–Li、同じ WorkChain、2026-10-28 完了）

| MLIP | E_form Al₃Li / B32 (meV/atom) | V fcc Al / bcc Li (Å³/atom) | S fcc Al 300 K（k_B、古典） | Al 融点（固液 G 交点、K） | 最低の不変反応（K） | fcc 固溶限 700 K |
|---|---|---|---|---|---|---|
| ACE | −94 / −179 | 16.54 / 20.40 | 3.31 | 888 | 760–770 | 0.140 |
| GRACE-FS-OAM | −130 / −211 | 16.90 / 18.91 | 4.54 | > 925（QHA 打ち切り） | 740–750 | 0.225 |
| GRACE-1L | −94 / −178 | 16.43 / 20.39 | 3.32 | 870 | 720–730 | 0.194 |
| GRACE-2L | −90 / −176 | 16.42 / 20.28 | 3.31 | 922 | 750–760 | 0.168 |
| SevenNet-0 | −111 / −182 | 16.46 / 20.14 | 4.42 | > 1100 | 930–940（B32+fcc → fcc+液相） | 0.250 |
| SevenNet-MF-ompa | −93 / −186 | 16.55 / 20.43 | 3.60 | 992 | 850–860 | 0.132 |
| MACE-MPA-0 | −87 / −178 | 16.47 / 20.17 | 3.64 | 1038 | 770–780 | 0.209 |
| 実験 / DFT | ≈−100 / ≈−190（DFT） | 16.6 / 21.3 | — | 933.5 | 875（共晶、x ≈ 0.24） | ≈0.12 |

- 0 K の生成エネルギーと体積は GRACE-FS 以外ほぼ一致（差 ≤ 20 meV/atom）。相図の差は振動（03A）と液相（03B）から来る。
- 固相の振動エントロピーが ACE より大きい MLIP（GRACE-FS、SevenNet-0：+1.1〜1.2 k_B；MF-ompa、MACE：+0.3 k_B）は固相を過安定化し、Al 融点を上げる。SevenNet-0 は 1100 K まで Al が融けない。
- 共晶・固溶限が実験に最も近いのは SevenNet-MF-ompa（850–860 K、0.132）。ただし Al 融点は 60 K 高い。ACE と GRACE-1L/2L は共晶が 100–150 K 低い。
- 単精度で実行（2026-10-25 のユーザー決定）。GRACE-3L は液相 1 本 6〜11 h のため比較から外した（2026-10-28）。
- 同じ spec・同じセル（seed 固定）・同じ温度格子・同じ fit；工程ごとの差の表と重ね描き図は `ftphase/examples/aiida_txdiagram/out/mlip_compare/`（REPORT.md、overlay.png、7 図を並べた panels.png）。
- **Matbench Discovery との関係**：κ_SRME（フォノン）が相図の結果と対応した（SevenNet-0 は 0.767 で最悪 → Al が融けない；SevenNet-MF-ompa は 0.317 → 共晶が実験に最も近い）。F1（0 K の安定性）は対応しない（0 K の生成エネルギーは 7 種でほぼ同じ）。κ_SRME だけでも足りない：MACE-MPA-0（0.412）も Al 融点が 105 K 高い。Matbench に液相の指標は無いので、基盤モデルを相図に使う前に純元素の融点を確かめる。今回使った GRACE-FS-OAM と OMAT-medium-base 版は表に未掲載（同じ層数の OAM 版を参考値にした）。

### 計算時間（2026-10-29、`ftphase/examples/mlip_bench/`、同じ入力を GPU 1 枚・CPU 4 コアで単独実行）

| MLIP | QHA 1 本（fcc 32 原子、phonopy 256 原子 × 9 体積、GPU） | 液相 calphy 1 本（256 原子、3 反復） | 液相の ACE 比 |
|---|---|---|---|
| ACE | 0.6〜1 分 | 9.5 分 | 1 |
| GRACE-FS-OAM | 18 分（CPU なら 0.3 分） | 26 分 | 2.7 |
| GRACE-1L-OMAT（fp32） | 2.5 分 | 28 分 | 2.9 |
| SevenNet-0 | 2.0 分 | 35 分 | 3.7 |
| GRACE-2L-OMAT（fp32） | 0.9 分 | 98 分 | 10 |
| SevenNet-MF-ompa | 19 分 | 204 分 | 21 |
| MACE-MPA-0（float32） | 3.0 分 | 573 分 | 60 |

- 比較計算の液相も Slurm の `--gres=gpu:1` で GPU を専有していたので、比較計算の実行時間は単独実行と 10 % 以内で一致する（測り直す必要は無い）。QHA は計算した装置が MLIP ごとに違ったので、比べるなら装置を揃える。
- conda 版 LAMMPS の Kokkos は古い GPU 向け（CC 5.0）にビルドされているので、ACE と GRACE-FS の QHA は CPU の方が速い。

### Ni–Al・Ag–Cu への展開（2026-10-30）

`run_aiida.py --system nial|agcu --mlip <name>` で同じ WorkChain を回せる（Ni–Al は B2 の Ni 反サイト・Ni 空孔、L1₂ の反サイト、Ni₂Al₃・NiAl₃、液相 11 組成を 2000 K から組成別の停止温度まで；Ag–Cu は fcc 全組成と液相 7 組成）。MLIP の場合は固相を QHA だけにする（2,000 原子の固相 TI は MLIP では 1 セル数十 GPU 時間）。GRACE-FS・GRACE-1L・SevenNet-0 で投入済み（pk 4784–4928）。

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
- libtorch 型（PET、NequIP、Allegro、SevenNet、MACE、DeePMD）は pair style 自身が GPU で動くので Kokkos も `hybrid/scaled/kk` も不要。通常ビルドに組み込めば calphy の全モードが GPU で走る。導入順：DeePMD（conda）→ SevenNet（Python 導入済み）→ MACE / NequIP → PET。**2026-10-30 追記**：モデルごとのビルドの代わりに ML-IAP unified（1 本の `lmp_gpumliap`）で MACE・SevenNet が動き、MatterSim（公式 `MatterSimMLIAP`）・NequIP（`nequip-prepare-lmp-mliap`）も同じ口で入る（下節）。
- 上位 4 つ（Prophet、TECE、EquFlash、EquiformerV3）は LAMMPS 接続が見つからず、ASE 経由の 01・03A まで。ORB v3 と eSEN は要確認。
- 精度（float32）は制約にならない（上節）。制約は速度：2 層以上の等変モデル（MACE-MPA、SevenNet-Omni、eSEN）は GRACE-FS の 5〜20 倍遅く、例 8 規模で 1 本数時間〜半日。
- 出典：Matbench Discovery leaderboard（https://matbench-discovery.materialsproject.org/）、lammps-metatomic（franken の interface_metatomic）、LAMMPS pair_style mliap、SevenNet / MACE / CURATOR の ML-IAP ガイド。

## libtorch 系 MLIP を calphy で回すときの注意（2026-10-24、SevenNet で実際に起きた）

- **`pair_style hybrid/scaled` の中でビリアルが消える**：LAMMPS はサブスタイルに F·r 方式のフラグ（VIRIAL_FDOTR）を渡さない。サブスタイルが自前のビリアルを `no_virial_fdotr_compute = 1` で宣言していないと（SevenNet 0.13 の `pair_e3gnn` がそう）、`if (vflag)` の分岐が飛んで圧力がゼロになり、calphy の NPT（液相の平衡化・reversible scaling）で箱が 12.9 → 91.6 Å に膨張、エネルギーが −10²² eV に発散する。単独の `pair_style e3gnn` では圧力が正しいので plain の MD では気づかない。修正：両コンストラクタに `no_virial_fdotr_compute = 1;` を入れる（`env/lammps-torch/build_sevenn.sh` が自動適用）。修正後は hybrid/scaled 下の軌道が plain と一致し、λ 倍の圧力になる。`pair_mace` は元から宣言済み。
- **検査の手順（新しい pair style を calphy に載せる前に必ず）**：同じ構造で (1) plain、(2) `hybrid/scaled v_lam <style>`（λ = 1）、(3) λ = 1.222 の `run 0` の圧力を比べる（`env/lammps-torch/test/in.seq2`、`in.npt`）。(2) が (1) と一致し、(3) が 1.222 倍なら可。NPT 200〜500 ステップで体積が plain と同じ推移をすることも見る。
- `pair_style mace` は `atom_modify map yes` と `newton on` が要る（無いと segfault）。calphy 2.3 は `md.init_commands` の `atom_modify` を拒否する（「not in the calphy vocabulary」）ので、ラッパー `lmp_mace.sh` が各 `-in` スクリプトの先頭に挿入する。
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

## LAMMPS が MLIP を使う仕組みと、ML-IAP unified の検証（2026-10-30）

| 仕組み | 内容 | 手元 |
|---|---|---|
| 組み込み pair style（C++） | `pace`, `snap`, `mlip`(MTP), `hdnnp`, `m3gnet`。LAMMPS 本体のパッケージ | conda 版 `lmp_mpi` に全部 |
| fork / パッチの pair style（libtorch・TF） | `e3gnn`(SevenNet), `mace`, `grace/*`, `nequip`/`allegro`, `metatomic`(PET), `matgl`。**本体には未統合**（stable_30Sep2026 の `src/ML-PACE` も pace のみ）。モデルごとに別ビルド | `lmp_sevenn`, `lmp_mace`, `lmp_gpugrace` |
| Kokkos 版 `/kk` | GPU 実行と calphy の `hybrid/scaled/kk` | GRACE・ACE（`lmp_gpugrace`, `lmp_gpu`）、ML-IAP（`lmp_gpumliap`） |
| **ML-IAP `unified`**（PYTHON + ML-IAP + Cython） | `pair_style mliap unified model.pt 0`：pickle した Python オブジェクト（`MLIAPUnified` 派生）を LAMMPS 内蔵の Python に読み込む。非 Kokkos 版は numpy、Kokkos 版（`mliap_unified_couple_kokkos`）は cupy/torch の GPU 配列を直接渡し、`forward_exchange` で多層 GNN のゴースト原子を層ごとに交換（多 rank 対応） | conda 版 `liblammps.so` に両カップリングあり（`PyInit_mliap_unified_couple[_kokkos]`）、`lmp_gpumliap` は Kokkos 版 + `hybrid/scaled/kk` |
| `plugin load` | DeePMD の `libdeepmd_lmp.so` | conda 版に PLUGIN あり、未使用 |
| `fix external` | fairchem（UMA/eSEN/eqV2）の `lmp_fc`。pair style ではないので `hybrid/scaled` に入らず **calphy 不可** | — |

検証（`env/lammps-gpu-mliap/README.md`、Slurm 22988、GPU 専有、108 原子 Al–Li セル）：

- `hybrid/scaled` 下のビリアル：ML-IAP の LJ 実装（conda 版）、MACE-MPA-0 fp64/fp32、SevenNet-0 OEQ の全部で plain = λ=1、λ=1.222 で pe・圧力が正確に 1.222 倍、0.7 model + 0.3 ufm（calphy の液相経路）で圧力非ゼロ。`pair_mliap` は F·r 方式で、SevenNet `e3gnn` の圧力ゼロ問題は起きない。
- エネルギー一致：MACE fp64 −403.92008 eV / 607.25954 bar（`pair_style mace` と全桁一致）、fp32 −403.92018（差 1 µeV/atom）、SevenNet-0 OEQ −401.71027 eV（`e3gnn` と一致）。
- 速度（s/step、108 / 256 原子、RTX 3060 専有）：MACE fp64 ML-IAP 0.391 / 0.944 vs `pair_style mace` 0.467 / 1.036；**MACE fp32 ML-IAP 0.037 / 0.090 vs `pair_style mace` 0.098 / 0.177（2〜2.6 倍速）**；SevenNet-0 OEQ ML-IAP 0.0111 / 0.0132 vs `e3gnn` 0.0076 / 0.0095（専用 pair style の方が 1.4 倍速）。MACE の液相 calphy（573 分/本）は ML-IAP fp32 で半減する見込み。
- 落とし穴：(1) ラッパーの基底クラスのため組み込み Python の env（PYTHONHOME）に `lammps` 純 Python パッケージと `cupy-cuda12x` が要る；(2) `mace_create_lammps_model --format mliap` は cuEquivariance 変換を強制して失敗 → `test/mace_to_mliap.py`；(3) SevenNet は **OEQ 版の export だけ**動く（非 OEQ は内蔵 Python の torch autograd で heap 破損）；(4) 22Jul2025 の `lammps.mliap.loader` は Kokkos モジュール名を知らない（`activate_mliappy_kokkos` を使う）；(5) env/mace の h5py と conda liblammps の libhdf5 が衝突（`import mace.data` を先に）；(6) ビルドは `set -u` の位置、応答ファイル、FindPython、rpath の 4 点（README）。
- 他の MLIP の接続経路（一次資料、2026-10-30）：NequIP/Allegro ≥0.7 は `pair_nequip_allegro`（AOTI）か `nequip-prepare-lmp-mliap`→ML-IAP；MatterSim は公式 `MatterSimMLIAP`→ML-IAP（層ごと exchange あり）；MatGL（TensorNet/M3GNet）は `pair_style matgl(/kk)` 別ビルド；DeePMD（DPA-3）は conda `deepmd-kit lammps` / `plugin load`；PET/UPET は `pair_style metatomic(/kk)`（conda `lammps-metatomic`）；fairchem は `fix external` のみ（calphy 不可）；ORB v3・CHGNet は公式経路なし。GRACE は fork / conda `grace.patch` のまま本体未統合。
- calphy からの実行（2026-10-30、Slurm 22990、`ftphase/examples/calphy_mliap_mace/`）：`calculation_block(gpu=True, lammps_executable=…/lmp_mliap_mace.sh, pair_style="mliap unified <f32 model> 0", pair_coeff="* * Al Li")` で Al 256 原子の液相 ts 1100→700 K を例 8 のジョブ pk 4356（`pair_style mace` fp32）と同設定で流した。G(1100 K) −4.187613 vs −4.187605 eV/atom、700〜1000 K で +0.10〜+0.15 meV/atom（乱数種が異なる独立 run；液相の run 間ばらつき 0.1〜0.5 meV/atom の範囲）。0.085 vs 0.157 s/step、calphy 壁時計 5.14 h vs 9.57 h（1.85 倍速）。`atom_modify map yes` は不要。`ts_dissipation` 1.05 meV/atom は既定しきい値 1 meV をわずかに超過（参照 0.98）。
- WorkChain の切り替え（2026-10-30）：`run_aiida.py` の `MLIPS["mace-mpa-0"]` は ML-IAP（`pair_style: "mliap unified {potential} 0"`、`pair_coeff: "* * Al Li"`、`calphy_gpu: True` で `calphy_extra gpu=True`、`lmp_mliap_mace.sh`）になった。`CalphyCalculation` は `{potential}` を pair_style にも展開する。旧経路は `--mlip mace-mpa-0-pairstyle`。smoke pk 6160。calphy ホストには `env/lammps-gpu-mliap` と、env/mace の cupy・lammps パッケージが要る（mygarden5 のみ。mygarden6 は未配備）。
- MatterSim（2026-10-30、Slurm 22999、GPU 専有）：mattersim 1.2.5 を env/torch に導入（PyPI の torchvision 0.26.0 は torch 2.11.0 と合わず `torchvision::nms does not exist`→cu128 index から入れ直す）。公式の `MatterSimMLIAP`（M3GNet、fp32、層ごと exchange、torch.compile）を `test/mattersim_to_mliap.py` で `potentials/mattersim/mattersim-v1.0.0-{5M,1M}_mliap.pt` に書き出し、`bin/lmp_mliap_mattersim.sh` で実行。108 原子 Al-Li：5M pe −403.17578 eV（ASE 計算器 −403.17511、6 µeV/atom）、圧力 −3403.39 / −3403.49 bar；`hybrid/scaled/kk` λ=1 一致、λ=1.222 正確、ufm 混合正常。速度 s/step（108 / 256 原子）：5M 0.018 / 0.040（初回起動に compile 20 s）、1M 0.012 / 0.015；MACE-MPA-0 fp32 の 0.037 / 0.090 より 2 倍強速い。未了：WorkChain の `qha_calculator: mattersim` と `MLIPS` 登録、`TORCHINDUCTOR_*CACHE*` の設定。
- NequIP/Allegro（2026-10-30 調査、`ftphase/examples/mlip_bench/nequip_allegro_survey.md`）：Matbench の NequIP/Allegro 系で重みが公開されているのは MIR group の OAM/MP パッケージ（CC-BY-4.0、Zenodo 18775904）。選択は **NequIP-OAM-L 0.1**（F1 0.893、κ_SRME 0.166；Allegro-OAM-L は 0.319 でフォノンが劣る）。
- NequIP-OAM-L の導入と検証（2026-10-30、Slurm 23000、GPU 専有）：nequip 0.19.1 + nequip-allegro 0.8.3 を env/torch に導入（lightning が増えるだけ）。`nequip-prepare-lmp-mliap nequip.net:mir-group/NequIP-OAM-L:0.1 X.nequip.lmp.pt --modifiers enable_OpenEquivariance` → `potentials/nequip/`（117 MB、パッケージ内蔵）、ラッパー `bin/lmp_mliap_nequip.sh`。108 原子 Al-Li：ML-IAP pe −404.08095 eV / 2017.74 bar、パッケージを Python で eager 評価した参照（`test/nequip_ref_eager.py`）−404.08091 eV / 2017.68 bar（0.4 µeV/atom）。`hybrid/scaled/kk` λ=1 一致、λ=1.222 正確、ufm 混合正常。速度 s/step（108 / 256 原子）：OEQ compile 0.0125 / 0.029（起動ごとに約 40 s の compile）、OEQ eager 0.016、plain 0.077 / 0.198。ASE 計算器は AOTI compile 済みモデル専用で、GPU compile は `cuda.h` を CPATH に要し、CPU compile は g++ 13 で inductor の生成コードが通らない（torch 2.11）。WorkChain：`--mlip nequip-oam-l`（runner の `qha_calculator: nequip` がジョブ内でデバイスに合わせて compile、dry-run 合格、未実行）。
- WorkChain への登録（2026-10-30）：`--mlip mattersim-5m|mattersim-1m`（`qha_calculator: mattersim`；MatterSim の numpy float32 を JSON に書けず smoke pk 6231 が stage 01 で失敗 → runner で float() に直し pk 6244 を再投入）、`--mlip nequip-oam-l`。ML-IAP MACE の smoke は pk 6160。本番 AiiDA ジョブを約 2.5 時間 hold して先に通し、6160（MACE ML-IAP）・6244（MatterSim-5M）とも 2026-10-31 に assemble まで完走（`out/alli_mace_mpa_0_smoke/`、`out/alli_mattersim_5m_smoke/`）。`--mlip nequip-oam-l` の smoke も pk 6367 で完走（`out/alli_nequip_oam_l_smoke/`）。1 回目 pk 6354 は stage 01 で失敗：torch の AOTInductor が GPU 向け compile に `CUDA_HOME` を要求するため、runner が env/torch（conda の cuda toolkit 入り）を `CUDA_HOME` に設定するよう修正。QHA ジョブは各ジョブ内で約 2 分の compile を行う。
- CPU での MPI 実行（2026-10-30〜31、`env/lammps-cpu-mliap/`、README に詳細）：MatterSim / NequIP / MACE のラッパーは `forward_exchange` を呼ぶので、CPU でも Kokkos 結合が要る（非 Kokkos 結合には無い：Slurm 23008 で確認）。Kokkos Serial + ML-IAP Python の CPU ビルド `lmp_cpumliap` を作ったところ 3 モデルとも落ち、原因は **LAMMPS 本体のバグ**：`CommBrick::forward_comm(Pair*)`/`reverse_comm(Pair*)` が送受信バッファの大きさを確かめずに詰めるのに対し、バッファは初期化時の `pair->comm_forward`（`pair mliap/kk` は `forward_exchange` の呼び出し時にしか設定しない）で確保される。特徴量幅 128 以上でヒープを壊す（4・32 は正常）。GPU 経路は Kokkos バッファを毎回リサイズするので無事だった。`env/patches/lammps-30Sep2026-comm_brick-pair-comm-buffers.patch`（swap ごとに必要幅へ伸ばす）で修正。修正後、108 原子セルの単点で 1 rank / 4 rank とも GPU 値と float32 の丸め（0.1〜1 µeV/atom）で一致：MatterSim 5M −403.17566 / −403.1757（GPU −403.17578）、MACE fp32 −403.92015 / −403.92016（−403.92018）、NequIP-OAM-L −404.08091 / −404.08096（−404.08095）。4 rank = 領域分割 + ghost 交換なので、多 rank の `forward_exchange` の検証にもなった。CPU 用の書き出し：MatterSim は `_mliap_nocompile.pt`、NequIP は `-plain-nocompile`（OEQ は CUDA 専用、CPU の torch.compile は g++ 13 で失敗）、MACE は pickle 内の `config.allow_cpu=True` にした `-f32-cpu.pt`（環境変数は書き出し時にしか読まれない）。nequip 0.19.1 のラッパーは Kokkos 結合＝GPU と決めつけるので `torch.cuda.is_available()` を足すパッチ（`env/patches/`）。Kokkos OpenMP ビルドは torch 同梱の libgomp と二重になり forward で止まる（Serial + MPI rank で使う）。速度（Slurm 23010、4 コア、s/step、108 原子 1 rank / 4 rank、256 原子 4 rank）：MatterSim 5M 0.458 / 0.218 / 0.726（GPU 0.040）、NequIP-OAM-L plain 2.40 / 1.07 / 2.98（GPU OEQ 0.029）。4 rank で 2.1 倍、GPU は 4 コアの 18〜100 倍。CPU 経路は GPU の無いホストと検証用で、calphy 本番には向かない（MatterSim 液相 1 本 ≈ 40 時間/4 コア）。
- TODO（2026-10-30 の判断で先送り）：多 rank（`forward_exchange`）は CPU 4 rank で 3 モデルとも検証済み（上記）、複数 GPU は未検証、cuEquivariance（MACE のテンソル積の CUDA カーネル。QHA と calphy の両方が速くなる見込み。mace-torch 0.3.16 / torch 2.11 / sm_86 との版の整合は未確認）。
