
#!/usr/bin/env python3
"""
Installation verification script for EPW Visualizer
Checks all dependencies and system requirements
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
import importlib.util

class Colors:
    """ANSI color codes"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
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

def print_header(title):
    """Print formatted header"""
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f" {title}", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)

def check_mark():
    return "✓" if platform.system() != "Windows" else "[OK]"

def cross_mark():
    return "✗" if platform.system() != "Windows" else "[FAIL]"

def check_python_version():
    """Check Python version"""
    print_colored("\n1. Python Version Check", Colors.BOLD)
    print("-" * 30)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Current Python version: {version_str}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    
    if version.major >= 3 and version.minor >= 8:
        print_colored(f"{check_mark()} Python version is compatible", Colors.GREEN)
        return True
    else:
        print_colored(f"{cross_mark()} Python 3.8+ required, found {version_str}", Colors.RED)
        return False

def check_virtual_environment():
    """Check virtual environment"""
    print_colored("\n2. Virtual Environment Check", Colors.BOLD)
    print("-" * 35)
    
    venv_path = Path("venv")
    if not venv_path.exists():
        print_colored(f"{cross_mark()} Virtual environment not found", Colors.RED)
        print("Run installation script to create virtual environment")
        return False
    
    print_colored(f"{check_mark()} Virtual environment exists", Colors.GREEN)
    
    # Check if it's a valid virtual environment
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    if python_exe.exists():
        print_colored(f"{check_mark()} Python executable found in venv", Colors.GREEN)
    else:
        print_colored(f"{cross_mark()} Python executable not found in venv", Colors.RED)
        return False
    
    if pip_exe.exists():
        print_colored(f"{check_mark()} Pip executable found in venv", Colors.GREEN)
    else:
        print_colored(f"{cross_mark()} Pip executable not found in venv", Colors.RED)
        return False
    
    return True

