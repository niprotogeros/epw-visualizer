
#!/usr/bin/env python3
"""
Cross-platform launcher for EPW Visualizer
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.WHITE):
    """Print colored message"""
    if platform.system() == "Windows":
        print(message)
    else:
        print(f"{color}{message}{Colors.ENDC}")

def print_header():
    """Print application header"""
    print_colored("=" * 50, Colors.CYAN)
    print_colored("EPW Visualizer Launcher", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 50, Colors.CYAN)
    print()

def check_virtual_environment():
    """Check if virtual environment exists and is valid"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print_colored("ERROR: Virtual environment not found", Colors.RED)
        print("Please run the installation script first:")
        print("  Windows: install.bat")
        print("  macOS/Linux: ./install.sh")
        print("  Cross-platform: python installation/install.py")
        return False
    
    # Check for Python executable
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        streamlit_exe = venv_path / "Scripts" / "streamlit.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        streamlit_exe = venv_path / "bin" / "streamlit"
    
    if not python_exe.exists():
        print_colored("ERROR: Virtual environment Python not found", Colors.RED)
        print("Virtual environment may be corrupted. Please reinstall.")
        return False
    
    return True, str(python_exe), str(streamlit_exe)

def check_main_script():
    """Check if main application script exists"""
    main_script = Path("epw_visualizer.py")
    
    if not main_script.exists():
        print_colored("ERROR: epw_visualizer.py not found", Colors.RED)
        print("Please ensure you're in the correct directory")
        print("The main script should be in the same folder as this launcher")
        return False
    
    return True

def launch_application(python_exe, streamlit_exe):
    """Launch the EPW Visualizer application"""
    print_colored("Starting EPW Visualizer...", Colors.GREEN)
    print()
    print("The application will open in your web browser.")
    print("Press Ctrl+C to stop the application.")
    print()
    print_colored("-" * 50, Colors.CYAN)
    
    try:
        # Try using streamlit executable first
        if Path(streamlit_exe).exists():
            subprocess.run([streamlit_exe, "run", "epw_visualizer.py"], check=True)
        else:
            # Fallback to python -m streamlit
            subprocess.run([python_exe, "-m", "streamlit", "run", "epw_visualizer.py"], check=True)
            
    except subprocess.CalledProcessError as e:
        print_colored(f"\nERROR: Failed to start application (exit code {e.returncode})", Colors.RED)
        print("This might be due to:")
        print("  • Missing dependencies")
        print("  • Corrupted virtual environment")
        print("  • Port already in use")
        print("\nTry running the troubleshooter: python installation/troubleshoot.py")
        return False
        
    except KeyboardInterrupt:
        print_colored("\nApplication stopped by user", Colors.YELLOW)
        return True
        
    except Exception as e:
        print_colored(f"\nERROR: Unexpected error - {str(e)}", Colors.RED)
        return False
    
    print_colored("\nApplication stopped.", Colors.YELLOW)
    return True

def show_help():
    """Show help information"""
    print_colored("EPW Visualizer Launcher Help", Colors.BOLD)
    print()
    print("Usage: python run.py [options]")
    print()
    print("Options:")
    print("  -h, --help     Show this help message")
    print("  --check        Check installation without launching")
    print("  --version      Show version information")
    print()
    print("Troubleshooting:")
    print("  • Installation check: python installation/check_installation.py")
    print("  • Troubleshooter: python installation/troubleshoot.py")
    print("  • Reinstall: python installation/install.py")

def check_installation_only():
    """Check installation without launching"""
    print_colored("Checking EPW Visualizer installation...", Colors.CYAN)
    print()
    
    # Check virtual environment
    result = check_virtual_environment()
    if not result:
        return False
    
    _, python_exe, _ = result
    
    # Check main script
    if not check_main_script():
        return False
    
    # Check dependencies
    print("Checking dependencies...")
    try:
        result = subprocess.run([python_exe, "-c", 
            "import streamlit, pandas, plotly, numpy; print('All dependencies available')"],
            capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print_colored("✓ All dependencies are installed", Colors.GREEN)
        else:
            print_colored("✗ Some dependencies are missing", Colors.RED)
            print("Run: python installation/check_installation.py for details")
            return False
            
    except subprocess.TimeoutExpired:
        print_colored("✗ Dependency check timed out", Colors.YELLOW)
        return False
    except Exception as e:
        print_colored(f"✗ Error checking dependencies: {str(e)}", Colors.RED)
        return False
    
    print_colored("\n✓ Installation appears to be working correctly!", Colors.GREEN)
    return True

def main():
    """Main launcher function"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['-h', '--help']:
            show_help()
            return
        elif arg == '--check':
            print_header()
            check_installation_only()
            return
        elif arg == '--version':
            print("EPW Visualizer Launcher v1.0")
            return
        else:
            print_colored(f"Unknown option: {sys.argv[1]}", Colors.RED)
            print("Use --help for usage information")
            return
    
    print_header()
    
    # Check virtual environment
    result = check_virtual_environment()
    if not result:
        sys.exit(1)
    
    _, python_exe, streamlit_exe = result
    
    # Check main script
    if not check_main_script():
        sys.exit(1)
    
    # Launch application
    success = launch_application(python_exe, streamlit_exe)
    
    if not success:
        print()
        print_colored("Launch failed. For help:", Colors.YELLOW)
        print("  • Check installation: python run.py --check")
        print("  • Run troubleshooter: python installation/troubleshoot.py")
        print("  • Get help: python run.py --help")
        sys.exit(1)

if __name__ == "__main__":
    main()
