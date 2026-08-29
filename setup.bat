@echo off
setlocal
cd /d "%~dp0"

echo [ARCADIA] Deterministic host environment setup
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: The Windows Python launcher ^(py.exe^) is required.
    echo Install 64-bit Python 3.12, then run this file again.
    exit /b 1
)

py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python 3.12 is not installed or not visible to py.exe.
    echo Download: https://www.python.org/downloads/windows/
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creating .venv with Python 3.12...
    py -3.12 -m venv .venv
    if errorlevel 1 exit /b 1
) else (
    echo [1/4] Reusing existing .venv...
)

echo [2/4] Updating packaging tools...
".venv\Scripts\python.exe" -m pip install --upgrade "pip==26.2.1" "setuptools==80.9.0" "wheel==0.48.0"
if errorlevel 1 exit /b 1

echo [3/4] Installing pinned ARCADIA host and development dependencies...
".venv\Scripts\python.exe" -m pip install --requirement requirements.lock
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install --editable ".[dev]" --no-deps
if errorlevel 1 exit /b 1

if not exist ".env" copy /y ".env.example" ".env" >nul

echo [4/4] Validating environment...
call check.bat
if errorlevel 1 exit /b 1

echo.
echo ARCADIA host environment is ready.
echo Use activate.bat to open an activated development shell.
exit /b 0
