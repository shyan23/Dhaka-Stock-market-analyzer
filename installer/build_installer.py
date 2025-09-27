#!/usr/bin/env python3
"""
Build Script for Stock Market Analyzer Installer
Creates a standalone executable with PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import tempfile

class InstallerBuilder:
    def __init__(self, source_dir: str, output_dir: str = "dist"):
        self.source_dir = Path(source_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.installer_dir = self.source_dir / "installer"
        self.build_dir = Path(tempfile.mkdtemp(prefix="sma_build_"))

        print(f"Source: {self.source_dir}")
        print(f"Output: {self.output_dir}")
        print(f"Build temp: {self.build_dir}")

    def check_dependencies(self):
        """Check if required build tools are available"""
        required_packages = [
            "pyinstaller",
            "pillow",  # For icon support
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print("Installing required build dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages, check=True)

    def create_installer_spec(self):
        """Create PyInstaller spec file for the installer"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Build paths
source_dir = Path(r"{self.source_dir}")
installer_dir = source_dir / "installer"

a = Analysis(
    [str(installer_dir / "setup_wizard.py")],
    pathex=[str(source_dir), str(installer_dir)],
    binaries=[],
    datas=[
        # Include all source files in the installer
        (str(source_dir / "src"), "src"),
        (str(source_dir / "main.py"), "."),
        (str(source_dir / "requirements.txt"), "."),
        (str(source_dir / "USER_GUIDE_SIMPLE.md"), "."),
        (str(installer_dir / "installer_config.py"), "installer"),

        # Include any additional files
        (str(source_dir / "README.md"), "."),
    ],
    hiddenimports=[
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "json",
        "shutil",
        "subprocess",
        "threading",
        "pathlib",
        "datetime",
        "time",
        "pandas",
        "numpy",
        "streamlit",
        "plotly",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="StockMarketAnalyzer_Setup",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
)
'''

        spec_file = self.build_dir / "installer.spec"
        with open(spec_file, "w") as f:
            f.write(spec_content)

        return spec_file

    def build_executable(self):
        """Build the executable using PyInstaller"""
        spec_file = self.create_installer_spec()

        print("Building executable with PyInstaller...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            str(spec_file)
        ]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(self.build_dir), capture_output=True, text=True)

        if result.returncode != 0:
            print("PyInstaller failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

        # Find the built executable
        dist_dir = self.build_dir / "dist"
        exe_files = list(dist_dir.glob("*"))  # Look for any file, not just .exe

        print(f"Looking in: {dist_dir}")
        print(f"Files found: {[f.name for f in exe_files]}")

        if not exe_files:
            print("No executable found in dist directory")
            print("PyInstaller output:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

        # Copy executable to output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        built_exe = exe_files[0]

        # Choose appropriate extension based on platform
        if sys.platform == "win32":
            final_exe = self.output_dir / "StockMarketAnalyzer_Setup.exe"
        else:
            final_exe = self.output_dir / "StockMarketAnalyzer_Setup"

        shutil.copy2(built_exe, final_exe)

        # Make executable on Unix systems
        if sys.platform != "win32":
            os.chmod(final_exe, 0o755)

        print(f"Executable created: {final_exe}")
        return True

    def create_portable_package(self):
        """Create a portable package alongside the installer"""
        print("Creating portable package...")

        portable_dir = self.output_dir / "StockMarketAnalyzer_Portable"
        portable_dir.mkdir(exist_ok=True)

        # Copy application files
        files_to_copy = [
            ("src", "src"),
            ("main.py", "main.py"),
            ("requirements.txt", "requirements.txt"),
            ("USER_GUIDE_SIMPLE.md", "USER_GUIDE_SIMPLE.md"),
            ("installer/installer_config.py", "installer_config.py"),
        ]

        for src_path, dst_path in files_to_copy:
            src = self.source_dir / src_path
            dst = portable_dir / dst_path

            if src.exists():
                if src.is_file():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                else:
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)

        # Create portable launcher
        launcher_content = f'''@echo off
title Stock Market Analyzer (Portable)
cd /d "%~dp0"

echo Stock Market Analyzer - Portable Version
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8+ is required but not found
    echo Please install Python from: https://python.org
    echo.
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\\Scripts\\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
) else (
    call venv\\Scripts\\activate.bat
)

REM Launch application
echo Starting Stock Market Analyzer...
echo Press Ctrl+C to stop the application
echo.
streamlit run main.py

if errorlevel 1 (
    echo.
    echo Application stopped. Press any key to exit.
    pause >nul
)
'''

        with open(portable_dir / "run.bat", "w") as f:
            f.write(launcher_content)

        # Create README for portable version
        readme_content = '''# Stock Market Analyzer - Portable Version

