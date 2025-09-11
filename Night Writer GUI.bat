@echo off
REM 🌙 Night Writer GUI Launcher for Windows
REM Double-click this file to launch the GUI

echo Starting Night Writer GUI...
echo Activating conda environment...

REM Activate conda environment and run GUI
call conda activate graphrag-gpu
python night_writer_gui.py

REM Keep window open if there's an error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error occurred. Press any key to exit...
    pause >nul
)
