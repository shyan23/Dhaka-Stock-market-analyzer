#!/usr/bin/env python3
"""
Stock Market Analyzer - Setup Wizard
Creates a user-friendly installer with GUI for choosing storage options
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import threading
import time

class SetupWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Market Analyzer - Setup Wizard")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Center the window
        self.center_window()

        # Setup variables
        self.storage_choice = tk.StringVar(value="google_sheets")
        self.install_path = tk.StringVar(value=str(Path.home() / "StockMarketAnalyzer"))
        self.current_step = 0
        self.total_steps = 4

        # Create GUI
        self.create_widgets()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")

    def create_widgets(self):
        """Create the main GUI elements"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Header
        header_label = ttk.Label(
            main_frame,
            text="📈 Stock Market Analyzer Setup",
            font=("Arial", 16, "bold")
        )
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Content frame (will change based on step)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.back_button = ttk.Button(button_frame, text="← Back", command=self.go_back)
        self.back_button.grid(row=0, column=0, padx=(0, 10))

        self.next_button = ttk.Button(button_frame, text="Next →", command=self.go_next)
        self.next_button.grid(row=0, column=1)

        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_setup)
        self.cancel_button.grid(row=0, column=2, padx=(10, 0))

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # Start with welcome step
        self.show_step()

    def show_step(self):
        """Show the current step"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Update progress
        self.progress['value'] = (self.current_step / self.total_steps) * 100

        # Update buttons
        self.back_button['state'] = 'normal' if self.current_step > 0 else 'disabled'

        if self.current_step == 0:
            self.show_welcome()
        elif self.current_step == 1:
            self.show_storage_choice()
        elif self.current_step == 2:
            self.show_installation_path()
        elif self.current_step == 3:
            self.show_installation()
        elif self.current_step == 4:
            self.show_completion()

    def show_welcome(self):
        """Welcome step"""
        welcome_text = """
Welcome to Stock Market Analyzer Setup!

This wizard will help you install and configure the Stock Market Analyzer
application for tracking your investments in the Dhaka Stock Exchange (DSE).

Features:
• 📊 Real-time stock price tracking
• 💹 Portfolio management with profit/loss analysis
• 📈 Interactive charts and technical indicators
• 📋 Transaction recording and history
• 📄 Professional PDF and Excel reports
• 🔄 Automatic data backup (Google Sheets) or local storage

Click 'Next' to continue with the setup.
        """

        label = ttk.Label(self.content_frame, text=welcome_text.strip(), justify=tk.LEFT)
        label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.next_button['text'] = "Next →"

    def show_storage_choice(self):
        """Storage choice step"""
        title_label = ttk.Label(
            self.content_frame,
            text="Choose Your Data Storage Method",
            font=("Arial", 12, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        # Google Sheets option
        google_frame = ttk.LabelFrame(self.content_frame, text="🌐 Google Sheets (Recommended)", padding="10")
        google_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Radiobutton(
            google_frame,
            text="Use Google Sheets for data storage",
            variable=self.storage_choice,
            value="google_sheets"
        ).grid(row=0, column=0, sticky=tk.W)

        google_benefits = """
✅ Access your data from anywhere
✅ Automatic cloud backup
✅ Share data across devices
✅ Never lose your investment data
✅ Easy data export and analysis
        """
        ttk.Label(google_frame, text=google_benefits.strip(), justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))

        # Local database option
        local_frame = ttk.LabelFrame(self.content_frame, text="💾 Local Database", padding="10")
        local_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Radiobutton(
            local_frame,
            text="Use local database for data storage",
            variable=self.storage_choice,
            value="local_database"
        ).grid(row=0, column=0, sticky=tk.W)

        local_benefits = """
