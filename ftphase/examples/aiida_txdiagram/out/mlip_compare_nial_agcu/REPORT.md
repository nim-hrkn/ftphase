# Ni–Al / Ag–Cu: EAM vs 3 MLIPs (2026-10-31)

固相 QHA のみ（固相 TI なし）、液相 calphy TI、0 GPa。図: `panels.png`（上段 Ni–Al, 下段 Ag–Cu; 左端が EAM 基準 = 図4/図5）。
WorkChain pk: nial_grace_fs 4784, nial_grace_1l 4798, nial_sevenn_0 4813, agcu_grace_fs 4869, agcu_grace_1l 4900, agcu_sevenn_0 4928（全て Finished [0]）。

## 純物質・B2 の固液交点（05 表の G 交点, K）

| | 実験 | EAM (TI) | GRACE-FS-OAM | GRACE-1L fp32 | SevenNet-0 |
|---|---|---|---|---|---|
| Al | 933 | 1040 | > 2000 | 870 | > 2000 |
| Ni | 1728 | 1703 | 1751 | 1694 | < 1500 |
| B2 NiAl | 1911 | 1808 | > 2000 | > 2000 | > 2000 |
| Ag | 1235 | 1278 | 判定不可 (QHA 固相が 1050 K で切れる) | 1093 | 判定不可 (固相 950 K まで) |
| Cu | 1358 | 1326 | 1345 | 1347 | 液相なし |

## 何が起きたか

* GRACE-FS / SevenNet-0 の fcc Al: 1000 K で S_solid (9.35 / 9.21 k_B) が S_liquid (9.06 / 8.80 k_B) を上回る。融解エントロピーが負なので Al は融けない。Al–Li で見た「fcc フォノンが軟らかすぎて固相を過剰安定化」と同じ。GRACE-1L は ΔS_m = 1.45 k_B で正常。
* B2 NiAl は 3 MLIP とも 2000 K まで融けない（QHA のみ。EAM でも QHA は T_m 近傍で 20–45 meV/atom 高すぎた。ここは逆向きで、QHA の非調和誤差だけでは説明できない大きさ: ΔG(2000 K) = +6..+118 meV）。固相 TI なしでは B2 側の結論は出せない。
* Ag–Cu: Cu の融点は FS / 1L とも 1345–1347 K で実験・EAM と合う。Ag 側は QHA の固相が 950–1050 K で不安定化（体積発散）して表が切れ、融点が出ない（1L だけ 1250 K まで残り 1093 K = 実験 −140 K）。共晶は 3 MLIP とも再現しない。
* GRACE-FS Ag–Cu の liquid+liquid 帯 (1110–1320 K) は液相フィットの偽物（x 0.2–0.6）。
* 失敗: nial_grace_1l の液相 x=0.90 が SolidifiedError（pk 5039）。agcu_sevenn_0 の液相 x=0.6, 0.8, 1.0 は `nedges exceeded nedges_upper_bound (pair_e3gnn.cpp:163)` で落ち、x=0.5 も無い → Cu 側に液相なし。
* B2+B2 の細い帯（1L, SevenNet-0）は欠陥系列のフィット雑音。

## 結論

QHA のみの固相では、Al–Li で既に見えた MLIP のフォノン軟化がそのまま融点に出て、Ni–Al / Ag–Cu の相図は EAM 基準（図4/5）とは比べられる形にならない。比較を成立させるには (1) 固相を 2000 原子以上の calphy TI にする（`solids_ti`）、(2) SevenNet-0 の e3gnn `nedges_upper_bound` を上げるか ML-IAP 経路（`mliap unified`）に移す、(3) Ag–Cu の液相掃引を 900 K 付近まで下げる、が必要。
