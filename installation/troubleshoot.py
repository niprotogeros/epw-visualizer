
#!/usr/bin/env python3
"""
Automated troubleshooting script for EPW Visualizer
Diagnoses common issues and provides solutions
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.WHITE):
    if platform.system() == "Windows":
        print(message)
    else:
        print(f"{color}{message}{Colors.ENDC}")

def print_header(title):
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f" {title}", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)

def print_issue(title):
    print_colored(f"\n🔍 {title}", Colors.YELLOW)
    print("-" * (len(title) + 4))

def print_solution(solution):
    print_colored(f"💡 Solution: {solution}", Colors.GREEN)

def print_error(message):
    print_colored(f"❌ {message}", Colors.RED)

def print_success(message):
    print_colored(f"✅ {message}", Colors.GREEN)

def run_command(command, timeout=30):
    """Run command and return success, stdout, stderr"""
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=timeout)
        else:
            result = subprocess.run(command, capture_output=True, 
                                  text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def diagnose_python():
    """Diagnose Python installation issues"""
    print_issue("Python Installation")
    
    version = sys.version_info
    print(f"Current Python: {version.major}.{version.minor}.{version.micro}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Executable: {sys.executable}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        print_solution("Install Python 3.8+ from https://python.org")
        if platform.system() == "Darwin":
            print("  macOS: brew install python3")
        elif platform.system() == "Linux":
            print("  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv")
            print("  CentOS/RHEL: sudo yum install python3 python3-pip")
        return False
    else:
        print_success("Python version is compatible")
        return True

def diagnose_venv():
    """Diagnose virtual environment issues"""
    print_issue("Virtual Environment")
    
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print_error("Virtual environment not found")
        print_solution("Create virtual environment")
        print("  Run: python -m venv venv")
        return False
    
    # Check venv structure
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
        activate_script = venv_path / "Scripts" / "activate.bat"
    else:
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
        activate_script = venv_path / "bin" / "activate"
    
    issues = []
    if not python_exe.exists():
        issues.append("Python executable missing")
    if not pip_exe.exists():
        issues.append("Pip executable missing")
    if not activate_script.exists():
        issues.append("Activation script missing")
    
    if issues:
        print_error("Virtual environment is corrupted:")
        for issue in issues:
            print(f"  - {issue}")
        print_solution("Recreate virtual environment")
        print("  1. Remove: rm -rf venv (or rmdir /s venv on Windows)")
        print("  2. Create: python -m venv venv")
        return False
    
    # Test venv Python
    success, stdout, stderr = run_command([str(python_exe), "--version"])
    if success:
        print_success(f"Virtual environment Python: {stdout.strip()}")
        return True
    else:
        print_error(f"Virtual environment Python not working: {stderr}")
        return False

def diagnose_dependencies():
    """Diagnose dependency issues"""
    print_issue("Dependencies")
    
    if platform.system() == "Windows":
        python_exe = Path("venv") / "Scripts" / "python.exe"
        pip_exe = Path("venv") / "Scripts" / "pip.exe"
    else:
        python_exe = Path("venv") / "bin" / "python"
        pip_exe = Path("venv") / "bin" / "pip"
    
    if not python_exe.exists():
        print_error("Virtual environment not found")
        return False
    
    # Check pip
    success, stdout, stderr = run_command([str(pip_exe), "--version"])
    if not success:
        print_error(f"Pip not working: {stderr}")
        print_solution("Reinstall pip in virtual environment")
        print(f"  Run: {python_exe} -m ensurepip --upgrade")
        return False
    
    print(f"Pip version: {stdout.strip()}")
    
    # Check required packages
    required_packages = ['streamlit', 'pandas', 'plotly', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        success, stdout, stderr = run_command([str(python_exe), "-c", f"import {package}"])
        if success:
            print_success(f"{package} is installed")
        else:
            print_error(f"{package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print_solution("Install missing packages")
        if Path("requirements.txt").exists():
            print(f"  Run: {pip_exe} install -r requirements.txt")
        else:
            packages_str = " ".join([f"{pkg}>=1.0.0" for pkg in missing_packages])
            print(f"  Run: {pip_exe} install {packages_str}")
        return False
    
    return True

def diagnose_main_script():
    """Diagnose main script issues"""
    print_issue("Main Script")
    
    main_script = Path("epw_visualizer.py")
    if not main_script.exists():
        print_error("epw_visualizer.py not found")
        print_solution("Ensure you're in the correct directory")
        print("  The script should be in the same directory as this troubleshooter")
        return False
    
    # Check if readable
    try:
        with open(main_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) < 100:
            print_error("Main script appears to be empty or too small")
            return False
        
        if 'streamlit' not in content:
            print_error("Main script doesn't appear to be a Streamlit app")
            return False
        
        print_success("Main script exists and appears valid")
        return True
        
    except Exception as e:
        print_error(f"Cannot read main script: {str(e)}")
        return False

def diagnose_permissions():
    """Diagnose permission issues"""
    print_issue("Permissions")
    
    current_dir = Path.cwd()
    
    # Check write permissions
    test_file = current_dir / "test_write_permission.tmp"
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        test_file.unlink()
        print_success("Write permissions OK")
    except Exception as e:
        print_error(f"No write permission in current directory: {str(e)}")
        print_solution("Run from a directory where you have write permissions")
        return False
    
    # Check launcher script permissions (Unix only)
    if platform.system() != "Windows":
        launcher = Path("run.sh")
        if launcher.exists():
            if os.access(launcher, os.X_OK):
                print_success("run.sh is executable")
            else:
                print_error("run.sh is not executable")
                print_solution("Make run.sh executable")
                print("  Run: chmod +x run.sh")
                return False
    
    return True

def diagnose_network():
    """Diagnose network connectivity for package installation"""
    print_issue("Network Connectivity")
    
    # Test PyPI connectivity
    success, stdout, stderr = run_command(["python", "-c", 
        "import urllib.request; urllib.request.urlopen('https://pypi.org', timeout=10)"])
    
    if success:
        print_success("PyPI connectivity OK")
        return True
    else:
        print_error("Cannot connect to PyPI")
        print_solution("Check internet connection and firewall settings")
        print("  - Ensure you have internet access")
        print("  - Check if corporate firewall blocks PyPI")
        print("  - Try using a different network")
        return False

def auto_fix_common_issues():
    """Attempt to automatically fix common issues"""
    print_issue("Automatic Fixes")
    
    fixes_applied = []
    
    # Fix 1: Recreate virtual environment if corrupted
    venv_path = Path("venv")
    if venv_path.exists():
        if platform.system() == "Windows":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        success, _, _ = run_command([str(python_exe), "--version"])
        if not success:
            print("Attempting to recreate corrupted virtual environment...")
            try:
                shutil.rmtree(venv_path)
                import venv
                venv.create(venv_path, with_pip=True)
                fixes_applied.append("Recreated virtual environment")
                print_success("Virtual environment recreated")
            except Exception as e:
                print_error(f"Failed to recreate venv: {str(e)}")
    
    # Fix 2: Make run.sh executable (Unix only)
    if platform.system() != "Windows":
        run_script = Path("run.sh")
        if run_script.exists() and not os.access(run_script, os.X_OK):
            try:
                os.chmod(run_script, 0o755)
                fixes_applied.append("Made run.sh executable")
                print_success("Made run.sh executable")
            except Exception as e:
                print_error(f"Failed to make run.sh executable: {str(e)}")
    
    # Fix 3: Install missing dependencies
    if venv_path.exists():
        if platform.system() == "Windows":
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            pip_exe = venv_path / "bin" / "pip"
        
        if pip_exe.exists():
            print("Attempting to install/upgrade dependencies...")
            if Path("requirements.txt").exists():
                success, _, stderr = run_command([str(pip_exe), "install", "-r", "requirements.txt"])
            else:
                success, _, stderr = run_command([str(pip_exe), "install", 
                    "streamlit>=1.28.0", "pandas>=1.5.0", "plotly>=5.15.0", "numpy>=1.24.0"])
            
            if success:
                fixes_applied.append("Installed/upgraded dependencies")
                print_success("Dependencies installed/upgraded")
            else:
                print_error(f"Failed to install dependencies: {stderr}")
    
    if fixes_applied:
        print_success("Applied fixes:")
        for fix in fixes_applied:
            print(f"  ✓ {fix}")
    else:
        print("No automatic fixes were applied")
    
    return len(fixes_applied) > 0

def main():
    """Main troubleshooting function"""
    print_header("EPW Visualizer Troubleshooting")
    
    print("This script will diagnose common installation and runtime issues.\n")
    
    # Run diagnostics
    diagnostics = [
        ("Python Installation", diagnose_python),
        ("Virtual Environment", diagnose_venv),
        ("Dependencies", diagnose_dependencies),
        ("Main Script", diagnose_main_script),
        ("Permissions", diagnose_permissions),
        ("Network Connectivity", diagnose_network)
    ]
    
    issues_found = []
    
    for name, diagnostic_func in diagnostics:
        try:
            if not diagnostic_func():
                issues_found.append(name)
        except Exception as e:
            print_error(f"Error in {name} diagnostic: {str(e)}")
            issues_found.append(name)
    
    # Summary and recommendations
    print_header("Troubleshooting Summary")
    
    if not issues_found:
        print_success("No issues found! Your installation appears to be working correctly.")
        print("\nIf you're still experiencing problems:")
        print("  • Try running: python installation/check_installation.py")
        print("  • Check the application logs when running Streamlit")
    else:
        print_error(f"Found {len(issues_found)} issue(s):")
        for issue in issues_found:
            print(f"  ❌ {issue}")
        
        print("\n" + "="*60)
        print_colored(" ATTEMPTING AUTOMATIC FIXES", Colors.BOLD + Colors.YELLOW)
        print("="*60)
        
        fixes_applied = auto_fix_common_issues()
        
        if fixes_applied:
            print("\n" + "="*60)
            print_colored(" NEXT STEPS", Colors.BOLD + Colors.GREEN)
            print("="*60)
            print("Some issues were automatically fixed. Please:")
            print("  1. Run this troubleshooter again to verify fixes")
            print("  2. Run: python installation/check_installation.py")
            print("  3. Try launching the application")
        else:
            print("\n" + "="*60)
            print_colored(" MANUAL FIXES REQUIRED", Colors.BOLD + Colors.RED)
            print("="*60)
            print("Please address the issues above manually, then:")
            print("  1. Run the installation script: python installation/install.py")
            print("  2. Run this troubleshooter again")
            print("  3. Check the installation: python installation/check_installation.py")

if __name__ == "__main__":
    main()
