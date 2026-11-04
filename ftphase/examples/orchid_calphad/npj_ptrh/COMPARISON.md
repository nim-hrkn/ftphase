# Saengdeejing ほか (2026) Pt–Rh の MLIP 熱力学データベースと、本プロジェクト・ORCHID 経路の比較

論文: A. Saengdeejing, R. Sahara, H. Kino, Y. Kawazoe, K. Higashino, T. Chikyow, "The comparison between the Pt-Rh thermodynamic
database from machine learning interatomic potential and first-principles calculations", npj Comput. Mater. 12, 362 (2026),
doi:10.1038/s41524-026-02212-9（`papers/s41524-026-02212-9.pdf`、CC BY-NC-ND 4.0、本文 11 ページ）。テキストは `paper.txt`。

## 論文が何をしたか（p. 1–9）

- 系: Pt–Rh。fcc 固溶体が全組成で 2000 K まで連続。文献で報告された規則相は PtRh (I4₁/amd) と PtRh₃ (I4/mmm) で、室温以下でしか安定でない（p. 1–2）。
- 計算: MLIP = Matlantis の PFP（汎用 NNP）、比較用 DFT = VASP PBE（p. 8–9）。fcc 格子上のクラスター展開で 0 K 基底状態を探索（図 2）、ATAT mcsqs の SQS（16/64 原子）で fcc・bcc・hcp の混合エンタルピーと副格子内混合（表 4、5）、規則相端成分には調和フォノン（力定数 → PDOS → F_vib、式 15）で有限温度の生成自由エネルギー（図 4、5）。DFT では SQS の有限温度計算は行っていない（計算資源の制約、p. 4）。
- CALPHAD 化: 端成分は Neumann–Kopp 近似 ΔG = ΔH − TΔS（ΔS は ΔG(T) の傾き、式 11–12）、規則相は 2 副格子 CEF (Pt,Rh)(Pt,Rh)・(Pt,Rh)₃(Pt,Rh)、不規則 fcc/hcp は Redlich–Kister、液相は「データが無いので理想溶体」（p. 5；表 6 の液相パラメータは fcc と同じ値が書かれている）。パラメータの評価と相図計算は Thermo-Calc（p. 8）。表 6 が TDB 相当。
- 結果: MLIP の 0 K 生成エネルギーは DFT より系統的に 0.7–1.5 kJ/mol-atom 低い（p. 2）。PtRh-I4₁/amd の振動自由エネルギーは 1000 K で 5.5 meV/atom の差（図 4）。fcc 混合エネルギーは等組成で MLIP が 700 J/mol-atom 低く、温度係数の差は約 3 J/mol-atom-K（図 8）。相図（図 9–11、表 7）: 規則–不規則転移は MLIP で PtRh −15 °C・PtRh₃ −38 °C、DFT で −63 °C・−117 °C、文献の MC（Pohl & Albe 2009）は −35 °C。MLIP だけ Pt₃Rh が安定（−127 °C 以下）。固溶幅は文献より狭い（短距離秩序を無視したため、p. 6–7）。fcc+液相の二相域は非常に狭い（p. 6）。
- 結論: MLIP だけから作った熱力学データベースは DFT から作ったものと同程度の相図を与える（要旨、p. 7）。データと TDB は非公開（著者に請求、p. 9）。

## 「ORCHID で有限温度相図は書けるか」の観点で見ると

この論文は、前のやり取りで挙げた 3 経路のうち **経路 3（計算から CALPHAD 記述を組む）** の実例で、ORCHID 論文の PhaseForge と同じ系統にある。違いと共通点:

| 項目 | Saengdeejing 2026 (Pt–Rh) | ORCHID / PhaseForge (Cu–Zr) | 本プロジェクト ftphase (Al–Li, Ni–Al, Ag–Cu) |
|---|---|---|---|
| 入力 | PFP（汎用 MLIP）と DFT、実験データなし | 8 種の汎用 MLIP、ORCHID の文献値で精錬（PhaseForge+） | 系専用 ACE と汎用 MLIP 9 種、実験は照合のみ |
| 固相の有限温度 | 規則相端成分だけ調和フォノン、SQS は MLIP で有限温度（方法は本文に明記なし）、Neumann–Kopp で a + bT | 0 K エネルギーのみ（振動自由エネルギーなし） | QHA（phonopy/ALAMODE）または calphy の固相 TI（2,000 原子以上） |
| 配置エントロピー | CEF の副格子理想混合 + RK 過剰項、短距離秩序なし | 理想混合 | 理想混合・副格子・Wagner–Schottky 熱的欠陥・CE+MC |
| 液相 | 理想溶体（データなし） | 短い液相 MD | calphy の UFM 熱力学積分（組成ごと、温度掃引） |
| 自由エネルギー → 相図 | Thermo-Calc で CALPHAD パラメータに手で当てはめ | PhaseForge → TDB → pycalphad、ESPEI 勾配法で精錬 | 各相 G(T,x) の表 → 下側凸包（CALPHAD 補間は液相の RK fit のみ任意） |
| 検証 | DFT 版 TDB と文献 MC の転移温度 | ORCHID の不変反応・相領域点（再現率 S、2σ 内の数） | ORCHID の不変反応・相領域点（同じ指標、`orchid_compare.py`）、純元素融点 |
| 公開性 | TDB・生データ非公開、Matlantis と Thermo-Calc は商用 | データ CC BY 4.0、コード MIT | コード MIT（ftphase）、環境はすべて conda/pip |

