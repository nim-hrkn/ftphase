# ORCHID を使う CALPHAD 経路（MLIP 相図との比較用、2026-11-04）

ORCHID v2026.10（arXiv:2610.41164、`data/orchid-v2026.10/`）は文献証拠のデータベースで自由エネルギーの計算法ではない。
MLIP で計算した T–x 図（`aiida_txdiagram/out/*/07_two_phase_regions.tsv`、`nial_eam/`、`alli_ace_txdiagram/out_full/`）と
並べる「CALPHAD の相図」を ORCHID 経由で 2 通り作った。

| 経路 | 入力 | 道具 | 出すもの |
|---|---|---|---|
| 1 | ORCHID-Diagrams（SGTE binary collection, Hallstedt 2025 の TDB から pycalphad 0.11.2 で計算済みの境界・不変反応） | `sgte_diagrams.py` | 評価済み CALPHAD 相図（Al–Li 7、Al–Ni 12、Ag–Cu 6 評価）と MLIP 図への重ね描き |
| 2 | ORCHID の ESPEI データ（実験の不変反応 ZPF、手描き状態図の相領域点、DFT・実験の生成エンタルピー） | ESPEI 0.9.1（`env/pycalphad` に 11-04 追加）+ pycalphad | 自分で評価（fit）した Al–Li の TDB と相図 |

追加で取得した Zenodo 記録（`data/orchid-v2026.10/zip/`、md5 検証済み、README 以外 gitignore）:
ORCHID-Diagrams 10.5281/zenodo.23735859（`orchid-phase-diagrams-v2026.10.zip`, md5 95cbbc0dca646a2ab0185ddf95eb22d0）、
ORCHID ESPEI datasets 10.5281/zenodo.23735788（`orchid-espei-v2026.10.zip`, md5 0c37807a6e0c6441a57feca0c34f9787）。
TDB 本体は ORCHID に同梱されない（Hallstedt, Calphad 89 (2025) 102833 の付録、CC BY 4.0；各 JSON に SHA-256 のみ）。

## 経路 1: `sgte_diagrams.py`

```
./env/ftphase/bin/python -I ftphase/examples/orchid_calphad/sgte_diagrams.py     # -> out/
```

`orchid_calphad/out/sgte_<sys>.png` は系内の全評価、`orchid_calphad/out/overlay_<sys>.png` は MLIP/EAM の図に参照評価（Al–Li `AlLi-20Lon`、
Al–Ni `AlNi-01Dup-4sl`、Ag–Cu `AgCu-04Wit-LB`）の境界（黒）と不変反応（破線）を重ねたもの。`out/sgte_invariants.tsv`
に全評価の不変反応、`out/REPORT.md` に評価一覧・参照不変反応・run の不変反応。

読み:

- Al–Li: 7 評価とも共晶 873–876 K、B32 の合致溶融の最高点 975 K（`AlLi-20Lon`、x 0.499）、B32+Al₂Li₃+L 793 K で、評価間の差は数 K。Li 側（Al₂Li₃ 609 K、AlLi₂ 546 K、Al₄Li₉、Li 側共晶 452 K）の扱いだけが評価で違う（AlLi₂ を持つのは 20Lon/23Cui/24Liu）。`AlLi-24Liu` の `L12_FCC` は分配モデルの fcc（Al₃Li の規則相ではない）。
- Al–Ni: 12 評価。参照 `AlNi-01Dup-4sl` では L1₂+fcc(Ni)+L 1643 K、B2+L1₂+L 1642 K、Ni₂Al₃ 包晶 1401 K、NiAl₃ 包晶 1124 K、Al 側共晶 915 K、B2 の合致溶融の最高点 1953 K、Ni 融点 1728 K。
- Ag–Cu: 6 評価とも共晶 1053 K（x_Cu 0.40、fcc 0.12/0.95）。

MLIP との重ね描きで分かること（図 `overlay_*.png`）:

- Al–Li: どの MLIP も共晶の形は出るが温度が低い（ACE −107 K ほか）。NequIP-OAM-M と SevenNet-MF-ompa が CALPHAD の液相線・共晶に最も近い。全組成 ACE（例 6）は Li 側の Al₂Li₃・Al₄Li₉ の安定域も CALPHAD と同じ順序。
- Al–Ni: EAM（固相 TI、第 5 段）は B2 合致溶融・L1₂ 共晶・Ni 融点が CALPHAD と数十 K で一致。GRACE-1L も Ni 側は一致、GRACE-FS/SevenNet-0 の QHA 固相は B2 が融けず、Al 側は SevenNet-0 で Ni₂Al₃ が出る。
- Ag–Cu: 全 run の格子下限 1100 K が共晶 1053 K より上なので、液相線の傾きと fcc 固溶限だけが比較できる。
