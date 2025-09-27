@echo off
title Stock Market Analyzer - Complete Installer Creation
echo =========================================================
echo Stock Market Analyzer - Complete Installer Creation
echo =========================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install required packages
echo 📦 Installing build dependencies...
pip install --upgrade pip
pip install pyinstaller pillow

echo.
echo 🔨 Building installer components...
python installer/build_installer.py

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo 📦 Creating final distribution package...
python installer/package_installer.py

if errorlevel 1 (
    echo ❌ Packaging failed!
    pause
    exit /b 1
)

echo.
echo =========================================================
echo 🎉 INSTALLER CREATION COMPLETE! 🎉
echo =========================================================
echo.
echo Your installer package is ready in the 'final_distribution' folder!
echo.
echo What's included:
echo   📱 StockMarketAnalyzer_Setup.exe - Main installer with wizard
echo   📁 StockMarketAnalyzer_Portable/ - No-install portable version
echo   📚 Documentation/ - Complete user guides
echo   📄 README.txt - Instructions for your friend
echo.
echo Your friend can now:
echo   1. Run the .exe for automated installation with setup wizard
echo   2. Choose between Google Sheets or Local Database storage
echo   3. Switch between storage types anytime (data auto-migrates)
echo   4. Use portable version without any installation
echo.
echo Key Features:
echo   ✅ Persistent data storage (local database remembers everything)
echo   ✅ Switch Google Sheets ↔ Local Database anytime
echo   ✅ Automatic data migration and backup
echo   ✅ Complete transaction and portfolio history preserved
echo   ✅ Professional reports and charts
echo.
pause