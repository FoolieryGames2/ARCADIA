@echo off
setlocal
cd /d "%~dp0"
call check.bat
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" scripts\verify_phase0.py
exit /b %errorlevel%
