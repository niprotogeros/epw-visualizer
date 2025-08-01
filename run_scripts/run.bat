
@echo off
echo ========================================
echo Starting EPW Visualizer
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found
    echo Please run installation first: install.bat
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if main script exists
if not exist "epw_visualizer.py" (
    echo ERROR: epw_visualizer.py not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

:: Start the application
echo Starting EPW Visualizer...
echo.
echo The application will open in your web browser.
echo Press Ctrl+C to stop the application.
echo.

streamlit run epw_visualizer.py

echo.
echo Application stopped.
pause
