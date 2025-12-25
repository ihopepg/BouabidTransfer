@echo off
echo ========================================
echo   BouabidTransfer - Starting...
echo ========================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.9 or higher.
    echo.
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Run the application
echo Starting BouabidTransfer...
echo.
python src/main.py

REM If there's an error, show it
if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start!
    echo Check the logs folder for details.
    echo.
    pause
)


