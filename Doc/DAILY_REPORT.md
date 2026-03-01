# DAILY_REPORT

Date: 2026-03-01
Scope: consolidated report for completed 40-task cycle.

## Cycle Outcome
- Completed tasks: 01-40 (all merged to `main`).
- Final gates on `main`:
  - `python src/app/main.py`: PASS
  - `pytest -q`: PASS (`183 passed`)
- Stable branch policy: unchanged (no day-time merge to `stable`).

## What Was Delivered
- Core editing parity improvements: selection workflows, mirror overlays, fill confidence preview.
- Viewport/control improvements: MMB/Blender-mix nav profiles, precision mode, HUD badges.
- Scene workflow improvements: multi-select part actions, filtering, grouping upgrades.
- Export/interop improvements: glTF UV/COLOR/material baseline, VOX transform mapping v1, QB feasibility import/export.
- Reliability/perf improvements: transaction abort hardening, schema handshake, incremental telemetry, dense stress tiers, memory instrumentation.
- UX polish: top quick toolbar, command palette, dock presets, theme/contrast pass, startup recovery UX.

## Operator Validation Pack
- Follow [OPERATIONS.md](./OPERATIONS.md) for full validation, packaging, and publishing procedures.

## Open Risks (Post-Cycle)
1. Mesh edit mode (vertex/edge/face editing) remains out of scope.
2. FBX exporter remains unimplemented.
3. VOX hierarchy reconstruction beyond transform mapping v1 is partial.
4. Packaging confidence still needs clean-machine confirmation.

## Archive Note
- Historical day logs were intentionally condensed to keep documentation maintainable.
- Source of truth for detailed change history remains git log + commit diffs.

## Pre-stable QA Run Report
Date/Time:
- 2026-03-01 08:27:19 +02:00

Environment:
- OS: Windows 11 (per packaging/runtime logs)
- Python: 3.14.3
- Branch: `feature/qa-hardening-pre-stable`

Test results summary:
- App launch smoke: PASS (`python src/app/main.py`)
- Full automated suite: PASS (`pytest -q` -> `185 passed`)
- Targeted IO/export/recovery suite: PASS (`36 passed`)
- Packaging diagnostics: PASS (`tools/package_windows.ps1`)
  - `ARTIFACT_EXE=C:\\Users\\Rampu\\OneDrive\\Documents\\Github Repos\\Voxel Tool\\dist\\VoxelTool\\VoxelTool.exe`
  - `ARTIFACT_SIZE_BYTES=2418943`
  - `ARTIFACT_SHA256=d723565f7a51ba48543ee244860b65b291841276b1639744bc976eff6a904c87`

Bugs found:
- QA-001 (P0): Solidify output not visible in viewport (wire/points only).
  - Repro:
    1. Launch app and create voxels.
    2. Trigger `Voxels -> Solidify/Rebuild Mesh`.
    3. Observe viewport remains wire/point visualization only.
  - Expected: visible solid mesh surface appears after solidify.
  - Actual: no solid mesh triangles rendered.
  - Root cause: viewport render path drew only voxel points/line cubes; `part.mesh_cache` triangles were never submitted.

Fixes applied:
- Added solid mesh triangle rendering from `part.mesh_cache` in viewport draw loop.
- Added palette-aware color mapping for viewport voxel/mesh rendering (uses active project palette values).
- Added regression tests:
  - `test_mesh_triangles_from_surface_emits_two_triangles_per_quad`
  - `test_palette_color_rgb_uses_context_palette_values`
- Commit notes:
  - include viewport mesh visibility fix + regression tests in this QA branch commit.

Remaining issues:
- No remaining P0/P1 blocker found for pre-stable promotion baseline.
- Non-blocking backlog remains (mesh edit mode, FBX export, full VOX hierarchy semantics).
