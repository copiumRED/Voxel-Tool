# NEXT_WORKDAY

Date Prepared: 2026-03-01
Prepared By: Codex

## Workday Definition
- Complete `Doc/ROADMAP_TASKS.md` Tasks **01-40** in strict order.
- Tasks 01-30 are core stability/parity/perf/packaging delivery.
- Tasks 31-40 are interface polish delivery.
- One task per branch; merge only to `main` after gate pass.

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
1. Confirm all roadmap tasks completed in `Doc/ROADMAP_TASKS.md` with commit hashes.
2. Confirm `main` is clean and green:
- `python src/app/main.py`
- `pytest -q`
3. Validate viewport workflow:
- Create test voxels
- Orbit/pan/zoom across dense and sparse scenes
- Confirm edit-plane and pick-mode behavior is visible and predictable
4. Validate scene workflow:
- Add, duplicate, rename, reorder, hide/show, lock/unlock parts
- Group/ungroup parts and verify inspector reflects membership
5. Validate export workflow:
- Export OBJ/glTF/VOX on a multi-color, multi-part scene
- Verify files are created and non-empty
6. Validate recovery workflow:
- Perform edits, force-close, relaunch, validate recovery prompt path
7. Validate packaging workflow:
- Run packaging script and record artifact diagnostics
- Build portable zip and verify launch from extracted folder
8. Record outcomes in `Doc/DAILY_REPORT.md` and list any blocker with exact repro.
9. Only after sign-off: operator may promote `main` to `stable`.

## Day Objective
Deliver a production-credible voxel editor MVP in this cycle by resolving the highest-risk stability/correctness gaps first, then completing parity-critical workflows, then hardening performance and packaging, followed by focused interface polish for industry-standard daily use.
