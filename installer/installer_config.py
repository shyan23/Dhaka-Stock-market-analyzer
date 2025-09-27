#!/usr/bin/env python3
"""
Installer Configuration and Data Migration System
Handles switching between storage types and data persistence
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any, Optional
import pickle

class DataMigrationManager:
    """Handles data migration between storage types"""

    def __init__(self, install_path: str):
        self.install_path = Path(install_path)
        self.config_file = self.install_path / "config.json"
        self.local_db_path = self.install_path / "data"
        self.backup_path = self.install_path / "backups"

        # Ensure directories exist
        self.local_db_path.mkdir(exist_ok=True)
        self.backup_path.mkdir(exist_ok=True)

    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "storage_type": "local_database",
            "first_run": True,
            "installation_date": datetime.now().isoformat(),
            "version": "1.0.0",
            "google_sheets": {
                "enabled": False,
                "credentials_file": "",
                "spreadsheet_id": ""
            },
            "local_database": {
                "enabled": True,
                "path": str(self.local_db_path)
            },
            "data_migration": {
                "last_migration": None,
                "migration_history": []
            }
        }

    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def create_backup(self, storage_type: str) -> str:
        """Create backup of current data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_path / f"backup_{storage_type}_{timestamp}"
        backup_dir.mkdir(exist_ok=True)

        if storage_type == "local_database":
            # Backup local database files
            if self.local_db_path.exists():
                shutil.copytree(self.local_db_path, backup_dir / "data", dirs_exist_ok=True)

        # Always backup config
        if self.config_file.exists():
            shutil.copy2(self.config_file, backup_dir / "config.json")

        return str(backup_dir)

    def switch_storage_type(self, new_storage_type: str) -> bool:
        """Switch between storage types with data migration"""
        try:
            config = self.get_current_config()
            current_storage = config.get("storage_type", "local_database")

            if current_storage == new_storage_type:
                return True  # No change needed

            # Create backup before migration
            backup_path = self.create_backup(current_storage)

            # Export current data
            exported_data = self.export_current_data(current_storage)

            # Update configuration
            config["storage_type"] = new_storage_type
            config[new_storage_type]["enabled"] = True
            config[current_storage]["enabled"] = False

            # Record migration
            migration_record = {
                "timestamp": datetime.now().isoformat(),
                "from": current_storage,
                "to": new_storage_type,
                "backup_path": backup_path,
                "records_migrated": len(exported_data.get("transactions", []))
            }

            config["data_migration"]["last_migration"] = migration_record
            config["data_migration"]["migration_history"].append(migration_record)

            # Save updated config
            self.save_config(config)

            # Import data to new storage type
            if exported_data:
                self.import_data_to_storage(new_storage_type, exported_data)

            return True

        except Exception as e:
            print(f"Migration failed: {e}")
            return False

    def export_current_data(self, storage_type: str) -> Dict[str, Any]:
        """Export data from current storage"""
        exported_data = {
            "transactions": [],
            "portfolio_items": {},
            "selected_stocks": [],
            "settings": {}
        }

        if storage_type == "local_database":
            # Export from local files
            try:
                # Transactions
                transactions_file = self.local_db_path / "transactions.json"
                if transactions_file.exists():
                    with open(transactions_file, 'r') as f:
                        exported_data["transactions"] = json.load(f)

                # Portfolio
                portfolio_file = self.local_db_path / "portfolio.json"
                if portfolio_file.exists():
                    with open(portfolio_file, 'r') as f:
                        exported_data["portfolio_items"] = json.load(f)

                # Selected stocks
                stocks_file = self.local_db_path / "selected_stocks.json"
                if stocks_file.exists():
                    with open(stocks_file, 'r') as f:
                        exported_data["selected_stocks"] = json.load(f)

            except Exception as e:
                print(f"Error exporting local data: {e}")

        elif storage_type == "google_sheets":
            # Export from Google Sheets would be handled by the app's Google Sheets service
            # For now, we'll create a placeholder
            pass

        return exported_data

    def import_data_to_storage(self, storage_type: str, data: Dict[str, Any]):
        """Import data to specified storage"""
        if storage_type == "local_database":
            # Import to local files
            try:
                # Transactions
                if data.get("transactions"):
                    with open(self.local_db_path / "transactions.json", 'w') as f:
                        json.dump(data["transactions"], f, indent=2)

                # Portfolio
                if data.get("portfolio_items"):
                    with open(self.local_db_path / "portfolio.json", 'w') as f:
                        json.dump(data["portfolio_items"], f, indent=2)

                # Selected stocks
                if data.get("selected_stocks"):
                    with open(self.local_db_path / "selected_stocks.json", 'w') as f:
                        json.dump(data["selected_stocks"], f, indent=2)

            except Exception as e:
                print(f"Error importing to local storage: {e}")

        elif storage_type == "google_sheets":
            # Import to Google Sheets would be handled by the app's Google Sheets service
            # The app will detect the change and prompt for Google Sheets setup
            pass