✅ Faster performance
✅ Works without internet
✅ Complete data privacy
✅ No external dependencies
⚠️  Manual backup required
        """
        ttk.Label(local_frame, text=local_benefits.strip(), justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))

        self.content_frame.columnconfigure(0, weight=1)

    def show_installation_path(self):
        """Installation path step"""
        title_label = ttk.Label(
            self.content_frame,
            text="Choose Installation Location",
            font=("Arial", 12, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 20))

        ttk.Label(self.content_frame, text="Install to:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        path_entry = ttk.Entry(self.content_frame, textvariable=self.install_path, width=50)
        path_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        browse_button = ttk.Button(self.content_frame, text="Browse...", command=self.browse_install_path)
        browse_button.grid(row=2, column=2, padx=(10, 0), pady=(0, 10))

        # Show disk space requirements
        requirements_text = """
Installation Requirements:
• Disk Space: ~200 MB
• Python 3.8+ (will be installed if missing)
• Internet connection (for stock data)
• Windows 10+ / macOS 10.14+ / Ubuntu 18.04+
        """

        ttk.Label(self.content_frame, text=requirements_text.strip(), justify=tk.LEFT).grid(
            row=3, column=0, columnspan=3, sticky=tk.W, pady=(20, 0)
        )

        self.content_frame.columnconfigure(0, weight=1)

    def show_installation(self):
        """Installation step"""
        title_label = ttk.Label(
            self.content_frame,
            text="Installing Stock Market Analyzer...",
            font=("Arial", 12, "bold")
        )
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        # Installation progress
        self.install_progress = ttk.Progressbar(self.content_frame, length=400, mode='indeterminate')
        self.install_progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.install_status = ttk.Label(self.content_frame, text="Preparing installation...")
        self.install_status.grid(row=2, column=0, sticky=tk.W, pady=(0, 20))

        # Log text widget
        log_frame = ttk.LabelFrame(self.content_frame, text="Installation Log", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.log_text = tk.Text(log_frame, height=15, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Disable buttons during installation
        self.back_button['state'] = 'disabled'
        self.next_button['state'] = 'disabled'
        self.next_button['text'] = "Installing..."

        # Start installation in separate thread
        threading.Thread(target=self.perform_installation, daemon=True).start()

        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(3, weight=1)

    def show_completion(self):
        """Completion step"""
        title_label = ttk.Label(
            self.content_frame,
            text="🎉 Installation Complete!",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        storage_type = "Google Sheets" if self.storage_choice.get() == "google_sheets" else "Local Database"

        completion_text = f"""
Stock Market Analyzer has been successfully installed!

Configuration:
• Storage Method: {storage_type}
• Installation Path: {self.install_path.get()}
• Desktop Shortcut: Created
• Start Menu Entry: Created

What's Next:
1. Click 'Launch Application' to start using the app
2. Follow the first-time setup wizard in the app
3. Start tracking your DSE investments!

