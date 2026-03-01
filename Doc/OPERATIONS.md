# OPERATIONS

Date: 2026-03-01

## Canonical Commands
- Launch app: `python src/app/main.py`
- Run tests: `pytest -q`
- Packaging: `powershell -ExecutionPolicy Bypass -File .\tools\package_windows.ps1`

## Daily Execution Rules
- Work on feature branches only (`feature/roadmap-*` or `feature/fix-*`).
- One task/fix per branch, one commit, then merge to `main`.
- Do not merge to `stable` during active implementation.
- If gates fail, do not merge; log blocker in `Doc/CURRENT_STATE.md` and `Doc/DAILY_REPORT.md`.

## Mandatory Gate (Before Merge)
1. `python src/app/main.py` (launch smoke, no crash).
2. `pytest -q` (green).
3. Task-specific manual smoke as needed:
- Viewport tasks: `Debug -> Create Test Voxels (Cross)`, orbit/zoom/pan.
- IO tasks: Save/Open roundtrip.
- Export tasks: export once and verify file exists.

## Operator Validation Checklist
1. Verify `main` clean and green.
2. Run full manual validation:
- Viewport/navigation profiles + precision mode.
- Tooling (brush/box/line/fill/mirror/selection).
- Scene operations (parts/groups/bulk actions).
- Palette operations.
- Save/Open + recovery/open-recent paths.
- Export OBJ/glTF/VOX/QB.
3. Run packaging script and capture artifact diagnostics.
4. Record outcomes in `Doc/DAILY_REPORT.md`.
5. Only after sign-off, promote `main` to `stable`.

## Publishing Notes
- If local `main` is ahead of `origin/main`, push when connectivity/auth is available.
- Keep `stable` untouched until operator sign-off completes.

## PRE-STABLE QA GATE (QUBICLE STANDARD)
Use this exact checklist before promoting `main` to `stable`.

1. Viewport visibility modes
- Action: Launch app, create test voxels, trigger `Voxels -> Solidify/Rebuild Mesh`.
- Expected: voxel points and wire cubes remain visible; solid mesh surface is visibly rendered for solidified parts.

2. Camera controls + precision + reset/frame
- Action: Orbit/pan/zoom in `Classic`, `MMB Orbit`, and `Blender-Mix`; hold `Alt` while moving camera; run `Shift+R` and `Shift+F`.
- Expected: camera moves in all profiles; `Alt` reduces sensitivity; reset/frame work deterministically.

3. Brush paint/erase across XY/YZ/XZ
- Action: Set edit plane to `XY`, `YZ`, `XZ`; paint and erase with brush.
- Expected: edits apply on selected plane, undoable, and visible immediately.

4. Line/box/fill correctness + preview ghosting
- Action: Use line/box/fill tools on occupied and empty areas.
- Expected: hover/drag previews match final applied cells; fill respects limits and connectivity mode.

5. Mirror/symmetry behavior
- Action: Enable X/Y/Z mirror (with offsets) and paint/erase.
- Expected: mirrored cells appear correctly; mirror guide overlays reflect active axes/offsets.

6. Parts workflow
- Action: Create/rename/duplicate/delete/reorder parts; assign groups; toggle lock/visibility; edit transforms.
- Expected: all actions update scene and inspector state without crashes/regressions.

7. Palette editing + hotkeys + persistence
- Action: Edit palette slots, switch with `1..0`, save/open project.
- Expected: slot edits persist, hotkeys select active slot, locked slots remain protected.

8. Project save/open compatibility sanity
- Action: Save project, reopen, validate tool/editor state restoration.
- Expected: no schema crash; compatible state restored with clear error on unsupported schema.

9. Import (VOX) correctness + palette fidelity
- Action: Import VOX sample(s), including multi-model file where possible.
- Expected: parts are created and named/grouped correctly, transforms (supported subset) apply, colors map correctly.

10. Solidify workflow (critical)
- Action: Rebuild mesh for active part, inspect viewport, then export mesh.
- Expected: visible solid surface exists (not wire-only), mesh is exportable, and export geometry aligns with viewport.

11. Export workflows: OBJ + glTF
- Action: Export OBJ and glTF with scale preset options.
- Expected: files are generated and non-empty; basic structure sanity (positions, normals, materials/colors) is valid.

12. Undo/redo depth + hotkey overlay
- Action: Set undo depth, perform edits, run undo/redo chain, open shortcut overlay.
- Expected: undo stack obeys configured depth; overlay opens/closes quickly and lists active hotkeys.

13. Startup recovery UX
- Action: Trigger autosave snapshot scenario and relaunch.
- Expected: startup prompt supports restore/discard/open recent/cancel with safe behavior.

14. Packaging diagnostics
- Action: Run `powershell -ExecutionPolicy Bypass -File .\\tools\\package_windows.ps1`.
- Expected: packaging completes with artifact path, size, and SHA256 diagnostics.
