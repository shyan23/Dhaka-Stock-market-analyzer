@echo off
REM Google Sheets Setup for Stock Market Analyzer
REM Simple batch file for non-tech users

setlocal enabledelayedexpansion

echo.
echo ================================================
echo   Google Sheets Setup for Stock Market Analyzer
echo ================================================
echo.

echo This will help you setup Google Sheets for your Stock Market Analyzer.
echo.
echo You need:
echo 1. A Google service account JSON file (usually called service.json)
echo 2. Your Google Sheets ID (from the spreadsheet URL)
echo.

pause

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell is available'" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PowerShell is required but not available
    echo Please ensure PowerShell is installed on your system
    pause
    exit /b 1
)

echo Starting Google Sheets setup wizard...
echo.

REM Run the PowerShell setup script
powershell -ExecutionPolicy Bypass -File "setup-google-sheets.ps1"

if %errorlevel% eq 0 (
    echo.
    echo ✅ Google Sheets setup completed!
    echo.
    echo You can now start the application by running:
    echo   deploy-windows.bat
    echo.
    echo Or double-click deploy-windows.bat
    echo.
) else (
    echo.
    echo ❌ Google Sheets setup encountered an issue
    echo.
    echo You can try again by running this file again,
    echo or contact your developer for assistance.
    echo.
)

pause