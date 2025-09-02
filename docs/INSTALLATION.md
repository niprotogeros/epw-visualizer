
# Installation Guide

This guide will help you set up EPW Visualizer on your system.

## Prerequisites

- Python 3.8 or higher
- `pip` (bundled with Python)
- (Windows optional) Permission to create a Desktop shortcut

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/epw-visualizer.git
cd epw-visualizer
```

## 2) Create & activate a virtual environment (recommended)

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3) Install dependencies

```bash
pip install -r requirements.txt
# or
pip install streamlit pandas plotly numpy
```

## 4) Run the app

```bash
streamlit run epw_visualizer.py
```

Open the URL shown in the terminal (usually http://localhost:8501). Press `Ctrl+C` in the terminal to stop the server. Run `deactivate` to exit the virtual environment when finished.

---

## Optional (Windows): Create a Desktop shortcut with icon

This project provides a ready-made `.vbs` script and `.ico` file so you can start the app from your Desktop with one double‑click.

**Files used**

- `launch_epw_visualizer.bat` – activates `venv` and launches Streamlit.
- `scripts/windows/Create_EPWVisualizer_Shortcut.vbs` – creates the Desktop shortcut.
- `assets/icons/EPWVisualizer.ico` – the shortcut’s icon.

**How it works**

- The VBS script sets:
  - `TargetPath` → `launch_epw_visualizer.bat`
  - `WorkingDirectory` → the project folder
  - `IconLocation` → `assets/icons/EPWVisualizer.ico`

**Steps**

1. Ensure `venv` exists and dependencies are installed.
2. Double‑click `scripts/windows/Create_EPWVisualizer_Shortcut.vbs`.
3. Look on your Desktop for **EPW Visualiser.lnk**.
4. Double‑click the shortcut anytime to start the app.

**Editing the VBS script (if needed)**

If you change folder names, open `scripts/windows/Create_EPWVisualizer_Shortcut.vbs` in a text editor and update the relative paths accordingly.

---

## Troubleshooting

### Common Issues

**ImportError: No module named 'pandas'**
- Solution: Install pandas using `pip install pandas` the missing package or run `pip install -r requirements.txt`.

**Browser doesn’t open**
- Solution: Copy the terminal URL (e.g. http://localhost:8501) and paste it into your browser.

**FileNotFoundError: EPW file not found**
- Solution: Check the file path and ensure the EPW file exists

**Permission denied errors**
- Solution: Ensure you have read permissions for the EPW file and write permissions for the output directory

**Permission issues on Windows for the shortcut**
- Solution: Run the VBS script from a folder you own (e.g., inside your user profile).

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

- **Minimum**: Python 3.8, 512MB RAM, 50MB disk space
- **Recommended**: Python 3.10+, 1GB RAM, 100MB disk space
- **Operating Systems**: Windows 10+, macOS 10.14+, Linux (most distributions)
