@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
    echo ARCADIA is not set up. Run setup.bat first.
    exit /b 1
)
call ".venv\Scripts\activate.bat"
echo ARCADIA environment active. Type exit to close this shell.
cmd /k
