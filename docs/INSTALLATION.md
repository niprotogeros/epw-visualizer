
# Installation Guide

This guide will help you set up EPW Visualizer on your system.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/epw-visualizer.git
cd epw-visualizer
```

### 2. Install Required Dependencies
```bash
pip install pandas matplotlib seaborn numpy
```

Or if you prefer using a virtual environment (recommended):
```bash
# Create virtual environment
python -m venv epw_env

# Activate virtual environment
# On Windows:
epw_env\Scripts\activate
# On macOS/Linux:
source epw_env/bin/activate

# Install dependencies
pip install pandas matplotlib seaborn numpy
```

### 3. Verify Installation
Run the script with a sample EPW file to verify everything works:
```bash
python epw_visualizer.py path/to/your/file.epw
```

## Getting EPW Files

EPW (EnergyPlus Weather) files can be downloaded from:
- [EnergyPlus Weather Data](https://energyplus.net/weather)
- [Climate.OneBuilding.Org](https://climate.onebuilding.org/)
- [NREL](https://www.nrel.gov/analysis/sam/weather-data.html)

## Troubleshooting

### Common Issues

**ImportError: No module named 'pandas'**
- Solution: Install pandas using `pip install pandas`

**FileNotFoundError: EPW file not found**
- Solution: Check the file path and ensure the EPW file exists

**Permission denied errors**
- Solution: Ensure you have read permissions for the EPW file and write permissions for the output directory

**Memory errors with large files**
- Solution: EPW files are typically small, but if you encounter memory issues, try closing other applications

### Getting Help

If you encounter issues not covered here:
1. Check the [GitHub Issues](../../issues) for similar problems
2. Create a new issue using the bug report template
3. Include your system information and error messages

## Development Setup

If you want to contribute to the project:

1. Fork the repository
2. Follow the installation steps above
3. Install additional development dependencies (if any are added in the future)
4. See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines

## System Requirements

- **Minimum**: Python 3.7, 512MB RAM, 50MB disk space
- **Recommended**: Python 3.9+, 1GB RAM, 100MB disk space
- **Operating Systems**: Windows 10+, macOS 10.14+, Linux (most distributions)
