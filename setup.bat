@echo off
echo ======================================================
echo   Titanium Downloader - Setup Script
echo ======================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from python.org
    pause
    exit /b
)

:: 2. Create Virtual Environment
echo [1/3] Creating Virtual Environment (.venv)...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b
)

:: 3. Install Dependencies
echo [2/3] Installing dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

:: 4. Done
echo.
echo [3/3] SETUP COMPLETE!
echo.
echo To run the app, simply run: start_app.bat
echo or manual: .venv\Scripts\python.exe app.py
echo.

:: Create a quick start script
echo @echo off > start_app.bat
echo .venv\Scripts\python.exe app.py >> start_app.bat

pause
