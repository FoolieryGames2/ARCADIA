@echo off
setlocal
cd /d "%~dp0"
call check.bat
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m ruff check scripts\verify_architecture_freeze.py
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m mypy --strict scripts\verify_architecture_freeze.py
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" scripts\verify_architecture_freeze.py
exit /b %errorlevel%
