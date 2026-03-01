# Windows Packaging Checklist

1. Open PowerShell in repo root.
2. Run `powershell -ExecutionPolicy Bypass -File .\tools\package_windows.ps1`.
3. Confirm script exits with code `0` and output contains:
   - `[PASS] Packaging complete.`
   - `ARTIFACT_EXE=<absolute path>`
   - `ARTIFACT_SIZE_BYTES=<non-zero>`
   - `ARTIFACT_SHA256=<64 hex chars>`
4. Confirm file exists: `dist\VoxelTool\VoxelTool.exe` and size is non-zero.
5. Launch packaged app once:
   - `.\dist\VoxelTool\VoxelTool.exe`
   - If launch is successful, process should stay running until closed manually.
6. Smoke checks in packaged app:
   - Viewport loads with grid/axes/debug text.
   - `Debug -> Create Test Voxels (Cross)` is visible.
   - `View -> Frame Voxels` centers test voxels.
   - `File -> Export OBJ` writes a file.
   - `File -> Export glTF` writes a file.
7. Record artifact hash and run timestamp in `Doc/DAILY_REPORT.md` end-of-day entry.

## Notes (2026-03-01 validation run)
- `tools/build_pyinstaller.spec` now resolves project root robustly when invoked via `pyinstaller tools/build_pyinstaller.spec`.
- `tools/package_windows.ps1` now emits explicit pass/fail step labels and deterministic artifact diagnostics.
- Packaging script no longer requires `pip install -e .` for packaging flow.

## Portable Zip Workflow (Operator Ready)
1. Complete the packaging steps above so `dist\VoxelTool\VoxelTool.exe` exists.
2. Set output folder:
   - `New-Item -ItemType Directory -Force .\artifacts | Out-Null`
3. Build portable zip:
   - `Compress-Archive -Path .\dist\VoxelTool\* -DestinationPath .\artifacts\VoxelTool-portable.zip -Force`
4. Validate zip exists and size is non-zero:
   - `Get-Item .\artifacts\VoxelTool-portable.zip | Format-List FullName,Length,LastWriteTime`
5. Record zip hash:
   - `Get-FileHash .\artifacts\VoxelTool-portable.zip -Algorithm SHA256`
6. Manual unzip smoke:
   - Extract zip into a clean folder.
   - Run `VoxelTool.exe` from extracted folder.
   - Verify app launches and viewport loads.
7. Operator validation matrix (packaged build):
   - `Debug -> Create Test Voxels (Cross)` works.
   - Orbit/pan/zoom + `Alt` precision modifier works.
   - Brush paint/erase and selection move/duplicate work.
   - Export OBJ/glTF/VOX/QB creates non-empty files.
   - Save/Open roundtrip works once.
8. Record packaging evidence in `Doc/DAILY_REPORT.md`:
   - artifact path
   - artifact SHA256
   - zip path + SHA256
   - pass/fail for packaged smoke matrix

## Installer Prerequisites (Prep Only)
- Inno Setup (or equivalent installer tool) selected and version pinned.
- Installer script path reserved (`tools\installer\VoxelTool.iss`) with owner assigned.
- Product metadata finalized: app name, version string, publisher, support URL.
- Artifact signing decision documented (unsigned for internal testing vs code-signed release).
- Install/uninstall smoke checklist drafted:
  - Fresh install
  - Launch app
  - Uninstall cleanly
  - Reinstall over existing build
