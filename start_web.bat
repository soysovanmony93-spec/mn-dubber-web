@echo off
chcp 65001 > nul
title MN DUBBER WEB PRO - Server
echo ========================================================
echo   🚀 MN DUBBER WEB PRO - AI Video Dubbing Studio
echo   (Optimized for iOS, Android & Desktop)
echo ========================================================
echo.
echo [1/2] Checking Python environment...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo [2/2] Starting Web Server...
echo.
python server.py
pause
