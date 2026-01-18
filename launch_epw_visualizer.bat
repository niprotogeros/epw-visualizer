@echo off
REM Change directory to your application folder.
cd /d "C:\Users\nipro\epw_visualizer"

REM Optionally create the virtual environment if it doesn't exist.
if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Creating one now...
    python -m venv venv
)

REM Activate the virtual environment.
call venv\Scripts\activate.bat

REM Run the Streamlit application.
streamlit run epw_visualizer.py

REM Keeps the window open so you can see any messages.
pause