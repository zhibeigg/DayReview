@echo off
echo ========================================
echo   DayReview - Install Dependencies
echo ========================================
echo.

cd /d "%~dp0"

echo Installing dependencies...
python -m pip install -r requirements.txt

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Usage:
echo   1. CLI mode:  python main.py
echo   2. Tray mode: python tray_app.py
echo.
echo Edit config.py to set your API key before first use.
echo.
pause
