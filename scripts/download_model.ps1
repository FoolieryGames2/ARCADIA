[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $root 'manifests\phase0_inputs.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$target = Join-Path $root $manifest.base_model.local_path
$targetDirectory = Split-Path -Parent $target
New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null

& curl.exe -L --fail --retry 3 --continue-at - --output $target $manifest.base_model.source_url
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$item = Get-Item -LiteralPath $target
$hash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
if ($item.Length -ne $manifest.base_model.size_bytes) {
    throw "Model byte count mismatch: expected $($manifest.base_model.size_bytes), got $($item.Length)"
}
if ($hash -ne $manifest.base_model.sha256) {
    throw "Model SHA-256 mismatch: expected $($manifest.base_model.sha256), got $hash"
}

Write-Host "PASS model bytes=$($item.Length) sha256=$hash"
