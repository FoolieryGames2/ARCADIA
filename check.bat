@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: .venv is missing. Run setup.bat first.
    exit /b 1
)
".venv\Scripts\python.exe" -m arcadia doctor
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pytest
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m ruff check src tests
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m mypy
exit /b %errorlevel%
