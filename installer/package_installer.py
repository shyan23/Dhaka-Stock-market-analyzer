#!/usr/bin/env python3
"""
Package the complete installer distribution
Creates a final zip file with all components
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

class InstallerPackager:
    def __init__(self, project_dir: str, output_dir: str = "final_distribution"):
        self.project_dir = Path(project_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.installer_output = self.project_dir / "installer_output"

    def create_final_package(self):
        """Create the final distribution package"""
        print("=== Creating Final Distribution Package ===")
        print()

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Create versioned folder
        version = "1.0.0"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        dist_name = f"StockMarketAnalyzer_v{version}_{timestamp}"
        dist_dir = self.output_dir / dist_name

        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        dist_dir.mkdir()

        print(f"Creating distribution: {dist_name}")

        # 1. Copy installer executable (check both .exe and no extension)
        exe_file = self.installer_output / "StockMarketAnalyzer_Setup.exe"
        exe_file_unix = self.installer_output / "StockMarketAnalyzer_Setup"

        if exe_file.exists():
            shutil.copy2(exe_file, dist_dir / "StockMarketAnalyzer_Setup.exe")
            print("✅ Installer executable copied (Windows)")
        elif exe_file_unix.exists():
            shutil.copy2(exe_file_unix, dist_dir / "StockMarketAnalyzer_Setup")
            # Also create a .exe copy for distribution
            shutil.copy2(exe_file_unix, dist_dir / "StockMarketAnalyzer_Setup.exe")
            print("✅ Installer executable copied (Unix/Linux)")
        else:
            print("❌ Installer executable not found! Run build_installer.py first")

        # 2. Copy portable version
        portable_src = self.installer_output / "StockMarketAnalyzer_Portable"
        if portable_src.exists():
            portable_dst = dist_dir / "StockMarketAnalyzer_Portable"
            shutil.copytree(portable_src, portable_dst)
            print("✅ Portable version copied")

        # 3. Copy documentation
        docs_src = self.installer_output / "Documentation"
        if docs_src.exists():
            docs_dst = dist_dir / "Documentation"
            shutil.copytree(docs_src, docs_dst)
            print("✅ Documentation copied")

        # 4. Create distribution README
        self.create_distribution_readme(dist_dir)
        print("✅ Distribution README created")

        # 5. Create checksums
        self.create_checksums(dist_dir)
        print("✅ Checksums created")

        # 6. Create ZIP file
        zip_file = self.create_zip_package(dist_dir)
        print(f"✅ ZIP package created: {zip_file.name}")

        print()
        print("=== Distribution Complete ===")
        print(f"Distribution folder: {dist_dir}")
        print(f"ZIP package: {zip_file}")
        print()
        print("Contents:")
        print("📁 StockMarketAnalyzer_Setup.exe - Main installer")
        print("📁 StockMarketAnalyzer_Portable/ - Portable version")
        print("📁 Documentation/ - User guides")
        print("📄 README.txt - Distribution instructions")
        print("📄 checksums.txt - File verification")

        return zip_file

    def create_distribution_readme(self, dist_dir: Path):
        """Create README for distribution"""
        readme_content = f'''Stock Market Analyzer - Distribution Package
==========================================

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Version: 1.0.0

CONTENTS
--------
1. StockMarketAnalyzer_Setup.exe - Main installer with setup wizard
2. StockMarketAnalyzer_Portable/ - Portable version (no installation required)
3. Documentation/ - Complete user documentation
4. checksums.txt - File integrity verification

INSTALLATION OPTIONS
--------------------

Option 1: Automated Installation (Recommended)
- Double-click "StockMarketAnalyzer_Setup.exe"
- Follow the setup wizard
- Choose between Google Sheets or Local Database storage
- Application will be installed and ready to use

Option 2: Portable Version
- Extract "StockMarketAnalyzer_Portable" folder anywhere
- Double-click "run.bat" inside the folder
- No installation required, runs directly

SYSTEM REQUIREMENTS
-------------------
- Windows 10 or later
- Python 3.8+ (automatically installed by main installer)
- 500MB free disk space
- Internet connection for stock data

FEATURES
--------
📊 Real-time DSE (Dhaka Stock Exchange) stock tracking
💹 Portfolio management with profit/loss analysis
📈 Interactive charts and technical indicators
📋 Transaction recording with smart price filling
📄 Professional PDF and Excel report generation
🔄 Data backup and migration between storage types
🌐 Google Sheets integration for cloud storage
💾 Local database for offline usage

STORAGE SWITCHING
-----------------
Users can switch between Google Sheets and Local Database anytime:
- All data is automatically migrated
- Complete transaction history preserved
- No data loss during switching
- Backup created before each migration

FIRST-TIME SETUP
----------------
1. Run the installer or portable version
2. Choose storage method (Google Sheets or Local Database)
3. For Google Sheets: Follow OAuth setup wizard
4. For Local Database: Data stored locally on computer
5. Start tracking stocks and recording transactions

SUPPORT & DOCUMENTATION
-----------------------
- User_Guide.md - Complete step-by-step instructions
- Installation_Guide.md - Detailed installation help
- Built-in help system within the application

TECHNICAL NOTES
---------------
- The installer creates a virtual environment automatically
- All Python dependencies are managed automatically
- Desktop shortcuts and start menu entries created
- Uninstaller available through Windows Programs & Features

For technical support or questions, refer to the documentation
or the built-in help system within the application.

Enjoy tracking your DSE investments! 📈
'''

        with open(dist_dir / "README.txt", "w") as f:
            f.write(readme_content)

    def create_checksums(self, dist_dir: Path):
        """Create checksums for file verification"""
        import hashlib

        checksums = []

        for file_path in dist_dir.rglob("*"):
            if file_path.is_file() and file_path.name != "checksums.txt":
                # Calculate MD5 hash
                md5_hash = hashlib.md5()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)

                relative_path = file_path.relative_to(dist_dir)
                checksums.append(f"{md5_hash.hexdigest()}  {relative_path}")

        # Write checksums file
        with open(dist_dir / "checksums.txt", "w") as f:
            f.write("MD5 Checksums for Stock Market Analyzer Distribution\\n")
            f.write("=" * 55 + "\\n\\n")
            for checksum in checksums:
                f.write(checksum + "\\n")

    def create_zip_package(self, dist_dir: Path) -> Path:
        """Create ZIP package of the distribution"""
        zip_path = self.output_dir / f"{dist_dir.name}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file_path in dist_dir.rglob("*"):
                if file_path.is_file():
                    arc_path = file_path.relative_to(dist_dir.parent)
                    zipf.write(file_path, arc_path)

        return zip_path

    def run(self):
        """Run the packaging process"""
        try:
            if not self.installer_output.exists():
                print("❌ Installer output directory not found!")
                print("Please run 'build_installer.py' first to create the installer components.")
                return False

            zip_file = self.create_final_package()

            print()
            print("🎉 DISTRIBUTION READY! 🎉")
            print()
            print(f"Send this file to your friend: {zip_file.name}")
            print()
            print("Instructions for your friend:")
            print("1. Extract the ZIP file")
            print("2. Run 'StockMarketAnalyzer_Setup.exe' for guided installation")
            print("3. Or use the portable version without installation")
            print("4. Choose storage type during setup")
            print("5. Start tracking DSE investments!")

            return True

        except Exception as e:
            print(f"❌ Packaging failed: {e}")
            return False

if __name__ == "__main__":
    # Get project directory
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        project_dir = Path(__file__).parent.parent

    # Get output directory
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = Path(__file__).parent.parent / "final_distribution"

    # Package installer
    packager = InstallerPackager(project_dir, output_dir)
    success = packager.run()

    if not success:
        sys.exit(1)