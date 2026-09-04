@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "scripts\prepare_qwen3_runtime.ps1" %*
if errorlevel 1 (
    echo.
    echo ERROR: Qwen3 runtime preparation failed.
    exit /b 1
)

exit /b 0
