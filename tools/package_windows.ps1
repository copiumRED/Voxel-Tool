$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Invoke-Step {
    param(
        [string]$CommandLine
    )
    Write-Host ">> $CommandLine"
    cmd /c $CommandLine
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $CommandLine"
    }
}

if (-not (Test-Path ".venv")) {
    Invoke-Step "python -m venv .venv"
}

. .\.venv\Scripts\Activate.ps1

Invoke-Step "python -m pip install -r requirements.txt"

if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

Invoke-Step "pyinstaller tools/build_pyinstaller.spec --noconfirm --clean"

Write-Host "Packaging complete."
Write-Host "EXE path: $repoRoot\\dist\\VoxelTool\\VoxelTool.exe"
