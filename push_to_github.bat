@echo off
echo ========================================
echo   Pushing BouabidTransfer to GitHub
echo ========================================
echo.

REM Check if git is available
where git >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo Or use GitHub Desktop: https://desktop.github.com/
    echo.
    pause
    exit /b 1
)

REM Change to project directory
cd /d "%~dp0"

REM Initialize git if needed
if not exist ".git" (
    echo Initializing Git repository...
    git init
    if errorlevel 1 (
        echo ERROR: Failed to initialize git
        pause
        exit /b 1
    )
)

REM Add remote if not exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Adding remote repository...
    git remote add origin https://github.com/ihopepg/BouabidTransfer.git
)

REM Check current remote
echo Current remote:
git remote -v
echo.

REM Add all files
echo Adding all files...
git add .
if errorlevel 1 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)

REM Commit
echo.
echo Committing changes...
git commit -m "Initial commit: BouabidTransfer - Professional iPhone to PC Data Transfer Application"
if errorlevel 1 (
    echo WARNING: No changes to commit or commit failed
    echo This is OK if files are already committed
)

REM Set branch to main
git branch -M main

REM Push to GitHub
echo.
echo Pushing to GitHub...
echo NOTE: You may be prompted for GitHub credentials
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Possible reasons:
    echo   1. Authentication required (use Personal Access Token)
    echo   2. Repository doesn't exist or you don't have access
    echo   3. Network issues
    echo.
    echo Solutions:
    echo   - Use GitHub Desktop (easier)
    echo   - Use Personal Access Token instead of password
    echo   - Check repository URL and permissions
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS! Code pushed to GitHub
echo ========================================
echo.
echo Repository: https://github.com/ihopepg/BouabidTransfer
echo.
pause


