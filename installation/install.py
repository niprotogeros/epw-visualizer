
#!/usr/bin/env python3
"""
Cross-platform Python installer for EPW Visualizer
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import venv
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.WHITE):
    """Print colored message (colors work on Unix, plain text on Windows)"""
    if platform.system() == "Windows":
        print(message)
    else:
        print(f"{color}{message}{Colors.ENDC}")

def print_header(title):
    """Print a formatted header"""
    print_colored("=" * 50, Colors.CYAN)
    print_colored(title, Colors.BOLD + Colors.CYAN)
    print_colored("=" * 50, Colors.CYAN)
    print()

def print_error(message):
    """Print error message"""
    print_colored(f"ERROR: {message}", Colors.RED)

def print_success(message):
    """Print success message"""
    print_colored(message, Colors.GREEN)

def print_warning(message):
    """Print warning message"""
    print_colored(f"WARNING: {message}", Colors.YELLOW)

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def run_command(command, shell=False):
    """Run a command and return success status"""
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=True, 
                                  capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_warning("Virtual environment already exists, removing...")
        import shutil
        shutil.rmtree(venv_path)
    
    print("Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print_success("Virtual environment created successfully")
        return True
    except Exception as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the appropriate pip command for the current platform"""
    if platform.system() == "Windows":
        return str(Path("venv") / "Scripts" / "python.exe")
    else:
        return str(Path("venv") / "bin" / "python")

def install_dependencies():
    """Install required dependencies"""
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    print("Upgrading pip...")
    success, output = run_command([pip_cmd, "-m", "pip", "install", "--upgrade", "pip"])
    if not success:
        print_warning("Failed to upgrade pip, continuing anyway...")
    
    # Install dependencies
    print("Installing dependencies...")
    requirements_file = Path("requirements.txt")
    
    if requirements_file.exists():
        print("Installing from requirements.txt...")
        success, output = run_command([pip_cmd, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("Installing default dependencies...")
        packages = [
            "streamlit>=1.28.0",
            "pandas>=1.5.0", 
            "plotly>=5.15.0",
            "numpy>=1.24.0"
        ]
        success, output = run_command([pip_cmd, "-m", "pip", "install"] + packages)
    
    if success:
        print_success("Dependencies installed successfully")
        return True
    else:
        print_error(f"Failed to install dependencies: {output}")
        return False

def create_launcher_scripts():
    """Create platform-specific launcher scripts"""
    system = platform.system()
    
    if system == "Windows":
        launcher_content = """@echo off
call venv\\Scripts\\activate.bat
streamlit run epw_visualizer.py
pause
"""
        with open("run.bat", "w") as f:
            f.write(launcher_content)
        print_success("Created run.bat launcher")
    
    else:  # Unix-like systems
        launcher_content = """#!/bin/bash
source venv/bin/activate
streamlit run epw_visualizer.py
"""
        with open("run.sh", "w") as f:
            f.write(launcher_content)
        
        # Make executable
        os.chmod("run.sh", 0o755)
        print_success("Created run.sh launcher")

def main():
    """Main installation function"""
    print_header("EPW Visualizer - Cross-Platform Installation")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print(f"Platform: {platform.system()} {platform.release()}")
    print()
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create launcher scripts
    create_launcher_scripts()
    
    print()
    print_header("Installation Complete!")
    
    print("To run EPW Visualizer:")
    if platform.system() == "Windows":
        print("  • Double-click run.bat")
        print("  • Or run: venv\\Scripts\\activate.bat && streamlit run epw_visualizer.py")
    else:
        print("  • Run: ./run.sh")
        print("  • Or run: source venv/bin/activate && streamlit run epw_visualizer.py")
    
    print()
    print("Verify installation: python installation/check_installation.py")
    print("Troubleshooting: python installation/troubleshoot.py")
    print()

if __name__ == "__main__":
    main()
