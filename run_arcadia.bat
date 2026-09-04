@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: ARCADIA environment is missing. Run setup.bat first.
    exit /b 1
)

".venv\Scripts\python.exe" -m arcadia run %*
exit /b %errorlevel%
