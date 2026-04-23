@echo off
title StreamFetch Server
echo ===================================================
echo             StreamFetch Video Downloader
echo ===================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed on this computer!
    echo To use this program, you must install Python.
    echo.
    echo Opening Python download page...
    start "" https://www.python.org/downloads/
    echo.
    echo IMPORTANT: When installing Python, make sure to check the box that says:
    echo "Add python.exe to PATH" at the bottom of the installer!
    echo.
    echo After installing, double-click Start.bat again.
    pause
    exit
)

:: 2. Check and install required packages
echo [INFO] Checking and installing required background tools...
python -m pip install --upgrade -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install required packages. Make sure you have an internet connection.
    pause
    exit
)

:: Clear yt-dlp cache to prevent YouTube 403 Forbidden errors
echo [INFO] Clearing yt-dlp cache...
python -m yt_dlp --rm-cache-dir >nul 2>&1

echo.
echo [SUCCESS] Everything is ready! Starting the server...
echo.
echo ===================================================
echo PLEASE DO NOT CLOSE THIS BLACK WINDOW!
echo The application will run as long as this is open.
echo ===================================================
echo.

:: 3. Download required tools if missing
python download_tools.py

:: 4. Open browser and start the app
start "" http://127.0.0.1:5000
python app.py

pause
