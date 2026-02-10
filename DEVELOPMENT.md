# 💻 ローカル開発環境セットアップ

開発やテスト用にローカルでアプリを実行する方法

## 前提条件

- Python 3.8以上
- pip

---

## セットアップ手順

### 1. 仮想環境の作成（推奨）

#### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 開発モードで起動

```bash
export DEBUG=True  # macOS/Linux
set DEBUG=True     # Windows

python server.py
```

### 4. ブラウザでアクセス

```
http://localhost:5000
```

---

## 開発時のヒント

### デバッグモード

デバッグモードでは：
- コード変更時に自動リロード
- 詳細なエラーメッセージ表示
- Flaskデバッガー有効

### ホットリロード

server.py を変更すると自動的に再起動されます。

### テスト実行

```bash
python test_game.py
```

---

## 本番環境との違い

| 項目 | ローカル | Render.com |
|------|---------|-----------|
| ポート | 5000 | 環境変数 |
| デバッグ | ON | OFF |
| サーバー | Flask開発サーバー | Gunicorn |
| URL | localhost | 公開URL |

---

## トラブルシューティング

### ポート5000が使用中

他のポート番号に変更：
```bash
python server.py  # server.py内で変更
```

### 依存関係エラー

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```
