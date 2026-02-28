$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $repoRoot ".venv"

if (-not (Test-Path $venvDir)) {
    python -m venv $venvDir
}

. (Join-Path $venvDir "Scripts\Activate.ps1")

python -m pip install --upgrade pip
python -m pip install -r (Join-Path $repoRoot "requirements.txt")
python -m pip install -e $repoRoot

python -m voxel_tool.app.main
