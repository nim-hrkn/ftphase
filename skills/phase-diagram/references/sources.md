# 公式資料と検証例

以下は作成時に参照した資料。機能・入力形式は使用する版で再確認する。

- [calphy公式](https://calphy.org/)：熱力学積分による固液自由エネルギー。
- [calphy入力](https://calphy.org/inputfile.html)：fe/ts、構造、配置交換、UFMなど。
- [calphy液相実装](https://calphy.org/_modules/calphy/liquid.html)：基準系、往復スイッチング、理想気体項、PV項。
- [calphy相図API](https://calphy.org/calphy.html#calphy.phase_diagram.PhaseDiagram)：二元相図、固定組成・限定組成範囲、TDB出力の制約。
- [LAMMPS hybrid/scaled](https://docs.lammps.org/pair_hybrid.html)：係数によるエネルギー・力・応力のスケーリング。
- [icet SQS](https://icet.materialsmodeling.org/advanced_topics/sqs_generation.html)
- [ATAT mcsqs](https://axelvandewalle.github.io/www-avdw/atat/manual/node49.html)
- [ALAMODE QHA ZnO例](https://alamode.readthedocs.io/en/latest/tutorial_pages/zno_qha_relax.html)
- [ALAMODE入力](https://alamode.readthedocs.io/en/latest/anphondir/inputanphon.html)
- [Phonopy定式化](https://phonopy.github.io/phonopy/formulation.html)
- [pycalphad二元相図](https://pycalphad.org/docs/latest/examples/1_Phase_Diagrams/1_BinaryExamples.html)
- [公開TDB案内](https://pycalphad.org/docs/latest/reference/calphad_databases.html)

## Al–Liの例を参照するとき

[Menon et al., 2024](https://www.nature.com/articles/s41524-024-01441-0)：
DFTで学習したACE・HDNNP等、calphy、pyironを用いた有限温度相図。Al側からLi原子分率0.5までを扱う。固相はランダム置換配置で、配置エントロピーは理想混合近似。SQSによる例として紹介しない。

- fcc-Al中のLi固溶限は再現した（図9、表3）。
- AlLi規則相へのAl固溶は十分再現できていない。空孔除外が原因候補だが、空孔追加で再現成功したとの実証ではない。
- phonon計算はポテンシャル検証にも使われるが、この相図の自由エネルギーはMD・熱力学積分を用いる。
- [公開Notebook](https://github.com/pyiron/potential_publication/tree/main/04_phase_diagram)：01_running_calculations、03_HDNNP_phase_diagram、04_ACE_phase_diagram。公開と現環境での実行確認を区別する。

[Shao et al., Al–Liの配置・振動エントロピーを含む第一原理相図](https://arxiv.org/abs/2211.03664)：
クラスター展開・MCによる別経路。calphyによる実証例と混同しない。

## このプロジェクトの資料

プロジェクトルートの `資料/Saengdeejing - CALHAD Database Summary.pdf`：
pp.2–4はGibbsエネルギーとCEF、p.5は端成分の自由エネルギー、pp.6–7は液相相互作用とデータベース構築。p.7に不規則fcc/bcc/hcpの相互作用評価にはSQSが必要との言及があるが、具体的生成・フィット手順は記載されていない。SQSをあらゆる有限温度計算に必須とする根拠にはしない。
