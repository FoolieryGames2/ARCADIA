@echo off
setlocal
cd /d "%~dp0"

set "VSWHERE=C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (
    echo ERROR: Visual Studio Build Tools are missing. Run setup_native.bat.
    exit /b 1
)

for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products Microsoft.VisualStudio.Product.BuildTools -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%i"
if not defined VSINSTALL (
    echo ERROR: The Visual C++ x64 toolchain is missing. Run setup_native.bat.
    exit /b 1
)

set "ARCADIA_CUDA_ROOT=%ProgramFiles%\NVIDIA GPU Computing Toolkit\CUDA\v13.3"
if not exist "%ARCADIA_CUDA_ROOT%\bin\nvcc.exe" (
    echo ERROR: CUDA Toolkit 13.3 is missing. Run setup_native.bat and approve the UAC prompt.
    exit /b 1
)

call "%VSINSTALL%\VC\Auxiliary\Build\vcvars64.bat"
if errorlevel 1 exit /b 1
set "CUDA_PATH=%ARCADIA_CUDA_ROOT%"
set "CUDA_PATH_V13_3=%ARCADIA_CUDA_ROOT%"
set "CUDAToolkit_ROOT=%ARCADIA_CUDA_ROOT%"
set "PATH=%ARCADIA_CUDA_ROOT%\bin\x64;%ARCADIA_CUDA_ROOT%\bin;%PATH%"

git submodule update --init --recursive vendor/llama.cpp
if errorlevel 1 exit /b 1

cmake --fresh -S vendor/llama.cpp -B build/llama.cpp -G "Visual Studio 17 2022" -A x64 -DGGML_CUDA=ON -DCUDAToolkit_ROOT="%ARCADIA_CUDA_ROOT%" -DCMAKE_CUDA_COMPILER="%ARCADIA_CUDA_ROOT%\bin\nvcc.exe" -DCMAKE_CUDA_ARCHITECTURES=75 -DGGML_NATIVE=ON -DBUILD_SHARED_LIBS=ON -DLLAMA_BUILD_SERVER=OFF -DLLAMA_BUILD_APP=OFF -DLLAMA_BUILD_TESTS=ON -DLLAMA_BUILD_EXAMPLES=ON
if errorlevel 1 exit /b 1

rem Keep concurrency low: this workstation has 8 GB of RAM, and an unrestricted
rem MSBuild/CUDA compile can race or exhaust memory before all objects are ready.
cmake --build build/llama.cpp --config Release --parallel 2
if errorlevel 1 (
    echo.
    echo ERROR: llama.cpp CUDA build failed. The window will remain open for review.
    pause
    exit /b 1
)

echo.
echo llama.cpp CUDA build completed successfully.
exit /b 0