def check_dependencies():
    """Check required dependencies"""
    print_colored("\n3. Dependencies Check", Colors.BOLD)
    print("-" * 25)
    
    # Get Python executable from venv
    if platform.system() == "Windows":
        python_exe = str(Path("venv") / "Scripts" / "python.exe")
    else:
        python_exe = str(Path("venv") / "bin" / "python")
    
    if not Path(python_exe).exists():
        print_colored(f"{cross_mark()} Virtual environment Python not found", Colors.RED)
        return False
    
    required_packages = {
        'streamlit': '1.28.0',
        'pandas': '1.5.0',
        'plotly': '5.15.0',
        'numpy': '1.24.0'
    }
    
    all_good = True
    
    for package, min_version in required_packages.items():
        try:
            # Check if package is installed
            result = subprocess.run([python_exe, "-c", f"import {package}; print({package}.__version__)"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                installed_version = result.stdout.strip()
                print_colored(f"{check_mark()} {package}: {installed_version}", Colors.GREEN)
            else:
                print_colored(f"{cross_mark()} {package}: Not installed", Colors.RED)
                all_good = False
                
        except subprocess.TimeoutExpired:
            print_colored(f"{cross_mark()} {package}: Check timed out", Colors.YELLOW)
            all_good = False
        except Exception as e:
            print_colored(f"{cross_mark()} {package}: Error checking - {str(e)}", Colors.RED)
            all_good = False
    
    return all_good

def check_main_script():
    """Check if main script exists"""
    print_colored("\n4. Main Script Check", Colors.BOLD)
    print("-" * 25)
    
    main_script = Path("epw_visualizer.py")
    if main_script.exists():
        print_colored(f"{check_mark()} epw_visualizer.py found", Colors.GREEN)
        
        # Check if it's a valid Python file
        try:
            with open(main_script, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'streamlit' in content and 'def' in content:
                    print_colored(f"{check_mark()} Main script appears valid", Colors.GREEN)
                    return True
                else:
                    print_colored(f"{cross_mark()} Main script may be incomplete", Colors.YELLOW)
                    return False
        except Exception as e:
            print_colored(f"{cross_mark()} Error reading main script: {str(e)}", Colors.RED)
            return False
    else:
        print_colored(f"{cross_mark()} epw_visualizer.py not found", Colors.RED)
        return False

def check_launcher_scripts():
    """Check launcher scripts"""
    print_colored("\n5. Launcher Scripts Check", Colors.BOLD)
    print("-" * 30)
    
    if platform.system() == "Windows":
        launcher = Path("run.bat")
        if launcher.exists():
            print_colored(f"{check_mark()} run.bat found", Colors.GREEN)
        else:
            print_colored(f"{cross_mark()} run.bat not found", Colors.YELLOW)
            print("You can create it by running the installation script")
    else:
        launcher = Path("run.sh")
        if launcher.exists():
            print_colored(f"{check_mark()} run.sh found", Colors.GREEN)
            # Check if executable
            if os.access(launcher, os.X_OK):
                print_colored(f"{check_mark()} run.sh is executable", Colors.GREEN)
            else:
                print_colored(f"{cross_mark()} run.sh is not executable", Colors.YELLOW)
                print("Run: chmod +x run.sh")
        else:
            print_colored(f"{cross_mark()} run.sh not found", Colors.YELLOW)
            print("You can create it by running the installation script")

def test_streamlit_import():
    """Test if Streamlit can be imported and run"""
    print_colored("\n6. Streamlit Test", Colors.BOLD)
    print("-" * 20)
    
    if platform.system() == "Windows":
        python_exe = str(Path("venv") / "Scripts" / "python.exe")
    else:
        python_exe = str(Path("venv") / "bin" / "python")
    
    try:
        # Test basic Streamlit import
        result = subprocess.run([python_exe, "-c", "import streamlit; print('Streamlit import successful')"], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print_colored(f"{check_mark()} Streamlit imports successfully", Colors.GREEN)
            
            # Test if streamlit command works
            streamlit_cmd = str(Path("venv") / ("Scripts" if platform.system() == "Windows" else "bin") / "streamlit")
            result = subprocess.run([streamlit_cmd, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print_colored(f"{check_mark()} Streamlit command works: {version}", Colors.GREEN)
                return True
            else:
                print_colored(f"{cross_mark()} Streamlit command failed", Colors.YELLOW)
                return False
                
        else:
            print_colored(f"{cross_mark()} Streamlit import failed: {result.stderr}", Colors.RED)
            return False
            
    except subprocess.TimeoutExpired:
        print_colored(f"{cross_mark()} Streamlit test timed out", Colors.YELLOW)
        return False
    except Exception as e:
        print_colored(f"{cross_mark()} Streamlit test error: {str(e)}", Colors.RED)
        return False

def main():
    """Main verification function"""
    print_header("EPW Visualizer Installation Verification")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Main Script", check_main_script),
        ("Launcher Scripts", check_launcher_scripts),
        ("Streamlit Test", test_streamlit_import)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_colored(f"Error in {name} check: {str(e)}", Colors.RED)
            results.append((name, False))
    
    # Summary
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored(" VERIFICATION SUMMARY", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = check_mark() if result else cross_mark()
        color = Colors.GREEN if result else Colors.RED
        print_colored(f"{status} {name}", color)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print_colored(f"\n{check_mark()} All checks passed! EPW Visualizer is ready to use.", Colors.GREEN)
        print("\nTo run the application:")
        if platform.system() == "Windows":
            print("  • Double-click run.bat")
            print("  • Or run: venv\\Scripts\\activate.bat && streamlit run epw_visualizer.py")
        else:
            print("  • Run: ./run.sh")
            print("  • Or run: source venv/bin/activate && streamlit run epw_visualizer.py")
    else:
        print_colored(f"\n{cross_mark()} Some checks failed. Please run the installation script.", Colors.RED)
        print("\nTroubleshooting:")
        print("  • Run: python installation/troubleshoot.py")
        print("  • Or reinstall: python installation/install.py")

if __name__ == "__main__":
    main()