読み取れること:

1. **相図の形を決めている量が違う。** Pt–Rh は規則相が室温以下、液相線は理想に近いので、論文の結論「MLIP と DFT で同程度」は 0 K エネルギーと調和フォノンの差（0.7–1.5 kJ/mol-atom、5.5 meV/atom）が転移温度 50 K 程度の差に収まる、という意味である。本プロジェクトの Al–Li 比較では、0 K の生成エネルギーは MLIP 間でほぼ一致したのに共晶温度は 870 K 前後で ±150 K 散らばり、差の源は固相の振動と液相だった。Pt–Rh の方法を Al–Li・Ni–Al に持ち込むと、液相を理想溶体にした時点で共晶・融点は出ない（Al–Li の液相 L0 は −16 〜 −25 kJ/mol 級で、経路 2 の fit でも液相パラメータが最初に動く）。
2. **液相の扱いが最大の違い。** 論文は液相データなし（p. 5）で、SGTE の 3 評価（ORCHID-Diagrams `PtRh-98Jac`・`02Mam`・`98Spe-LB`）でも Pt–Rh の固液二相域の幅は最大 x 0.037（2142 K 付近）しかなく、理想溶体と区別しにくい系である。本プロジェクトでは液相 TI が計算時間の大半（Al–Li で ACE 9.5 分〜MACE 573 分/本）を占める一方、それ無しには融点も共晶も決まらない。
3. **ORCHID はこの論文の検証には使えない。** ORCHID v2026.10 に Pt–Rh の文献値ファイルは無く（`literature/systems/PT-RH.json` 不在）、あるのは SGTE 評価 3 件（fcc と液相のみ、融点 2041.5/2237 K、規則相なし）と Okamoto 手描き図の内部点 3 つだけ。その手描き図は 605 K・x_Rh 0.50 に fcc+fcc（二相分離）を置いているが、論文（p. 1）と Maisel ら 2012（文献 17）はミシビリティギャップは無いとしている。ORCHID の評価状態図の点を正解に使うと、この系では誤った相集合を基準にすることになる。逆に、論文の規則–不規則転移（−15〜−127 °C）は SGTE 評価にも手描き図にも無いので、ORCHID 側の指標（再現率 S）で測れるのは液相線・固相線（2041–2241 K）だけである。
4. **「MLIP → CALPHAD パラメータ」の再現性。** 論文のパラメータは表 6 に全部載っているので pycalphad で再計算できる（SGTE unary が要る）。しかし当てはめは Thermo-Calc での手作業で、ORCHID 論文が問題にした「評価者の判断が手順に入る」点はそのまま残る。PhaseForge+/ESPEI の勾配法、または本プロジェクトのように CALPHAD 補間を経ずに凸包を取る方法は、この手作業を無くす 2 つの別解である。
5. **本プロジェクトで追試できること。** PFP（Matlantis）は手元に無いが、同じ役割の汎用 MLIP（MACE-MPA-0、SevenNet-MF-ompa、NequIP-OAM-M、GRACE、MatterSim）で Pt–Rh の工程 01–07 は回せる（ordered PtRh/PtRh₃ は点相または副格子相、fcc は SQS、液相は calphy）。得られるのは (a) 液相 TI を入れた場合の固液二相域、(b) QHA/TI の固相で規則–不規則転移温度が論文の −15〜−127 °C（258〜146 K）のどこに来るか、(c) 605 K の fcc 二相分離が出るか、の 3 点で、論文の非公開 TDB が無くても表 7 の数値と比較できる。

図 `ptrh_orchid.png`: ORCHID-Diagrams の SGTE 3 評価（fcc+液相）、手描き図の 3 点（×）、論文の規則化温度（▲、表 7）を一枚に置いたもの。

## 論文の数値の整理（表 2、6、7）

| 量 | MLIP (PFP) | DFT (PBE) |
|---|---|---|
| ΔH_f PtRh-I4₁/amd (eV/atom) | −0.0376 | −0.0236 |
| ΔH_f PtRh₃-I4/mmm | −0.0280 | −0.0200 |
| ΔH_f Pt₃Rh-I4/mmm | −0.0235 | −0.0200 |
| fcc ⁰L (J/mol) | −8725 + 4.53 T | −5000 + 1.3 T |
| fcc ¹L | +1.25 T | +3000 |
| fcc ↔ PtRh 規則化 | −15.3 °C | −62.6 °C |
| fcc ↔ PtRh₃ 規則化 | −38.4 °C | −117.1 °C |
| fcc ↔ Pt₃Rh | −127.5 °C | 不安定 |
| fcc ↔ PtRh + PtRh₃ 共析 | −62.2 °C (x_Rh 0.653) | −124.0 °C (0.693) |
| 文献 MC (Pohl & Albe) fcc ↔ PtRh | −35 °C | |
