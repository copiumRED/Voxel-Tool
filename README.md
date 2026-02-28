# Voxel Tool (Desktop)

See `Doc/PROJECT_SPEC.md` for the full specification.

## Quick Start (Windows)

From repo root, run:

```powershell
.\run.ps1
```

This creates/uses `.venv`, installs dependencies, installs the package in editable mode, and launches the app.

If you prefer manual steps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python src/app/main.py
```

## Windows Packaging (PyInstaller)

Build a standalone Windows artifact from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\package_windows.ps1
```

Expected output executable:

`dist\VoxelTool\VoxelTool.exe`

For verification steps, use:

`Doc/PACKAGING_CHECKLIST.md`
