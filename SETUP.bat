@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install Python 3.10 or newer, then run this file again.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating the project environment...
    py -3.12 -m venv .venv
    if errorlevel 1 py -3 -m venv .venv
    if errorlevel 1 (
        echo Could not create the project environment.
        pause
        exit /b 1
    )
)

echo Installing project packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

echo Downloading data and training the model...
".venv\Scripts\python.exe" train.py
if errorlevel 1 goto :failed

echo Building report and executed notebook...
".venv\Scripts\python.exe" scripts\build_deliverables.py
if errorlevel 1 goto :failed

echo Running project checks...
".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 goto :failed

echo.
echo Setup completed. Double-click START_PROJECT.bat to open the GUI.
pause
exit /b 0

:failed
echo.
echo Setup stopped because a required step failed. Read the message above, then run SETUP.bat again.
pause
exit /b 1
