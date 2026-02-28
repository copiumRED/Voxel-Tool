# Windows Packaging Checklist

1. Open PowerShell in repo root.
2. Run `powershell -ExecutionPolicy Bypass -File .\tools\package_windows.ps1`.
3. Confirm output contains: `Packaging complete.`
4. Confirm file exists: `dist\VoxelTool\VoxelTool.exe`.
5. Launch packaged app once:
   - `.\dist\VoxelTool\VoxelTool.exe`
6. Smoke checks in packaged app:
   - Viewport loads with grid/axes/debug text.
   - `Debug -> Create Test Voxels (Cross)` is visible.
   - `View -> Frame Voxels` centers test voxels.
   - `File -> Export OBJ` writes a file.
   - `File -> Export glTF` writes a file.
