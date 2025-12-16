@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting DayReview...
pythonw tray_app.py
