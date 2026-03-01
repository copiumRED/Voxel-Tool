$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$distDir = Join-Path $repoRoot "dist"
$buildDir = Join-Path $repoRoot "build"
$specPath = Join-Path $repoRoot "tools/build_pyinstaller.spec"
$exePath = Join-Path $repoRoot "dist/VoxelTool/VoxelTool.exe"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [string]$CommandLine
    )
    Write-Host "[STEP] $Label"
    Write-Host "       $CommandLine"
    cmd /c $CommandLine
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed ($Label) with exit code ${LASTEXITCODE}: $CommandLine"
    }
}

function Assert-PathExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PathValue,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )
    if (-not (Test-Path $PathValue)) {
        throw "$Label missing: $PathValue"
    }
}

Write-Host "[INFO] Packaging root: $repoRoot"
Assert-PathExists -PathValue $specPath -Label "PyInstaller spec"

if (-not (Test-Path ".venv")) {
    Invoke-Step -Label "Create virtual environment" -CommandLine "python -m venv .venv"
}

. .\.venv\Scripts\Activate.ps1
Invoke-Step -Label "Install requirements" -CommandLine "python -m pip install -r requirements.txt"

if (Test-Path $buildDir) {
    Write-Host "[STEP] Remove build directory: $buildDir"
    Remove-Item -Recurse -Force $buildDir
}
if (Test-Path $distDir) {
    Write-Host "[STEP] Remove dist directory: $distDir"
    Remove-Item -Recurse -Force $distDir
}

Invoke-Step -Label "Run PyInstaller" -CommandLine "pyinstaller tools/build_pyinstaller.spec --noconfirm --clean"
Assert-PathExists -PathValue $exePath -Label "Packaged executable"

$exeInfo = Get-Item $exePath
if ($exeInfo.Length -le 0) {
    throw "Packaged executable is empty: $exePath"
}

$exeHash = (Get-FileHash -Path $exePath -Algorithm SHA256).Hash.ToLower()

Write-Host "[PASS] Packaging complete."
Write-Host "ARTIFACT_EXE=$exePath"
Write-Host "ARTIFACT_SIZE_BYTES=$($exeInfo.Length)"
Write-Host "ARTIFACT_SHA256=$exeHash"
