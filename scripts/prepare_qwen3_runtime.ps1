[CmdletBinding()]
param(
    [string]$ModelRoot = "",
    [string]$WorkRoot = "",
    [string]$OutputRoot = "",
    [switch]$SkipDependencies,
    [switch]$SkipBuild,
    [switch]$SkipConversion,
    [switch]$SkipQuantization,
    [switch]$NativeTests,
    [switch]$Smoke
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$LlamaRepository = 'https://github.com/ggml-org/llama.cpp.git'
$LlamaTag = 'b10796'
$LlamaCommit = '9a4843cf2f1a3fc8e39f8148e92ee6bfe18e2db6'
$CudaRoot = Join-Path $env:ProgramFiles 'NVIDIA GPU Computing Toolkit\CUDA\v13.3'
$CudaBin = Join-Path $CudaRoot 'bin'

# The CUDA runtime DLLs must be discoverable both while building and when an
# existing build is reused for smoke qualification.
$env:CUDA_PATH = $CudaRoot
$env:CUDA_PATH_V13_3 = $CudaRoot
$env:CUDAToolkit_ROOT = $CudaRoot
$env:CudaToolkitDir = "$CudaRoot\"
$env:PATH = "$CudaBin;$(Join-Path $CudaBin 'x64');$env:PATH"

if (-not $ModelRoot) {
    $ModelRoot = Join-Path $RepoRoot 'Base 3-4b model'
}
if (-not $WorkRoot) {
    $WorkRoot = Join-Path $RepoRoot 'build\qwen3-runtime-b10796'
}
if (-not $OutputRoot) {
    $OutputRoot = Join-Path $RepoRoot 'models\qwen3-4b-instruct-2507'
}

$ModelRoot = [System.IO.Path]::GetFullPath($ModelRoot)
$WorkRoot = [System.IO.Path]::GetFullPath($WorkRoot)
$OutputRoot = [System.IO.Path]::GetFullPath($OutputRoot)
$SourceRoot = Join-Path $WorkRoot 'llama.cpp'
$BuildRoot = Join-Path $WorkRoot 'build'
$VenvRoot = Join-Path $WorkRoot 'convert-venv'
$Python = Join-Path $VenvRoot 'Scripts\python.exe'
$ReleaseRoot = Join-Path $BuildRoot 'bin\Release'
$Quantize = Join-Path $ReleaseRoot 'llama-quantize.exe'
$Completion = Join-Path $ReleaseRoot 'llama-completion.exe'
$F16Model = Join-Path $OutputRoot 'qwen3-4b-instruct-2507-f16.gguf'
$Q4Model = Join-Path $OutputRoot 'qwen3-4b-instruct-2507-q4_k_m.gguf'

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$ArgumentList
    )
    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath"
    }
}

Write-Host '[ARCADIA] Qwen3-4B base runtime preparation'
Write-Host "Source package: $ModelRoot"
Write-Host "llama.cpp:     $LlamaTag ($LlamaCommit)"
Write-Host "Work root:     $WorkRoot"
Write-Host "Output root:   $OutputRoot"
Write-Host 'Standing:      qualification-only / T0'
Write-Host ''

$HostPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $HostPython -PathType Leaf)) {
    throw 'ARCADIA Python 3.12 environment is missing. Run setup.bat first.'
}
Invoke-Checked $HostPython (Join-Path $PSScriptRoot 'verify_qwen3_source.py') '--model-root' $ModelRoot

