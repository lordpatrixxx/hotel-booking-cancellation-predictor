@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Please run SETUP.bat before starting the project.
    pause
    exit /b 1
)

if not exist "artifacts\cancellation_model.joblib" (
    echo The model has not been trained yet. Please run SETUP.bat.
    pause
    exit /b 1
)

if not exist "work" mkdir "work"
set PORT=
for /f %%P in ('powershell -NoProfile -Command "$ports=8501..8510; foreach($p in $ports){ if(-not (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue)){ $p; break } }"') do set PORT=%%P
if "%PORT%"=="" (
    echo No free local port was found between 8501 and 8510.
    pause
    exit /b 1
)

start "Hotel Booking Cancellations" /min cmd /c ""%CD%\.venv\Scripts\python.exe" -m streamlit run "%CD%\app.py" --server.headless true --server.port %PORT% --browser.gatherUsageStats false > "%CD%\work\streamlit.log" 2>&1"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:%PORT%"
echo The GUI is opening at http://127.0.0.1:%PORT%
exit /b 0
