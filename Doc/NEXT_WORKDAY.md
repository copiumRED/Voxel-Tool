# NEXT_WORKDAY

Date Prepared: 2026-03-01
Prepared By: Codex

## Workday Definition
- Day-cycle complete: Tasks **01-40** executed in order and merged to `main` only.
- Current focus is operator validation and defect triage only (no new roadmap feature starts).

## 10-Minute Smoke Checklist
1. `git checkout main`
2. `git status` (must be clean)
3. `python src/app/main.py` (launch smoke)
4. In app: `Debug -> Create Test Voxels (Cross)` then `View -> Frame Voxels`
5. Navigation smoke:
- Orbit, pan, zoom
- Switch projection (perspective/orthographic)
6. Tool smoke:
- Brush paint/erase
- Box and line drag preview/apply
- Fill (plane and volume once)
7. IO smoke:
- Save project once
- Open project once
8. Export smoke:
- Export OBJ once
- Export glTF once
- Export VOX once
9. Test gate:
- `pytest -q`
10. Packaging smoke:
- `powershell -ExecutionPolicy Bypass -File .\tools\package_windows.ps1`
- Confirm `ARTIFACT_EXE`, `ARTIFACT_SIZE_BYTES`, `ARTIFACT_SHA256`

## Operator End-of-Day Validation Checklist
1. Preflight:
- `git checkout main`
- `git status` (must be clean)
- `python src/app/main.py` (launch/close cleanly)
- `pytest -q` (must be green)
2. Viewport/navigation:
- `Debug -> Create Test Voxels (Cross)` is visible and works.
- Orbit/pan/zoom in all navigation profiles (`Classic`, `MMB Orbit`, `Blender-Mix`).
- Hold `Alt` during camera motion and verify precision mode reduces sensitivity.
3. Tooling:
- Brush/box/line/fill paint + erase paths.
- Mirror axes + mirror overlay visuals.
- Voxel selection mode: select, move (arrow/page keys), duplicate via tools panel, undo/redo.
4. Scene workflow:
- Multi-part add/duplicate/rename/reorder/delete.
- Multi-select visibility/lock/delete actions.
- Groups: create/assign/unassign/lock/visibility.
5. Palette and UI:
- Palette slot edit + lock + import/export.
- Hotkey overlay (`Edit -> Shortcut Help`) opens modeless and closes.
- Command palette (`Ctrl+Shift+P`) runs selected commands.
- Dock layout preset save/load (1 and 2).
6. IO and recovery:
- Save/Open roundtrip once.
- Restart app with recent project prompt.
- Recovery snapshot prompt: test restore/discard/open recent/cancel paths.
7. Export:
- Export OBJ, glTF, VOX, and QB once each on multi-color scene.
- Re-import VOX and QB once; validate scene loads without crash.
8. Packaging:
- Run `powershell -ExecutionPolicy Bypass -File .\tools\package_windows.ps1`.
- Validate artifact path/size/hash outputs and launch packaged EXE.
9. Reporting:
- Record pass/fail with exact repro steps for any defect in `Doc/DAILY_REPORT.md`.
- Promote `main` to `stable` only after full sign-off.

## Day Objective
Deliver operator-ready validation of the completed 40-task MVP cycle and capture any defects as isolated fix branches into `main`.