if (-not (Test-Path -LiteralPath (Join-Path $SourceRoot '.git') -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null
    Invoke-Checked 'git.exe' 'clone' '--branch' $LlamaTag '--depth' '1' $LlamaRepository $SourceRoot
}
$ActualCommit = (& git.exe -C $SourceRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $ActualCommit -ne $LlamaCommit) {
    throw "llama.cpp identity mismatch: expected $LlamaCommit, got $ActualCommit"
}

if (-not $SkipDependencies) {
    if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
        Invoke-Checked $HostPython '-m' 'venv' $VenvRoot
    }
    Invoke-Checked $Python '-m' 'pip' 'install' '--disable-pip-version-check' '--requirement' `
        (Join-Path $SourceRoot 'requirements\requirements-convert_hf_to_gguf.txt')
}
elseif (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Conversion environment is missing: $Python"
}

if (-not $SkipBuild) {
    $Nvcc = Join-Path $CudaRoot 'bin\nvcc.exe'
    if (-not (Test-Path -LiteralPath $Nvcc -PathType Leaf)) {
        throw "CUDA 13.3 compiler is missing: $Nvcc"
    }
    # CMake discovers nvcc from the explicit compiler path, while Visual Studio's
    # CUDA .targets files resolve their toolkit directory from these properties.
    Invoke-Checked 'cmake.exe' '--fresh' '-S' $SourceRoot '-B' $BuildRoot `
        '-G' 'Visual Studio 17 2022' '-A' 'x64' `
        '-DGGML_CUDA=ON' "-DCUDAToolkit_ROOT=$CudaRoot" "-DCMAKE_CUDA_COMPILER=$Nvcc" `
        '-DCMAKE_CUDA_ARCHITECTURES=75' '-DGGML_NATIVE=ON' '-DBUILD_SHARED_LIBS=ON' `
        '-DLLAMA_BUILD_SERVER=OFF' '-DLLAMA_BUILD_TESTS=ON' '-DLLAMA_BUILD_EXAMPLES=ON' `
        '-DLLAMA_BUILD_TOOLS=ON'
    # In b10796 llama-cli is coupled to the optional server implementation.
    # Keep LLAMA_BUILD_SERVER=OFF and use the non-interactive completion tool.
    Invoke-Checked 'cmake.exe' '--build' $BuildRoot '--config' 'Release' '--parallel' '2' `
        '--target' 'llama-completion'
    Invoke-Checked 'cmake.exe' '--build' $BuildRoot '--config' 'Release' '--parallel' '2' `
        '--target' 'llama-quantize'
}
if (-not (Test-Path -LiteralPath $Completion -PathType Leaf)) {
    throw "llama-completion was not built: $Completion"
}
if (-not (Test-Path -LiteralPath $Quantize -PathType Leaf)) {
    throw "llama-quantize was not built: $Quantize"
}

if ($NativeTests) {
    # Avoid the b10796 aggregate ALL_BUILD target: its optional llama-app target
    # still links llama-server-impl even when LLAMA_BUILD_SERVER=OFF. Build only
    # the registered tests and their one example dependency, then run CTest.
    $NativeTestTargets = @(
        'test-alloc',
        'test-arg-parser',
        'test-autorelease',
        'test-backend-ops',
        'test-backend-sampler',
        'test-barrier',
        'test-c',
        'test-chat-analysis',
        'test-chat-auto-parser',
        'test-chat-peg-parser',
        'test-chat-template',
        'test-col2im-1d',
        'test-export-graph-ops',
        'test-gguf',
        'test-jinja',
        'test-log',
        'test-model-load-cancel',
        'test-model-resolution',
        'test-mtmd-c-api',
        'test-mtmd-impl',
        'test-opt',
        'test-peg-parser',
        'test-quantize-fns',
        'test-quantize-perf',
        'test-recurrent-state-rollback',
        'test-rope',
        'test-save-load-state',
        'test-state-restore-fragmented',
        'test-thread-safety',
        'test-tokenizer-0',
        'llama-eval-callback'
    )
    foreach ($Target in $NativeTestTargets) {
        Invoke-Checked 'cmake.exe' '--build' $BuildRoot '--config' 'Release' '--parallel' '2' `
            '--target' $Target
    }
    Invoke-Checked 'ctest.exe' '--test-dir' $BuildRoot '-C' 'Release' '--output-on-failure'
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
if (-not $SkipConversion) {
    Invoke-Checked $Python (Join-Path $SourceRoot 'convert_hf_to_gguf.py') $ModelRoot `
        '--outfile' $F16Model '--outtype' 'f16'
}
if (-not (Test-Path -LiteralPath $F16Model -PathType Leaf)) {
    throw "F16 conversion is missing: $F16Model"
}

if (-not $SkipQuantization) {
    Invoke-Checked $Quantize $F16Model $Q4Model 'Q4_K_M'
}
if (-not (Test-Path -LiteralPath $Q4Model -PathType Leaf)) {
    throw "Q4_K_M candidate is missing: $Q4Model"
}

Write-Host ''
Write-Host '[ARCADIA] Candidate artifacts'
Get-Item -LiteralPath $F16Model, $Q4Model | ForEach-Object {
    $Stream = [System.IO.File]::OpenRead($_.FullName)
    try {
        $Hasher = [System.Security.Cryptography.SHA256]::Create()
        try {
            $Hash = ([System.BitConverter]::ToString($Hasher.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant()
        }
        finally {
            $Hasher.Dispose()
        }
    }
    finally {
        $Stream.Dispose()
    }
    Write-Host "$($_.Name) bytes=$($_.Length) sha256=$Hash"
}

if ($Smoke) {
    Write-Host ''
    Write-Host '[ARCADIA] BASE_ONLY_TEST_MODE smoke (no adapter, no authority promotion)'
    Invoke-Checked $Completion '-m' $Q4Model '-ngl' '99' '-c' '2048' '-n' '8' '--seed' '42' `
        '--temp' '0' '-no-cnv' '-p' 'Reply with only the word Ready.'
}

Write-Host ''
Write-Host 'PASS: Qwen3 runtime candidate prepared. Qualification authority remains T0.'
