

@echo off
title GreenGrid AI — Launching...
echo.
echo  ========================================
echo   GreenGrid AI v1.0
echo   Distributed Energy Resource Management
echo  ========================================
echo.

:: Move to project folder (same folder as this bat file)
cd /d "%~dp0"

:: Install / verify all dependencies
echo  Checking and installing dependencies...
echo  (This may take a moment on first run)
echo.
pip install -r requirements.txt --quiet
echo.
echo  Dependencies ready.
echo.

:: Launch Streamlit
echo  Starting application, please wait...
echo.
echo  Opening browser at http://localhost:8501
echo  Press Ctrl+C in this window to stop the app.
echo.
streamlit run app.py --server.headless false

pause