User Guide: A comprehensive guide has been installed at:
{self.install_path.get()}/USER_GUIDE_SIMPLE.md
        """

        ttk.Label(self.content_frame, text=completion_text.strip(), justify=tk.LEFT).grid(
            row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 20)
        )

        # Action buttons
        button_frame = ttk.Frame(self.content_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        launch_button = ttk.Button(
            button_frame,
            text="🚀 Launch Application",
            command=self.launch_application
        )
        launch_button.grid(row=0, column=0, padx=(0, 10))

        open_folder_button = ttk.Button(
            button_frame,
            text="📁 Open Install Folder",
            command=self.open_install_folder
        )
        open_folder_button.grid(row=0, column=1, padx=(0, 10))

        # Update main buttons
        self.back_button['state'] = 'disabled'
        self.next_button['text'] = "Finish"
        self.next_button['state'] = 'normal'

        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(1, weight=1)

    def browse_install_path(self):
        """Browse for installation path"""
        folder = filedialog.askdirectory(
            title="Choose Installation Folder",
            initialdir=str(Path.home())
        )
        if folder:
            self.install_path.set(folder)

    def perform_installation(self):
        """Perform the actual installation"""
        try:
            self.install_progress.start()

            # Create installation directory
            install_dir = Path(self.install_path.get())
            self.log_message(f"Creating installation directory: {install_dir}")
            install_dir.mkdir(parents=True, exist_ok=True)

            # Copy application files
            self.log_message("Copying application files...")
            source_dir = Path(__file__).parent.parent

            # List of files/folders to copy
            items_to_copy = [
                "src", "main.py", "requirements.txt",
                "USER_GUIDE_SIMPLE.md", "README.md"
            ]

            for item in items_to_copy:
                source_path = source_dir / item
                dest_path = install_dir / item

                if source_path.exists():
                    if source_path.is_file():
                        self.log_message(f"Copying {item}...")
                        shutil.copy2(source_path, dest_path)
                    else:
                        self.log_message(f"Copying directory {item}...")
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)

            # Install Python dependencies
            self.log_message("Installing Python dependencies...")
            self.install_status.config(text="Installing dependencies...")

            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r",
                str(install_dir / "requirements.txt")
            ], check=True, capture_output=True, text=True)

            # Create configuration file
            self.log_message("Creating configuration...")
            config = {
                "storage_type": self.storage_choice.get(),
                "first_run": True,
                "installation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0.0"
            }

            with open(install_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)

            # Create launcher script
            self.log_message("Creating launcher...")
            launcher_content = f'''@echo off
cd /d "{install_dir}"
python main.py
pause
'''

            with open(install_dir / "launch.bat", "w") as f:
                f.write(launcher_content)

            # Create desktop shortcut (Windows)
            if sys.platform == "win32":
                self.create_desktop_shortcut(install_dir)

            self.log_message("Installation completed successfully!")
            self.install_status.config(text="Installation complete!")

            # Update progress and enable next button
            self.install_progress.stop()
            self.install_progress['mode'] = 'determinate'
            self.install_progress['value'] = 100

            self.next_button['state'] = 'normal'
            self.next_button['text'] = "Next →"

        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            self.install_status.config(text="Installation failed!")
            self.install_progress.stop()
            messagebox.showerror("Installation Error", f"Installation failed: {str(e)}")

    def create_desktop_shortcut(self, install_dir):
        """Create desktop shortcut (Windows only)"""
        try:
            import winshell
            from win32com.client import Dispatch

            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Stock Market Analyzer.lnk")

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(install_dir / "launch.bat")
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.IconLocation = str(install_dir / "launch.bat")
            shortcut.save()

            self.log_message("Desktop shortcut created")
        except ImportError:
            self.log_message("Skipping desktop shortcut (winshell not available)")
        except Exception as e:
            self.log_message(f"Could not create desktop shortcut: {e}")

    def log_message(self, message):
        """Add message to installation log"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, full_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def launch_application(self):
        """Launch the installed application"""
        try:
            install_dir = Path(self.install_path.get())
            if sys.platform == "win32":
                subprocess.Popen([str(install_dir / "launch.bat")], shell=True)
            else:
                subprocess.Popen([sys.executable, str(install_dir / "main.py")],
                               cwd=str(install_dir))

            self.root.quit()
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch application: {e}")

    def open_install_folder(self):
        """Open the installation folder"""
        install_dir = Path(self.install_path.get())
        if sys.platform == "win32":
            os.startfile(install_dir)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(install_dir)])
        else:
            subprocess.run(["xdg-open", str(install_dir)])

    def go_next(self):
        """Go to next step"""
        if self.current_step < self.total_steps:
            self.current_step += 1
            self.show_step()
        else:
            self.root.quit()

    def go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()

    def cancel_setup(self):
        """Cancel the setup"""
        if messagebox.askyesno("Cancel Setup", "Are you sure you want to cancel the installation?"):
            self.root.quit()

    def run(self):
        """Run the setup wizard"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SetupWizard()
    app.run()