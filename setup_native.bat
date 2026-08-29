@echo off
setlocal
cd /d "%~dp0"

echo [ARCADIA] Native CUDA build prerequisites
echo This requires administrator approval and may request a restart.
echo.

winget install --id Microsoft.VisualStudio.2022.BuildTools --version 17.14.39 --exact --silent --accept-package-agreements --accept-source-agreements --override "--wait --quiet --norestart --add Microsoft.VisualStudio.Workload.VCTools"
if errorlevel 1 exit /b 1

winget install --id Nvidia.CUDA --version 13.3 --exact --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 exit /b 1

echo Native prerequisites installed. Open a fresh terminal, then run build_llama_cuda.bat.
exit /b 0
