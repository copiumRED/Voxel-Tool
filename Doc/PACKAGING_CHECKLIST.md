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
