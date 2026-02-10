@echo off
echo 🃏 テキサスホールデム ポーカートレーナー 🃏
echo ==========================================
echo.
echo サーバーを起動しています...
echo.

cd /d %~dp0

python server.py

pause
