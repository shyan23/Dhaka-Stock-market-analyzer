#!/usr/bin/env python3
"""
Stock Market Analyzer - Executable Builder
Creates Windows executable with installer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('config.py', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'plotly',
        'redis',
        'gspread',
        'google.auth',
        'google.auth.oauthlib',
        'google.auth.httplib2',
        'googleapiclient',
        'yfinance',
        'requests',
        'beautifulsoup4',
        'lxml',
        'python-dotenv',
        'schedule',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StockMarketAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('StockMarketAnalyzer.spec', 'w') as f:
        f.write(spec_content)

def create_installer_script():
    """Create NSIS installer script"""
    nsis_script = '''!define APPNAME "Stock Market Analyzer"
!define COMPANYNAME "StockAnalyzer"
!define DESCRIPTION "A comprehensive stock market analysis application"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!define HELPURL "https://github.com/your-repo/stock-market-analyzer"
!define UPDATEURL "https://github.com/your-repo/stock-market-analyzer"
!define ABOUTURL "https://github.com/your-repo/stock-market-analyzer"

!define INSTALLSIZE 150000
!define INSTALLER "StockMarketAnalyzer_Setup.exe"

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${APPNAME}"
Name "${APPNAME}"
Icon "icon.ico"
outFile "${INSTALLER}"
!include LogicLib.nsh

page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    setOutPath $INSTDIR
    
    file "StockMarketAnalyzer.exe"
    file "*.dll"
    file "src\\*"
    file "config.py"
    file "requirements.txt"
    file "README.md"
    
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    createDirectory "$SMPROGRAMS\\${APPNAME}"
    createShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\StockMarketAnalyzer.exe" "" "$INSTDIR\\StockMarketAnalyzer.exe"
    createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\StockMarketAnalyzer.exe" "" "$INSTDIR\\StockMarketAnalyzer.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\\"$INSTDIR$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\\"$INSTDIR\\StockMarketAnalyzer.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "uninstall"
    delete "$INSTDIR\\StockMarketAnalyzer.exe"
    delete "$INSTDIR\\*.dll"
    delete "$INSTDIR\\src\\*"
    delete "$INSTDIR\\config.py"
    delete "$INSTDIR\\requirements.txt"
    delete "$INSTDIR\\README.md"
    delete "$INSTDIR\\uninstall.exe"
    
    rmDir /r "$INSTDIR\\src"
    rmDir "$INSTDIR"
    
    delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
    rmDir "$SMPROGRAMS\\${APPNAME}"
    delete "$DESKTOP\\${APPNAME}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
sectionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # Create spec file
    create_spec_file()
    
    # Run PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'StockMarketAnalyzer.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building executable: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def create_installer():
    """Create Windows installer using NSIS"""
    print("📦 Creating installer...")
    
    # Create NSIS script
    create_installer_script()
    
    # Check if NSIS is available
    try:
        subprocess.run(['makensis', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ NSIS not found. Please install NSIS to create installer.")
        print("   Download from: https://nsis.sourceforge.io/Download")
        return False
    
    # Build installer
    try:
        subprocess.run(['makensis', 'installer.nsi'], check=True)
        print("✅ Installer created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating installer: {e}")
        return False

def create_portable_package():
    """Create portable package without installer"""
    print("📁 Creating portable package...")
    
    dist_dir = Path('dist/portable')
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable and dependencies
    exe_path = Path('dist/StockMarketAnalyzer.exe')
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir)
    
    # Copy source files
    src_dir = dist_dir / 'src'
    if Path('src').exists():
        shutil.copytree('src', src_dir, dirs_exist_ok=True)
    
    # Copy config files
    for file in ['config.py', 'requirements.txt', 'README.md']:
        if Path(file).exists():
            shutil.copy2(file, dist_dir)
    
    # Create run script
    run_script = dist_dir / 'run.bat'
    with open(run_script, 'w') as f:
        f.write('@echo off\n')
        f.write('echo Starting Stock Market Analyzer...\n')
        f.write('StockMarketAnalyzer.exe\n')
        f.write('pause\n')
    
    print("✅ Portable package created in dist/portable/")

def main():
    """Main build function"""
    print("🚀 Stock Market Analyzer - Executable Builder")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Build executable
    if not build_executable():
        print("❌ Build failed. Please check the errors above.")
        return
    
    # Ask user what to create
    print("\n📦 Choose packaging option:")
    print("1. Windows Installer (requires NSIS)")
    print("2. Portable Package")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        create_installer()
    
    if choice in ['2', '3']:
        create_portable_package()
    
    print("\n🎉 Build process completed!")
    print("📁 Check the 'dist' folder for your executable files.")

if __name__ == "__main__":
    main()
