@echo off
setlocal EnableExtensions
cd /d "%~dp0"

powershell -NoProfile -Command "$project=[regex]::Escape($PWD.Path); Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'streamlit' -and $_.CommandLine -match $project } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Output ('Stopped Streamlit process ' + $_.ProcessId) }"
echo Any Streamlit instance launched from this project folder has been closed.
exit /b 0
