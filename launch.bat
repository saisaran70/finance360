@echo off
title Budget Buddy AI
set "APPDIR=%~dp0"

:: Check if server is already running on port 5000
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% == 0 (
    echo Server already running — opening browser...
    start "" "http://127.0.0.1:5000"
    exit
)

:: Run full setup — migrations, seed categories, demo account
echo Setting up Budget Buddy AI...
"%APPDIR%.venv\Scripts\python.exe" "%APPDIR%setup_db.py"

:: Start the Flask server minimised in background
echo Starting server...
start /min "Budget Buddy AI Server" "%APPDIR%.venv\Scripts\python.exe" "%APPDIR%run.py"

:: Wait for server to be ready (up to 15 seconds)
set attempts=0
:waitloop
timeout /t 1 /nobreak >nul
set /a attempts+=1
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    if %attempts% lss 15 goto waitloop
)

:: Open browser
start "" "http://127.0.0.1:5000"
exit
