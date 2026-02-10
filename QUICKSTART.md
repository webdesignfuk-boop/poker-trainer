# 🚀 クイックデプロイコマンド

このファイルは、デプロイに必要なコマンドをまとめたものです。
詳細な説明は DEPLOY.md を参照してください。

## 前提条件

- Gitがインストールされている
- GitHubアカウントがある
- GitHubにリポジトリ `poker-trainer` を作成済み

---

## コマンド一覧（コピー&ペースト用）

### 1. プロジェクトディレクトリに移動

```bash
cd poker-trainer
```

### 2. Git初期化

```bash
git init
git add .
git commit -m "Initial commit: Poker Trainer App"
```

### 3. GitHubと接続

**重要**: `YOUR_USERNAME` を実際のGitHubユーザー名に変更してください

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/poker-trainer.git
git push -u origin main
```

---

## アップデート時のコマンド

コードを修正した後、以下を実行：

```bash
git add .
git commit -m "Update: 変更内容の説明"
git push
```

→ Render.com が自動的に再デプロイします

---

## よく使うGitコマンド

### 現在の状態を確認
```bash
git status
```

### 変更履歴を確認
```bash
git log --oneline
```

### リモートリポジトリを確認
```bash
git remote -v
```

### ブランチを確認
```bash
git branch
```

---

## トラブルシューティング用コマンド

### リモートURLを再設定
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/poker-trainer.git
```

### 強制プッシュ（注意: データが失われる可能性あり）
```bash
git push -f origin main
```

### 最新の変更を取得
```bash
git pull origin main
```

---

## Render.com デプロイ設定（参考）

これらの設定は `render.yaml` に記載されていますが、
Web UIで手動設定する場合の参考値です：

- **Name**: poker-trainer
- **Region**: Singapore
- **Branch**: main
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn server:app --bind 0.0.0.0:$PORT`
- **Instance Type**: Free

---

## 初回デプロイの完全な流れ（まとめ）

```bash
# 1. プロジェクトディレクトリに移動
cd poker-trainer

# 2. Git初期化
git init
git add .
git commit -m "Initial commit: Poker Trainer App"

# 3. GitHubと接続（YOUR_USERNAMEを変更！）
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/poker-trainer.git
git push -u origin main

# 4. Render.com でデプロイ
# → ブラウザで https://render.com/ にアクセス
# → GitHubでサインイン
# → New + → Web Service
# → poker-trainer を選択
# → Create Web Service
```

---

## 完了！

デプロイが完了すると、以下のようなURLが発行されます：

```
https://poker-trainer.onrender.com
```

または

```
https://poker-trainer-xxxx.onrender.com
```

このURLにアクセスしてゲームを楽しんでください！🎉
