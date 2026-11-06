# 別計算機での再開

このプロジェクトの移行先にはALAMODEとMLIPが導入済み（ユーザー指定、2026-10-21）。まず既存の環境・モデル・実行方法を確認して利用する。導入や転送が実行済みであると推測しない。

## 持ち運ぶ内容

CLAUDE.md、docs/、資料/、skills/phase-diagram/を相対構成を保って移す。構造、モデル重み、実際の入力・結果を別に保持している場合は追加する。環境のバイナリは移植せず、既存環境を有効化する。プロジェクトに同梱された詳細手順は `../../../docs/migration.html`、式と方法の説明は `../../../docs/obsolete_workflow.html`。スキルだけがインストールされている場合、この二つはプロジェクト側を探す。

## 再開時の判断

- ALAMODE・MLIPの導入と、対象系の入力・モデルの妥当性、ツール間の接続は別。実行ファイル、モデル重みのハッシュ、元素、単位、API、CPU/GPU設定を確認する。
- スケジューラ・キュー・アカウント・ランチャー・scratchを確認し、その施設の動作例を利用する。未知のSlurm/PBS設定を作動済みと扱わない。
- AiiDA/MCPは別途確認する。プロファイル・DB・code/computer設定・daemon・プラグイン・MCP接続はフォルダのコピーでは移らない。履歴が必要なら導入版に対応するアーカイブ移行を使う。AiiDAがなければALAMODEとMLIPを直接実行する経路もある。
- calphy/LAMMPS、icet/mcsqs、CE＋MC、TDBと平衡ソフトは選んだ経路に応じて確認する。ALAMODE・MLIP導入済みからこれらの導入済みを推測しない。
- docsの数値例をユーザーの対象系や実計算結果に流用しない。対象系・候補構造・T/P/組成・計算範囲の既存情報を読み、不足を区別する。

## 計算を依頼された後の検証順

1. 小さな構造でMLIPのエネルギー・力・応力と単位を確認する。同じ入力による以前の結果があれば照合する。
2. 一構造・一体積で変位→力→ALAMODEフィット→phononを通す。単一体積はQHAの完成ではなく、接続の検証とする。
3. 液相TIを選ぶ場合はLAMMPSとの接続と全系共通λでのエネルギー・力・ビリアルを検証する。通常MDの成功だけでTIの互換性を認定しない。
4. 独立な構造・組成・体積・変位・反復を分配し、ジョブID、入力・環境・モデル識別子、終了状態、結果を保存する。元の結果を残して未完了の仕事を特定する。
5. 自由エネルギーの単位・参照・量子/古典・配置項を統一して全相の平衡を求める。

本移行依頼は手順の文書化。接続・転送・ジョブ投入を実行済みと記載しない。

## 公開リポジトリ（github.com/nim-hrkn/ftphase、public、2026-11-06 整理）

- `ftphase/`・`docs/`・`skills/` は MIT（`LICENSE`）。`calphy-examples/` は calphy の Academic Software Licence v1.0（非商用；上流の複製と変更点を README に明記すれば配布可、同梱しても MIT 部分には及ばない）、`pycalphad-examples/` は MIT。
- 含めないもの：`資料/`（原典 PDF）、`potentials/`、`papers/`、`data/orchid-*`、pyiron 例のポテンシャルファイル（`resources/lammps/potentials/{ace,atomicrex,hdnnp}/`、出所の pyiron/potentials-workshop-2022 にライセンス表示が無い）。計算機の IP とメールアドレスも書かない（ssh alias と `~/.ssh/config` を参照させる）。
- 履歴から消す手順：`env/ftphase/bin/pip install git-filter-repo` → 他セッションの変更済みファイルを tar で退避 → `echo N | git-filter-repo --force --invert-paths --path … --replace-text repl.txt`（前回の実行があると継続か聞かれる）→ `git remote add origin …`（filter-repo が消す）→ 退避したファイルを戻す → `SSH_AUTH_SOCK=~/.ssh/agent.sock git push --force origin main`。GitHub 側の旧コミットは SHA 直打ちで暫く残る（完全に消すには Support に依頼）。他ホストは rsync 同期なので履歴書き換えの影響は無い。
