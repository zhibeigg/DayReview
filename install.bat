@echo off
chcp 65001 >nul
echo ========================================
echo   DayReview - 一天回顾 | 安装依赖
echo ========================================
echo.

cd /d "%~dp0"

echo 正在安装依赖包...
pip install -r requirements.txt

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 使用方法:
echo   1. 命令行模式: python main.py
echo   2. 托盘模式:   python tray_app.py
echo.
echo 首次使用请编辑 config.py 填写 API 密钥
echo.
pause