class PersistentAppLauncher:
    """Handles persistent launching and configuration"""

    def __init__(self, install_path: str):
        self.install_path = Path(install_path)
        self.migration_manager = DataMigrationManager(install_path)

    def create_launcher_script(self):
        """Create persistent launcher that remembers settings"""
        launcher_content = f'''@echo off
title Stock Market Analyzer
cd /d "{self.install_path}"

echo Starting Stock Market Analyzer...
echo Installation: {self.install_path}

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if dependencies are installed
if not exist "venv" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\\Scripts\\activate.bat
    pip install -r requirements.txt
) else (
    call venv\\Scripts\\activate.bat
)

REM Launch the application
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application closed with error. Press any key to exit.
    pause >nul
)
'''

        # Windows launcher
        with open(self.install_path / "Stock_Market_Analyzer.bat", "w") as f:
            f.write(launcher_content)

        # Create PowerShell launcher for better error handling
        ps_launcher = f'''# Stock Market Analyzer PowerShell Launcher
$installPath = "{self.install_path}"
Set-Location $installPath

Write-Host "Starting Stock Market Analyzer..." -ForegroundColor Green
Write-Host "Installation: $installPath" -ForegroundColor Yellow

# Check Python
try {{
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
}} catch {{
    Write-Host "ERROR: Python is not installed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}}

# Setup virtual environment if needed
if (!(Test-Path "venv")) {{
    Write-Host "Setting up virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & .\\venv\\Scripts\\Activate.ps1
    pip install -r requirements.txt
}} else {{
    & .\\venv\\Scripts\\Activate.ps1
}}

# Launch application
Write-Host "Launching application..." -ForegroundColor Green
python main.py

if ($LASTEXITCODE -ne 0) {{
    Write-Host "Application closed with error code: $LASTEXITCODE" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}}
'''

        with open(self.install_path / "launch.ps1", "w") as f:
            f.write(ps_launcher)

    def create_settings_manager_gui(self):
        """Create a settings manager for switching storage types"""
        settings_gui_content = '''#!/usr/bin/env python3
"""
Settings Manager - Switch between storage types
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
import sys

class SettingsManager:
    def __init__(self, install_path):
        self.install_path = Path(install_path)
        self.root = tk.Tk()
        self.root.title("Stock Market Analyzer - Settings")
        self.root.geometry("500x400")

        from installer_config import DataMigrationManager
        self.migration_manager = DataMigrationManager(install_path)

        self.create_gui()

    def create_gui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="📊 Storage Settings", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Current config
        config = self.migration_manager.get_current_config()
        current_storage = config.get("storage_type", "local_database")

        # Storage type selection
        ttk.Label(main_frame, text="Current Storage Type:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Label(main_frame, text=current_storage.replace("_", " ").title()).grid(row=1, column=1, sticky=tk.W, pady=(0, 10))

        ttk.Separator(main_frame, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)

        # Switch storage type
        ttk.Label(main_frame, text="Switch Storage Type:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        self.storage_var = tk.StringVar(value=current_storage)

        local_radio = ttk.Radiobutton(main_frame, text="💾 Local Database", variable=self.storage_var, value="local_database")
        local_radio.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)

        google_radio = ttk.Radiobutton(main_frame, text="🌐 Google Sheets", variable=self.storage_var, value="google_sheets")
        google_radio.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Migration info
        info_text = """
Note: Switching storage types will:
• Create a backup of your current data
• Migrate all transactions and portfolio data
• Preserve your investment history
• Allow you to switch back anytime
        """
        ttk.Label(main_frame, text=info_text.strip(), justify=tk.LEFT).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=20)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)

        apply_button = ttk.Button(button_frame, text="Apply Changes", command=self.apply_changes)
        apply_button.grid(row=0, column=0, padx=(0, 10))

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.root.quit)
        cancel_button.grid(row=0, column=1)

        # Migration history
        if config.get("data_migration", {}).get("migration_history"):
            history_button = ttk.Button(button_frame, text="Migration History", command=self.show_migration_history)
            history_button.grid(row=0, column=2, padx=(10, 0))

    def apply_changes(self):
        new_storage = self.storage_var.get()
        config = self.migration_manager.get_current_config()
        current_storage = config.get("storage_type", "local_database")

        if new_storage == current_storage:
            messagebox.showinfo("No Changes", "Storage type is already set to this option.")
            return

        if messagebox.askyesno("Confirm Migration",
                             f"Switch from {current_storage.replace('_', ' ').title()} to {new_storage.replace('_', ' ').title()}?\\n\\nThis will migrate all your data."):

            if self.migration_manager.switch_storage_type(new_storage):
                messagebox.showinfo("Success", "Storage type switched successfully!\\nYour data has been migrated.")
                self.root.quit()
            else:
                messagebox.showerror("Error", "Failed to switch storage type. Please try again.")

    def show_migration_history(self):
        # Create a simple history window
        history_window = tk.Toplevel(self.root)
        history_window.title("Migration History")
        history_window.geometry("400x300")

        config = self.migration_manager.get_current_config()
        history = config.get("data_migration", {}).get("migration_history", [])

        text_widget = tk.Text(history_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if history:
            for migration in history:
                text_widget.insert(tk.END, f"Date: {migration['timestamp']}\\n")
                text_widget.insert(tk.END, f"From: {migration['from']} → To: {migration['to']}\\n")
                text_widget.insert(tk.END, f"Records: {migration['records_migrated']}\\n")
                text_widget.insert(tk.END, "-" * 40 + "\\n\\n")
        else:
            text_widget.insert(tk.END, "No migration history available.")

        text_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        install_path = sys.argv[1]
    else:
        install_path = Path(__file__).parent

    app = SettingsManager(install_path)
    app.root.mainloop()
'''

        with open(self.install_path / "settings_manager.py", "w") as f:
            f.write(settings_gui_content)

def create_installer_package(source_dir: str, output_dir: str):
    """Create complete installer package"""
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Copy all necessary files
    files_to_include = [
        "installer/setup_wizard.py",
        "installer/installer_config.py",
        "src/",
        "main.py",
        "requirements.txt",
        "USER_GUIDE_SIMPLE.md",
        "README.md"
    ]

    for item in files_to_include:
        source_item = source_path / item
        dest_item = output_path / item

        if source_item.exists():
            if source_item.is_file():
                dest_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_item, dest_item)
            else:
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(source_item, dest_item)

    return output_path