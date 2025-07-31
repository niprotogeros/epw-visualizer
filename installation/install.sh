
#!/bin/bash

echo "========================================"
echo "EPW Visualizer - macOS/Linux Installation"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed"
        echo "Please install Python 3.8+ from:"
        echo "  macOS: https://python.org or 'brew install python3'"
        echo "  Linux: 'sudo apt install python3 python3-pip python3-venv' (Ubuntu/Debian)"
        echo "         'sudo yum install python3 python3-pip' (CentOS/RHEL)"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Get Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "Found Python $PYTHON_VERSION"

# Check Python version
$PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Python 3.8 or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

print_success "Python version check passed!"
echo

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment"
    echo "Try installing python3-venv: sudo apt install python3-venv (Ubuntu/Debian)"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Installing default dependencies..."
    pip install streamlit>=1.28.0 pandas>=1.5.0 plotly>=5.15.0 numpy>=1.24.0
fi

if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    exit 1
fi

echo
echo "========================================"
print_success "Installation completed successfully!"
echo "========================================"
echo
echo "To run EPW Visualizer:"
echo "1. Run: ./run.sh, or"
echo "2. Run: source venv/bin/activate && streamlit run epw_visualizer.py"
echo
echo "Installation verification: python installation/check_installation.py"
echo

# Make run script executable
if [ -f "run.sh" ]; then
    chmod +x run.sh
fi
