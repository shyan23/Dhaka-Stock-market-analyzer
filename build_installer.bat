@echo off
title Building Stock Market Analyzer Installer
echo ========================================
echo Stock Market Analyzer - Installer Build
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Found Python installation
echo.

REM Install build dependencies
echo Installing build dependencies...
pip install pyinstaller pillow

echo.
echo Starting build process...
echo.

REM Run the build script
python installer/build_installer.py

echo.
echo Build completed! Check the 'installer_output' folder for:
echo - StockMarketAnalyzer_Setup.exe (Main installer)
echo - StockMarketAnalyzer_Portable/ (Portable version)
echo - Documentation/ (User guides)
echo.

pause