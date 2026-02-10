# 🚀 Render.com デプロイガイド

このガイドに従って、ポーカートレーナーを無料でWeb公開しましょう！

## 📋 必要なもの

1. GitHubアカウント（無料）
2. Render.comアカウント（無料）
3. Git（ローカルにインストール）

所要時間: **約15分**

---

## Step 1: GitHubアカウント作成（既にある場合はスキップ）

1. https://github.com/ にアクセス
2. 「Sign up」をクリック
3. メールアドレス、パスワードを入力
4. アカウント作成完了

---

## Step 2: GitHubに新しいリポジトリを作成

### 方法A: GitHub Web UI で作成（簡単）

1. GitHubにログイン
2. 右上の「+」→「New repository」をクリック
3. 設定:
   - **Repository name**: `poker-trainer`
   - **Description**: `Texas Hold'em Poker Trainer`
   - **Public** を選択（無料）
   - **Initialize this repository with a README** はチェックしない
4. 「Create repository」をクリック

### 作成後に表示されるコマンドをメモしておく

例:
```
https://github.com/あなたのユーザー名/poker-trainer.git
```

---

## Step 3: ローカルでGit初期化とプッシュ

### 3-1: ターミナル（コマンドプロンプト）を開く

**macOS**: Terminal.app
**Windows**: コマンドプロンプトまたはGit Bash

### 3-2: プロジェクトフォルダに移動

```bash
cd poker-trainer
```

### 3-3: Git初期化

```bash
git init
```

### 3-4: ファイルを追加

```bash
git add .
```

### 3-5: コミット

```bash
git commit -m "Initial commit: Poker Trainer App"
```

### 3-6: GitHubリポジトリと接続

```bash
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/poker-trainer.git
```

**注意**: `あなたのユーザー名` を実際のGitHubユーザー名に変更してください

### 3-7: プッシュ

```bash
git push -u origin main
```

初回プッシュ時にGitHubのユーザー名とパスワード（またはトークン）を求められる場合があります。

---

## Step 4: Render.com でデプロイ

### 4-1: Render.com にサインアップ

1. https://render.com/ にアクセス
2. 「Get Started」をクリック
3. **「Sign in with GitHub」をクリック**（推奨）
4. GitHubでの認証を許可

### 4-2: 新しいWeb Serviceを作成

1. ダッシュボードの「New +」ボタンをクリック
2. 「Web Service」を選択

### 4-3: リポジトリを接続

1. 「Connect a repository」セクションで、`poker-trainer` を探す
2. リポジトリが見つからない場合:
   - 「Configure account」をクリック
   - Renderに権限を付与
3. `poker-trainer` の横の「Connect」をクリック

### 4-4: サービス設定

以下の設定を入力（ほとんどは自動入力されます）:

| 項目 | 値 |
|------|-----|
| **Name** | `poker-trainer` |
| **Region** | Singapore (最も近い) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn server:app --bind 0.0.0.0:$PORT` |
| **Instance Type** | **Free** を選択 |

### 4-5: デプロイ開始

1. 一番下の「Create Web Service」をクリック
2. デプロイが自動的に開始されます

---

## Step 5: デプロイ完了を待つ

### デプロイログを確認

画面にリアルタイムでログが表示されます：

```
==> Installing dependencies...
==> Building...
==> Starting server...
==> Your service is live 🎉
```

通常 **2-5分** で完了します。

---

## Step 6: アプリにアクセス 🎉

### URLを確認

デプロイ完了後、画面上部に以下のようなURLが表示されます：

```
https://poker-trainer.onrender.com
```

または

```
https://poker-trainer-xxxx.onrender.com
```

このURLをブラウザで開くと、ポーカートレーナーが動作しています！

---

## 🎮 動作確認

1. URLにアクセス
2. 「新しいハンドを開始」ボタンをクリック
3. ゲームが正常に動作するか確認

---

## ⚠️ 重要な注意点

### スリープモード

Renderの無料プランでは、**15分間アクセスがないとサービスがスリープ**します。

- 次回アクセス時に自動的に起動（30秒程度かかる）
- 使用時間: 月750時間まで（実質無制限）

### 初回アクセスが遅い場合

初回アクセス時や、スリープから復帰する際は30秒ほど待ってください。

---

## 🔗 URLをカスタマイズ（オプション）

### カスタムドメイン設定

Render.comの無料プランでもカスタムドメインが使えます：

1. ダッシュボードで「Settings」タブをクリック
2. 「Custom Domains」セクションへ
3. 所有しているドメインを追加

---

## 🔄 アップデート方法

コードを修正してアップデートする場合：

```bash
# 変更をコミット
git add .
git commit -m "Update: 説明"

# GitHubにプッシュ
git push
```

→ Render.com が自動的に再デプロイします！

---

## 🐛 トラブルシューティング

### エラー: "Build failed"

**確認事項**:
1. `requirements.txt` が存在するか
2. すべてのPythonファイル（.py）がアップロードされているか
3. ビルドログでエラーメッセージを確認

### エラー: "Application Error"

**確認事項**:
1. `server.py` のポート設定が正しいか
2. ログを確認（Render.comのダッシュボード → Logs）

### ページが表示されない

1. デプロイが完了しているか確認
2. URLが正しいか確認
3. ブラウザのキャッシュをクリア

### GitHubにプッシュできない

**認証エラーの場合**:
1. GitHubのPersonal Access Tokenを作成
2. Settings → Developer settings → Personal access tokens → Generate new token
3. パスワードの代わりにトークンを使用

---

## 📊 デプロイ後の確認事項

### ✅ チェックリスト

- [ ] URLにアクセスできる
- [ ] ゲームが正常に起動する
- [ ] カードが正しく表示される
- [ ] AIが正常に動作する
- [ ] ベッティングが機能する
- [ ] フィードバックが表示される

---

## 🎯 次のステップ

### 1. URLをシェア

友達やテストユーザーにURLを共有して、フィードバックをもらいましょう。

### 2. カスタムドメイン設定（オプション）

自分のドメイン（例: poker.yourname.com）を設定できます。

### 3. アプリの改善

ユーザーフィードバックを元に機能を追加・改善していきましょう。

### 4. モバイルアプリ化

Webアプリが完成したら、次はCapacitorでモバイルアプリ化も可能です。

---

## 💬 サポート

問題が解決しない場合：

1. Render.comのドキュメント: https://render.com/docs
2. GitHubのヘルプ: https://docs.github.com/

---

## 🎉 完成！

おめでとうございます！これであなたのポーカートレーナーが世界中からアクセスできるようになりました！

URLをシェアして、多くの人に使ってもらいましょう 🃏🎰

---

**作成日**: 2026年2月10日
**更新日**: 2026年2月10日
