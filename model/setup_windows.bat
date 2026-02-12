@echo off
REM Sentinel-AI Setup Script for Windows
REM This script installs tensorflow-cpu to avoid DLL issues on Windows

echo ============================================
echo Sentinel-AI - TensorFlow Fix for Windows
echo ============================================
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10 or 3.11
    pause
    exit /b 1
)

echo.
echo Step 1: Uninstalling old TensorFlow (if present)...
pip uninstall -y tensorflow tensorflow-intel 2>nul
echo.

echo Step 2: Installing tensorflow-cpu (stable version for Windows)...
pip install tensorflow-cpu==2.13.0
if errorlevel 1 (
    echo WARNING: tensorflow-cpu 2.13.0 failed, trying 2.12.0...
    pip install tensorflow-cpu==2.12.0
)

echo.
echo Step 3: Installing other dependencies...
pip install -r requirements.txt

echo.
echo ============================================
echo Installation complete!
echo ============================================
echo.
echo Now run: python app/app.py
echo.
pause