## Quick Start
1. Double-click `run.bat` to start the application
2. Your web browser will open automatically
3. Follow the setup wizard to configure your storage preference

## Requirements
- Python 3.8 or higher
- Internet connection (for stock data)

## Storage Options
- **Google Sheets**: Access data from anywhere, automatic backup
- **Local Database**: Faster, works offline, data stays on this computer

## Switching Storage Types
1. Go to Settings in the app
2. Choose "Storage Settings"
3. Select your preferred storage type
4. Your data will be automatically migrated

## Troubleshooting
- If Python is not found, download from: https://python.org
- For detailed help, see USER_GUIDE_SIMPLE.md
- The app creates a virtual environment automatically

## Features
- 📊 Real-time DSE stock tracking
- 💹 Portfolio management with P&L analysis
- 📈 Interactive charts and technical indicators
- 📋 Transaction recording and history
- 📄 Professional PDF and Excel reports
- 🔄 Data backup and migration between storage types
'''

        with open(portable_dir / "README.md", "w") as f:
            f.write(readme_content)

        print(f"Portable package created: {portable_dir}")

    def create_documentation_package(self):
        """Create comprehensive documentation package"""
        docs_dir = self.output_dir / "Documentation"
        docs_dir.mkdir(exist_ok=True)

        # Copy user guide
        user_guide_src = self.source_dir / "USER_GUIDE_SIMPLE.md"
        if user_guide_src.exists():
            shutil.copy2(user_guide_src, docs_dir / "User_Guide.md")

        # Create installation guide
        install_guide = '''# Installation Guide

## Method 1: Automated Installer (Recommended)
1. Run `StockMarketAnalyzer_Setup.exe`
2. Follow the setup wizard
3. Choose storage type (Google Sheets or Local Database)
4. Click "Install" and wait for completion
5. Launch the application

## Method 2: Portable Version
1. Extract the portable package
2. Run `run.bat`
3. Follow on-screen instructions

## System Requirements
- Windows 10 or later
- Python 3.8+ (will be installed automatically)
- 500MB free disk space
- Internet connection for stock data

## Storage Options

### Google Sheets (Recommended)
- ✅ Access data from anywhere
- ✅ Automatic cloud backup
- ✅ Share data across devices
- ✅ Never lose investment data

### Local Database
- ✅ Faster performance
- ✅ Works without internet
- ✅ Complete data privacy
- ⚠️ Manual backup required

## Switching Storage Types
You can switch between storage types anytime:
1. Open the app
2. Go to Settings → Storage Settings
3. Select new storage type
4. Your data will be automatically migrated

## Troubleshooting
- **Python not found**: Download from python.org
- **Installation fails**: Run as administrator
- **App won't start**: Check Windows Defender/antivirus
- **Data missing**: Check Settings → Migration History

## Support
For issues or questions, refer to the User Guide or check the application's Settings → Help section.
'''

        with open(docs_dir / "Installation_Guide.md", "w") as f:
            f.write(install_guide)

        print(f"Documentation created: {docs_dir}")

    def cleanup(self):
        """Clean up temporary build files"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        print("Build cleanup completed")

    def build(self):
        """Main build process"""
        try:
            print("=== Stock Market Analyzer Installer Build ===")
            print()

            # Check dependencies
            print("1. Checking build dependencies...")
            self.check_dependencies()

            # Build executable
            print("2. Building installer executable...")
            if not self.build_executable():
                print("Build failed!")
                return False

            # Create portable package
            print("3. Creating portable package...")
            self.create_portable_package()

            # Create documentation
            print("4. Creating documentation...")
            self.create_documentation_package()

            print()
            print("=== Build Complete ===")
            print(f"Output directory: {self.output_dir}")
            print("Files created:")
            print(f"  - StockMarketAnalyzer_Setup.exe (Installer)")
            print(f"  - StockMarketAnalyzer_Portable/ (Portable version)")
            print(f"  - Documentation/ (User guides)")
            print()
            print("Your friend can now:")
            print("1. Run the .exe installer for automatic setup")
            print("2. Or use the portable version without installation")
            print("3. Switch between Google Sheets and Local Database anytime")

            return True

        except Exception as e:
            print(f"Build failed with error: {e}")
            return False

        finally:
            self.cleanup()

if __name__ == "__main__":
    # Get source directory
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = Path(__file__).parent.parent

    # Get output directory
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = Path(__file__).parent.parent / "installer_output"

    # Build installer
    builder = InstallerBuilder(source_dir, output_dir)
    success = builder.build()

    if success:
        print("\n🎉 Installer build completed successfully!")
    else:
        print("\n❌ Installer build failed!")
        sys.exit(1)