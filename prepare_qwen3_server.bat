@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: ARCADIA environment is missing. Run setup.bat first.
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\prepare_qwen3_server.ps1"
exit /b %errorlevel%
