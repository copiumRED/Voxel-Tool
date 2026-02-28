# Task 1 Manual Checklist: Viewport Visibility Lockdown

## Goal
Confirm viewport visibility is reliable and test voxels are immediately visible.

## Environment
- Windows 10/11
- Run from repo root

## Steps
1. Launch app with `python src/app/main.py`.
2. Confirm viewport shows:
   - Grid lines
   - Axis lines
   - Debug text (`Voxels`, camera values, target)
3. Run `Debug -> Create Test Voxels (Cross)`.
4. Confirm the test voxels are clearly visible in the center region.
5. Run `View -> Frame Voxels`.
6. Confirm the camera centers the voxel cross and voxels remain visible on first try.
7. Orbit/pan/zoom to confirm voxels stay visible during camera movement.

## Expected Result
- All checks pass without crashes or invisible test voxels.
