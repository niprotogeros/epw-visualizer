
# EPW Visualizer

A Python-based weather data visualization tool for analyzing EnergyPlus Weather (EPW) files using Streamlit.

## Description

EPW Visualizer is an interactive web application that allows users to upload and visualize weather data from EPW files. The tool provides comprehensive charts and analysis of various weather parameters including temperature, humidity, solar radiation, and wind patterns.

## Features

- Interactive web interface built with Streamlit
- Support for standard EPW file format
- Multiple visualization types (line charts, scatter plots, heatmaps)
- Real-time data filtering and analysis
- Export capabilities for charts and processed data
- Responsive design for desktop and mobile viewing
- **Windows desktop shortcut & app icon** (optional)

## Installation

### 🚀 Quick Installation (Recommended)

**One-Click Installers:**
- **Windows**: Double-click `install.bat`
- **macOS/Linux**: Run `./install.sh`
- **Cross-platform**: Run `python installation/install.py`
- **GUI Setup**: Run `python installation/quick_setup.py`

**Docker Installation:**
```bash
cd docker
docker-compose up -d
# Access at http://localhost:8501
```

### 📋 Manual Installation

**Prerequisites:**
- Python 3.8 or higher
- pip package manager

**Setup:**

1. Clone this repository:
```bash
git clone https://github.com/yourusername/epw-visualizer.git
cd epw-visualizer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

### 🔧 Installation Verification & Troubleshooting

```bash
# Verify installation
python installation/check_installation.py

# Automated troubleshooting
python installation/troubleshoot.py
```

📖 **For detailed installation options and troubleshooting, see [Installation Automation Guide](installation/INSTALLATION_AUTOMATION.md)**

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Upload an EPW file using the file uploader

4. Explore the various visualization options and filters

## Optional: Windows desktop shortcut & icon

You can launch the app from a desktop shortcut that activates your virtual environment and starts Streamlit.

**Files:**

- `launch_epw_visualizer.bat` – starts the app (provided in the repository root).
- `scripts/windows/Create_EPWVisualizer_Shortcut.vbs` – creates a desktop shortcut.
- `assets/icons/EPWVisualizer.ico` – icon used by the shortcut.

## File Structure

```
epw-visualizer/
├── epw_visualizer.py
├── launch_epw_visualizer.bat
├── requirements.txt
├── README.md
├── REPOSITORY_SUMMARY.md
├── INSTALLATION.md
├── Create_EPWVisualizer_Shortcut.vbs
├── EPWVisualizer.ico
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

## Acknowledgments

- EnergyPlus team for the EPW file format specification
- Streamlit community for the excellent framework
- Contributors and users of this project
