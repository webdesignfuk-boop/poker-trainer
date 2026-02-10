#!/bin/bash

echo "🃏 テキサスホールデム ポーカートレーナー 🃏"
echo "=========================================="
echo ""
echo "サーバーを起動しています..."
echo ""

cd "$(dirname "$0")"

python server.py
