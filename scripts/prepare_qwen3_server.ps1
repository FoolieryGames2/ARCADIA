[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$RuntimeRoot = Join-Path $RepoRoot 'build\qwen3-runtime-b10796'
$SourceRoot = Join-Path $RuntimeRoot 'llama.cpp'
$BuildRoot = Join-Path $RuntimeRoot 'build'
$Server = Join-Path $BuildRoot 'bin\Release\llama-server.exe'
$ServerImpl = Join-Path $BuildRoot 'bin\Release\llama-server-impl.dll'
$CudaRoot = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3'
$ExpectedCommit = '9a4843cf2f1a3fc8e39f8148e92ee6bfe18e2db6'
$ExpectedHash = 'fb931a5ee34a4ebd508044de6564b0dba5947f6ebf26ba762d97501f79076c7f'
$ExpectedImplHash = '6f8d223b3ff2a9dc68e3ca4a26ba70a91bcd7432cd8525a560533d2565238d68'

function Get-Sha256Hex([string]$Path) {
    $Stream = [System.IO.File]::OpenRead($Path)
    $Hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($Hasher.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Hasher.Dispose()
        $Stream.Dispose()
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $SourceRoot '.git') -PathType Container)) {
    throw 'Pinned llama.cpp source is missing. Run prepare_qwen3_runtime.bat first.'
}
$ActualCommit = (& git.exe -C $SourceRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $ActualCommit -ne $ExpectedCommit) {
    throw "llama.cpp identity mismatch: expected $ExpectedCommit, got $ActualCommit"
}
if (-not (Test-Path -LiteralPath (Join-Path $CudaRoot 'bin\nvcc.exe') -PathType Leaf)) {
    throw "CUDA 13.3 compiler is missing: $CudaRoot"
}

$env:CUDA_PATH = $CudaRoot
$env:CUDA_PATH_V13_3 = $CudaRoot
$env:CudaToolkitDir = "$CudaRoot\"

& cmake.exe -S $SourceRoot -B $BuildRoot '-DLLAMA_BUILD_SERVER=ON' `
    '-DLLAMA_BUILD_UI=OFF' '-DLLAMA_USE_PREBUILT_UI=OFF'
if ($LASTEXITCODE -ne 0) { throw 'llama-server CMake configuration failed' }
$GeneratedUi = Join-Path $BuildRoot 'tools\ui\dist'
if (Test-Path -LiteralPath $GeneratedUi -PathType Container) {
    Remove-Item -LiteralPath $GeneratedUi -Recurse -Force
}
& cmake.exe --build $BuildRoot --config Release --parallel 2 --target llama-server
if ($LASTEXITCODE -ne 0) { throw 'llama-server build failed' }

if (-not (Test-Path -LiteralPath $Server -PathType Leaf)) {
    throw "llama-server was not built: $Server"
}
$ServerItem = Get-Item -LiteralPath $Server
$ActualHash = Get-Sha256Hex $Server
if ($ServerItem.Length -ne 10752 -or $ActualHash -ne $ExpectedHash) {
    throw "llama-server identity mismatch: bytes=$($ServerItem.Length) sha256=$ActualHash"
}
$ServerImplItem = Get-Item -LiteralPath $ServerImpl
$ActualImplHash = Get-Sha256Hex $ServerImpl
if ($ServerImplItem.Length -ne 3177984 -or $ActualImplHash -ne $ExpectedImplHash) {
    throw "llama-server implementation identity mismatch: bytes=$($ServerImplItem.Length) sha256=$ActualImplHash"
}

Write-Host '[ARCADIA] Resident CUDA server ready'
Write-Host "commit=$ActualCommit"
Write-Host "server_sha256=$ActualHash"
Write-Host "server_impl_sha256=$ActualImplHash"
