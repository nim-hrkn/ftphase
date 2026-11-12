# B2 NiAl の triple defect を MLIP で検査する（2026-11-11〜12、ユーザー依頼「1–3 を行う」）

背景: EAM（Purja Pun–Mishin 2009）の Ni–Al では B2 の Al-rich 側の幅（実験 1600 K で x_Ni ≈ 0.45）が出ず、`vacancy_analysis.py` で EAM の triple defect（2 V_Ni + Ni_Al）生成エネルギー 2.82 eV（DFT 1.0–1.3）が原因と分かっていた。

1. **0 K 点欠陥エネルギー**（`nial_defects_mlip.py --mlip <name>`、`defects_table.py` → `out_defects_mlip/TABLE.md`）: 128 サイト、各 MLIP の格子定数、位置緩和（fmax 5 meV/Å）。triple defect: SevenNet-0 0.84、GRACE-1L 1.40、MatterSim-5M 1.50、MACE-MPA-0 1.71、GRACE-FS 1.90、SevenNet-MF-ompa 1.92 eV（EAM 2.82、DFT 1.0–1.3）。Va_Ni 生成 0.77–1.24 eV（DFT 0.9–1.3）。GRACE-1L は mygarden6 の GPU（Kokkos LAMMPS）、他は CPU。
2. **Wagner–Schottky 再組立**（`reassemble_ws.py --in aiida_txdiagram/out/nial_<mlip>_ti --l12-sites 32` → `<run>/ws/`）: GRACE-1L・SevenNet-0 の B2 Al-rich 端は 1000–1600 K で 0.471 = 54 サイトに空孔 3 個（24/51）の標本端に張り付く。幅はポテンシャルでなく標本化が決めていた。
3. **標本の延長**: `run_aiida.py --system nial --mlip grace-1l --b2-extra --solid-only --T-window 900 2000 --computer mygarden6`（pk 15488：fcc Al・fcc Ni・B2 + 空孔 4–7 個 = x_Ni 0.460/0.449/0.438/0.426、反サイト 8・10 個 = 0.648/0.685；QHA 9 本）→ `mlip_solids_ti.py submit2 --names nial_grace_1l_b2ext_solid --T-hi s03_B2=1700,...`（3,008–3,456 原子の calphy ts、1000 K 開始、pk 15580–15605、mygarden6 GPU、各 1–2 時間）→ `mlip_solids_ti.py assemble` → `merge_b2ext.py nial_grace_1l`（B2 の TI 行を GRACE-1L の stage-2 表に継ぎ足し `out/nial_grace_1l_b2ext_merged/`、Wagner–Schottky で再組立 `ws/`）→ `b2_width_figure.py`（`out_defects_mlip/b2_width_nial_grace_1l.{png,md}`）。

結果（GRACE-1L、B2 の x_Ni 範囲）:

| 扱い | 1000 K | 1200 K | 1400 K | 1600 K |
|---|---|---|---|---|
| (a) WorkChain の組立（構成欠陥、空孔 ≤ 3） | 0.476–0.611 | 0.471–0.611 | 0.471–0.611 | 0.471–0.611 |
| (b) 同じ表、Wagner–Schottky | 0.471–0.611 | 0.471–0.611 | 0.471–0.611 | 0.471–0.611 |
| (c) + 拡張セル 6 本、Wagner–Schottky | 0.463–0.575 | 0.426–0.655 | 0.426–0.685 | **0.445**–0.600 |
| SGTE AlNi-01Dup-4sl の B2 境界点 | 0.456–0.599 | 0.440–0.627 | 0.410–0.664 | 0.431–0.714 |

- Al-rich 端: (c) で 1600 K 0.445（評価 0.431、実験 ≈ 0.45）、1200–1400 K 0.426（新しい標本端 = 空孔 7 個；評価 0.41–0.44）。triple defect 1.40 eV の GRACE-1L は標本を延ばすだけで実験の幅を再現する。EAM の幅ゼロはポテンシャル側（2.82 eV）の問題だったと確定。
- Ni-rich 端: 反サイト 8・10 個のセルを足すと 0.575–0.685 と温度ごとに跳ぶ。B2+L1₂ の共通接線は L1₂ 側の欠陥データ（各枝 1 セル）に依存し、反サイトの線形欠陥エネルギーが濃い濃度まで伸びすぎる。L1₂ 側の標本を増やすか、反サイトに二次の項を入れるのが次の課題。
- 多空孔 B2 セルの Frenkel–Ladd は 1000 K 開始で 6 本とも完走（1300 K 開始では原子が抜けた前例）。

## 追記（2026-11-12）：L1₂ の欠陥セルを増やした

`run_aiida.py --system nial --mlip grace-1l --l12-extra --solid-only`（pk 15876：Ni→Al 2・3・4 個 = x_Ni 0.6875 / 0.656 / 0.625、Al→Ni 2・3 個 = 0.8125 / 0.844；32 サイト）→ `mlip_solids_ti.py submit2 --names nial_grace_1l_l12ext_solid`（2,048 原子 TI、1200→1615 K、pk 16137–16157）→ `merge_b2ext.py nial_grace_1l`（B2 と L1₂ の TI 行を継ぎ足し `out/nial_grace_1l_b2l12ext_merged/ws/`）。

| 境界 | 1200 K | 1400 K | 1500 K | SGTE AlNi-01Dup-4sl |
|---|---|---|---|---|
| L1₂ の Al-rich 端 | 0.741 | 0.744 | 0.747 | 0.724–0.738 |
| L1₂ の Ni-rich 端 | 0.785 | 0.780 | 0.777 | （FCC_4SL として fcc Ni と連続） |
| B2 の Ni-rich 端 | 0.685 | 0.685 | 0.685 | 0.627–0.664 |

- L1₂ の Al-rich 端は標本端 0.719（反サイト 1 個）から離れ、評価の 0.02 以内に来た。L1₂ 側の標本不足は解消。
- B2 の Ni-rich 端は L1₂ を増やしても 0.685（反サイト 10 個 = B2 の標本端）のまま。標本不足ではなく、GRACE-1L が Ni 過剰の B2 を過安定にしている可能性が高い（Ni_Al 反サイト生成 0.81 eV）。確かめるには反サイト 12–14 個（x_Ni 0.72–0.76）の B2 セルが要る。
- 1200 K に境界の段差がある（L1₂ の TI が 1200 K 開始、その下は QHA）。
