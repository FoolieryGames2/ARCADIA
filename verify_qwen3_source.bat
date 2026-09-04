@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: ARCADIA Python environment is missing. Run setup.bat first.
    exit /b 1
)

".venv\Scripts\python.exe" "scripts\verify_qwen3_source.py" %*
exit /b %errorlevel%
