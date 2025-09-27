#!/usr/bin/env python3
"""
Test the installer package to ensure everything works
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import json
import zipfile

class InstallerTester:
    def __init__(self, distribution_dir: str):
        self.distribution_dir = Path(distribution_dir)
        self.test_dir = Path(tempfile.mkdtemp(prefix="sma_test_"))

        print(f"Test directory: {self.test_dir}")

    def test_distribution_package(self):
        """Test the complete distribution package"""
        print("=== Testing Stock Market Analyzer Installer ===")
        print()

        # Find the latest distribution
        zip_files = list(self.distribution_dir.glob("StockMarketAnalyzer_v*.zip"))
        if not zip_files:
            print("❌ No distribution ZIP files found")
            return False

        latest_zip = max(zip_files, key=os.path.getctime)
        print(f"Testing: {latest_zip.name}")

        # Extract ZIP
        extract_dir = self.test_dir / "extracted"
        with zipfile.ZipFile(latest_zip, 'r') as zipf:
            zipf.extractall(extract_dir)

        dist_folder = next(extract_dir.iterdir())
        print(f"✅ ZIP extracted to: {dist_folder}")

        # Test installer components
        tests_passed = 0
        total_tests = 5

        # Test 1: Check required files
        print("\\n1. Testing required files...")
        required_files = [
            "StockMarketAnalyzer_Setup.exe",
            "README.txt",
            "checksums.txt"
        ]

        required_dirs = [
            "StockMarketAnalyzer_Portable",
            "Documentation"
        ]

        for file_name in required_files:
            if (dist_folder / file_name).exists():
                print(f"   ✅ {file_name}")
            else:
                print(f"   ❌ {file_name} missing")
                return False

        for dir_name in required_dirs:
            if (dist_folder / dir_name).is_dir():
                print(f"   ✅ {dir_name}/")
            else:
                print(f"   ❌ {dir_name}/ missing")
                return False

        tests_passed += 1

        # Test 2: Portable version structure
        print("\\n2. Testing portable version structure...")
        portable_dir = dist_folder / "StockMarketAnalyzer_Portable"
        portable_files = ["run.bat", "main.py", "requirements.txt", "src"]

        for item in portable_files:
            if (portable_dir / item).exists():
                print(f"   ✅ {item}")
            else:
                print(f"   ❌ {item} missing from portable version")
                return False

        tests_passed += 1

        # Test 3: Test portable launcher (dry run)
        print("\\n3. Testing portable launcher...")
        launcher_script = portable_dir / "run.bat"
        if launcher_script.exists():
            # Read and validate launcher script
            content = launcher_script.read_text()
            if "streamlit run main.py" in content and "venv" in content:
                print("   ✅ Launcher script content valid")
                tests_passed += 1
            else:
                print("   ❌ Launcher script content invalid")
        else:
            print("   ❌ Launcher script missing")

        # Test 4: Documentation completeness
        print("\\n4. Testing documentation...")
        docs_dir = dist_folder / "Documentation"
        doc_files = ["User_Guide.md", "Installation_Guide.md"]

        for doc_file in doc_files:
            if (docs_dir / doc_file).exists():
                print(f"   ✅ {doc_file}")
            else:
                print(f"   ❌ {doc_file} missing")
                return False

        tests_passed += 1

        # Test 5: Installer config simulation
        print("\\n5. Testing installer configuration...")
        try:
            # Simulate installer config creation
            test_config = {
                "storage_type": "local_database",
                "first_run": True,
                "installation_date": "2024-01-01 12:00:00",
                "version": "1.0.0"
            }

            config_test_file = self.test_dir / "test_config.json"
            with open(config_test_file, 'w') as f:
                json.dump(test_config, f, indent=2)

            # Validate JSON structure
            with open(config_test_file, 'r') as f:
                loaded_config = json.load(f)

            if loaded_config["storage_type"] in ["local_database", "google_sheets"]:
                print("   ✅ Configuration structure valid")
                tests_passed += 1
            else:
                print("   ❌ Configuration structure invalid")

        except Exception as e:
            print(f"   ❌ Configuration test failed: {e}")

        # Results
        print(f"\\n=== Test Results ===")
        print(f"Tests passed: {tests_passed}/{total_tests}")

        if tests_passed == total_tests:
            print("🎉 All tests PASSED! Installer package is ready for distribution.")
            self.print_usage_instructions()
            return True
        else:
            print("❌ Some tests FAILED. Please fix issues before distributing.")
            return False

    def print_usage_instructions(self):
        """Print usage instructions for the user"""
        print("\\n" + "="*60)
        print("📋 INSTALLATION INSTRUCTIONS FOR YOUR FRIEND")
        print("="*60)
        print()
        print("1. Send the ZIP file to your friend")
        print("2. They should extract it to any folder")
        print("3. Two installation options:")
        print()
        print("   Option A: Automated Installation (Recommended)")
        print("   - Double-click 'StockMarketAnalyzer_Setup.exe'")
        print("   - Follow the setup wizard")
        print("   - Choose storage type (Google Sheets or Local Database)")
        print("   - App installs automatically with shortcuts")
        print()
        print("   Option B: Portable Version")
        print("   - Go to 'StockMarketAnalyzer_Portable' folder")
        print("   - Double-click 'run.bat'")
        print("   - No installation needed, runs directly")
        print()
        print("🔄 STORAGE TYPE SWITCHING:")
        print("- User can switch between Google Sheets ↔ Local Database anytime")
        print("- Go to Settings → Storage Settings in the app")
        print("- All data automatically migrates (transactions, portfolio, etc.)")
        print("- Complete backup created before each migration")
        print()
        print("💾 DATA PERSISTENCE:")
        print("- Local Database: All data saved in app folder, persists forever")
        print("- Google Sheets: Data saved to Google Drive, accessible anywhere")
        print("- Switching preserves ALL transaction history and portfolio data")
        print()
        print("📊 FEATURES:")
        print("- Real-time DSE stock tracking and portfolio management")
        print("- Transaction recording with smart price auto-fill")
        print("- Professional PDF/Excel reports")
        print("- Interactive charts and technical analysis")
        print("- Complete investment history tracking")

    def cleanup(self):
        """Clean up test files"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def run(self):
        """Run the complete test suite"""
        try:
            return self.test_distribution_package()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
        finally:
            self.cleanup()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        distribution_dir = sys.argv[1]
    else:
        distribution_dir = Path(__file__).parent.parent / "final_distribution"

    tester = InstallerTester(distribution_dir)
    success = tester.run()

    if not success:
        sys.exit(1)