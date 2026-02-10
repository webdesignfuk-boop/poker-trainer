# 🚀 セットアップガイド

## インストール手順

### 1. 必要な環境
- Python 3.8 以上
- pip（Pythonパッケージマネージャー）

### 2. Pythonのインストール確認

ターミナル（またはコマンドプロンプト）で以下のコマンドを実行：

```bash
python --version
```

または

```bash
python3 --version
```

バージョンが表示されればOKです。表示されない場合は、[Python公式サイト](https://www.python.org/downloads/)からダウンロードしてインストールしてください。

### 3. Flaskのインストール

#### macOS / Linux の場合：

```bash
pip install flask
```

または

```bash
pip3 install flask
```

#### Windows の場合：

```bash
pip install flask
```

### 4. ゲームの起動

#### 方法A: 起動スクリプトを使用（簡単）

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```
start.bat をダブルクリック
```

#### 方法B: 手動起動

```bash
python server.py
```

または

```bash
python3 server.py
```

### 5. ブラウザでアクセス

サーバーが起動したら、ブラウザで以下のURLを開きます：

```
http://localhost:5000
```

または

```
http://127.0.0.1:5000
```

## トラブルシューティング

### エラー: "Flask not found" または "No module named 'flask'"

→ Flaskがインストールされていません。再度インストールしてください：
```bash
pip install flask
```

### エラー: "Address already in use" または "Port 5000 is already in use"

→ ポート5000が既に使用されています。以下の方法で解決：

1. 他のアプリケーションを終了する
2. または、server.py の最後の行を編集してポート番号を変更：
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 5001に変更
```

### ブラウザでページが表示されない

1. サーバーが正常に起動しているか確認
2. ターミナルにエラーメッセージが表示されていないか確認
3. ブラウザのURLが正しいか確認（`http://localhost:5000`）
4. ファイアウォールがブロックしていないか確認

## システム要件

- **OS**: Windows 10以上、macOS 10.14以上、Linux（Ubuntu 18.04以上推奨）
- **メモリ**: 最低 2GB RAM
- **ディスク**: 最低 100MB の空き容量
- **ブラウザ**: Chrome、Firefox、Safari、Edge の最新版

## 推奨環境

- **メモリ**: 4GB 以上
- **ブラウザ**: Chrome 最新版（最も動作確認済み）
- **画面解像度**: 1280x720 以上

## ゲームの終了方法

1. ブラウザを閉じる
2. ターミナルで `Ctrl + C` を押してサーバーを停止

## サポート

問題が解決しない場合は、以下を確認してください：

1. Python のバージョンが 3.8 以上か
2. Flask が正しくインストールされているか
3. すべてのファイルが同じフォルダにあるか
4. ファイルの読み取り権限があるか

---

楽しいポーカートレーニングを！ 🎰
