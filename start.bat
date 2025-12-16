@echo off
cd /d "%~dp0"
echo Starting DayReview...
start /min python tray_app.py
