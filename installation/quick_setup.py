
#!/usr/bin/env python3
"""
Interactive GUI setup for EPW Visualizer
Provides a user-friendly installation experience
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import sys
import os
import platform
from pathlib import Path

class EPWVisualizerInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("EPW Visualizer - Quick Setup")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.installation_complete = False
        
        self.setup_ui()
        self.check_initial_requirements()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="EPW Visualizer Quick Setup", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status labels
        ttk.Label(status_frame, text="Python Version:").grid(row=0, column=0, sticky=tk.W)
        self.python_status = ttk.Label(status_frame, text="Checking...")
        self.python_status.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Virtual Environment:").grid(row=1, column=0, sticky=tk.W)
        self.venv_status = ttk.Label(status_frame, text="Not created")
        self.venv_status.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Dependencies:").grid(row=2, column=0, sticky=tk.W)
        self.deps_status = ttk.Label(status_frame, text="Not installed")
        self.deps_status.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Installation Log", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        self.install_button = ttk.Button(button_frame, text="Start Installation", 
                                        command=self.start_installation)
        self.install_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.launch_button = ttk.Button(button_frame, text="Launch EPW Visualizer", 
                                       command=self.launch_app, state=tk.DISABLED)
        self.launch_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.close_button = ttk.Button(button_frame, text="Close", 
                                      command=self.root.quit)
        self.close_button.pack(side=tk.RIGHT)
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_initial_requirements(self):
        """Check initial system requirements"""
        # Check Python version
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.python_status.config(text=f"✓ {version.major}.{version.minor}.{version.micro}", 
                                     foreground="green")
            self.log(f"Python {version.major}.{version.minor}.{version.micro} detected")
        else:
            self.python_status.config(text=f"✗ {version.major}.{version.minor}.{version.micro} (Need 3.8+)", 
                                     foreground="red")
            self.log(f"ERROR: Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
            self.install_button.config(state=tk.DISABLED)
        
        # Check if virtual environment exists
        if Path("venv").exists():
            self.venv_status.config(text="✓ Exists", foreground="green")
            self.log("Virtual environment found")
        
        # Check if dependencies are installed
        if Path("venv").exists():
            try:
                if platform.system() == "Windows":
                    pip_cmd = str(Path("venv") / "Scripts" / "python.exe")
                else:
                    pip_cmd = str(Path("venv") / "bin" / "python")
                
                result = subprocess.run([pip_cmd, "-c", "import streamlit, pandas, plotly, numpy"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.deps_status.config(text="✓ Installed", foreground="green")
                    self.log("Dependencies are installed")
                    self.installation_complete = True
                    self.install_button.config(text="Reinstall")
                    self.launch_button.config(state=tk.NORMAL)
            except:
                pass
    
    def start_installation(self):
        """Start the installation process"""
        self.install_button.config(state=tk.DISABLED)
        self.progress.start()
        
        # Run installation in separate thread
        thread = threading.Thread(target=self.run_installation)
        thread.daemon = True
        thread.start()
    
    def run_installation(self):
        """Run the actual installation"""
        try:
            self.log("Starting installation...")
            
            # Create virtual environment
            self.log("Creating virtual environment...")
            if Path("venv").exists():
                self.log("Removing existing virtual environment...")
                import shutil
                shutil.rmtree("venv")
            
            import venv
            venv.create("venv", with_pip=True)
            self.venv_status.config(text="✓ Created", foreground="green")
            self.log("Virtual environment created successfully")
            
            # Get pip command
            if platform.system() == "Windows":
                pip_cmd = str(Path("venv") / "Scripts" / "python.exe")
            else:
                pip_cmd = str(Path("venv") / "bin" / "python")
            
            # Upgrade pip
            self.log("Upgrading pip...")
            subprocess.run([pip_cmd, "-m", "pip", "install", "--upgrade", "pip"], 
                          check=True, capture_output=True)
            
            # Install dependencies
            self.log("Installing dependencies...")
            if Path("requirements.txt").exists():
                subprocess.run([pip_cmd, "-m", "pip", "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True)
            else:
                packages = ["streamlit>=1.28.0", "pandas>=1.5.0", "plotly>=5.15.0", "numpy>=1.24.0"]
                subprocess.run([pip_cmd, "-m", "pip", "install"] + packages, 
                              check=True, capture_output=True)
            
            self.deps_status.config(text="✓ Installed", foreground="green")
            self.log("Dependencies installed successfully")
            
            # Create launcher scripts
            self.create_launchers()
            
            self.log("Installation completed successfully!")
            self.installation_complete = True
            
            # Update UI
            self.root.after(0, self.installation_finished)
            
        except Exception as e:
            self.log(f"ERROR: Installation failed - {str(e)}")
            self.root.after(0, self.installation_failed)
    
    def create_launchers(self):
        """Create launcher scripts"""
        if platform.system() == "Windows":
            launcher_content = """@echo off
call venv\\Scripts\\activate.bat
streamlit run epw_visualizer.py
pause
"""
            with open("run.bat", "w") as f:
                f.write(launcher_content)
            self.log("Created run.bat launcher")
        else:
            launcher_content = """#!/bin/bash
source venv/bin/activate
streamlit run epw_visualizer.py
"""
            with open("run.sh", "w") as f:
                f.write(launcher_content)
            os.chmod("run.sh", 0o755)
            self.log("Created run.sh launcher")
    
    def installation_finished(self):
        """Called when installation is complete"""
        self.progress.stop()
        self.install_button.config(state=tk.NORMAL, text="Reinstall")
        self.launch_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success", "Installation completed successfully!\n\nYou can now launch EPW Visualizer.")
    
    def installation_failed(self):
        """Called when installation fails"""
        self.progress.stop()
        self.install_button.config(state=tk.NORMAL)
        messagebox.showerror("Error", "Installation failed. Please check the log for details.")
    
    def launch_app(self):
        """Launch the EPW Visualizer application"""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["run.bat"], shell=True)
            else:
                subprocess.Popen(["./run.sh"])
            
            messagebox.showinfo("Launched", "EPW Visualizer is starting...\nCheck your web browser for the application.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch application: {str(e)}")

def main():
    """Main function"""
    root = tk.Tk()
    app = EPWVisualizerInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
