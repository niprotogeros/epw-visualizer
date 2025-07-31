
#!/bin/bash

echo "========================================"
echo "Starting EPW Visualizer"
echo "========================================"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}ERROR: Virtual environment not found${NC}"
    echo "Please run installation first: ./install.sh"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if main script exists
if [ ! -f "epw_visualizer.py" ]; then
    echo -e "${RED}ERROR: epw_visualizer.py not found${NC}"
    echo "Please ensure you're in the correct directory"
    exit 1
fi

# Start the application
echo -e "${GREEN}Starting EPW Visualizer...${NC}"
echo
echo "The application will open in your web browser."
echo "Press Ctrl+C to stop the application."
echo

streamlit run epw_visualizer.py

echo
echo "Application stopped."
