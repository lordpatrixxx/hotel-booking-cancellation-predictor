@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Starting Hotel Booking Cancellation Predictor...

:: Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [.venv not found] Running initial setup first...
    call SETUP.bat
    if not exist ".venv\Scripts\python.exe" (
        echo [ERROR] Virtual environment could not be set up. Please run SETUP.bat manually.
        pause
        exit /b 1
    )
)

:: Check if model exists
if not exist "artifacts\cancellation_model.joblib" (
    echo [Model artifact missing] Training the model...
    ".venv\Scripts\python.exe" train.py
    if errorlevel 1 (
        echo [ERROR] Model training failed.
        pause
        exit /b 1
    )
)

if not exist "work" mkdir "work"

:: Find a free port between 8501 and 8510
set PORT=
for /f %%P in ('powershell -NoProfile -Command "$ports=8501..8510; foreach($p in $ports){ if(-not (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue)){ $p; break } }"') do set PORT=%%P
if "%PORT%"=="" set PORT=8501

echo Launching Streamlit on port %PORT%...
start "Hotel Booking Cancellations" /min cmd /c ""%CD%\.venv\Scripts\python.exe" -m streamlit run "%CD%\app.py" --server.headless true --server.port %PORT% --browser.gatherUsageStats false > "%CD%\work\streamlit.log" 2>&1"

timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:%PORT%"
echo GUI is live at: http://127.0.0.1:%PORT%
exit /b 0
