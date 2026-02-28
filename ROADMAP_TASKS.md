# ROADMAP_TASKS

This roadmap is sequenced for atomic 1234 cycles (one feature per cycle), aligned to `PROJECT_SPEC.md` and current codebase state.

## Task 1: Viewport Visibility Lockdown (Milestone: reliable visible voxels)
- Goal: make voxel rendering unmistakably visible across target Windows GPUs.
- Files/modules likely touched:
  - `src/app/viewport/gl_widget.py`
  - `src/app/ui/main_window.py` (status/debug action hooks only)
- Acceptance criteria:
  - On launch, viewport clearly shows grid/axes/text.
  - `Debug -> Create Test Voxels (Cross)` always produces clearly visible voxels.
  - `View -> Frame Voxels` centers and shows test voxels on first try.
- Tests required:
  - Core-only: none mandatory.
  - Manual checklist document for operator reproducibility.

## Task 2: Multi-Part Scene Core (Project + Scene milestone)
- Goal: introduce `Scene` + `Part` model (single selected part minimum) and move voxel authority under parts.
- Files/modules likely touched:
  - `src/core/scene.py` (new)
  - `src/core/part.py` (new)
  - `src/core/project.py`
  - `src/app/app_context.py`
- Acceptance criteria:
  - New project creates default scene with one part.
  - Active part can be resolved in UI and used by existing voxel commands.
- Tests required:
  - Unit tests for scene/part creation and selected-part behavior.

## Task 3: Scene/Part Persistence in Project IO
- Goal: persist scene + parts in project JSON (minimal schema evolution).
- Files/modules likely touched:
  - `src/core/io/project_io.py`
  - `src/core/project.py`
  - `tests/test_project_io.py`
- Acceptance criteria:
  - Save/open roundtrip preserves part list and active part voxel data.
- Tests required:
  - IO roundtrip tests including legacy compatibility paths.

## Task 4: Part List UI (Basic Object Management)
- Goal: add basic part list panel actions: add part, rename, select active part.
- Files/modules likely touched:
  - `src/app/ui/panels/inspector_panel.py` or new part list panel module
  - `src/app/ui/main_window.py`
- Acceptance criteria:
  - User can create/select parts and paint affects selected part only.
- Tests required:
  - Core tests for selection switching effects (no Qt test required).

## Task 5: Plane Tools v1 - Brush Paint/Erase (Stabilization)
- Goal: formalize current click paint/erase into tool-mode brush behavior with explicit mode state.
- Files/modules likely touched:
  - `src/app/app_context.py` (tool mode state)
  - `src/app/viewport/gl_widget.py`
  - `src/core/commands/demo_commands.py` (rename/generalize)
- Acceptance criteria:
  - Brush paint and erase operate predictably on active plane.
  - Undo/redo works per stroke click.
- Tests required:
  - Command tests for paint/erase overwrite semantics.

## Task 6: Plane Tools v1 - Box Fill/Box Erase
- Goal: add drag-rectangle box fill/erase on `z=0` as next tool increment.
- Files/modules likely touched:
  - `src/app/viewport/gl_widget.py`
  - `src/core/commands/` (new box commands)
  - `src/app/ui/panels/tools_panel.py`
- Acceptance criteria:
  - Drag box paints or erases expected cells on plane.
  - Single undo reverts one box operation.
- Tests required:
  - Command tests for filled cell counts and undo/redo.

## Task 7: Plane Tools v1 - Line Tool
- Goal: add line paint tool on plane using integer grid rasterization.
- Files/modules likely touched:
  - `src/core/commands/` (line command)
  - `src/app/viewport/gl_widget.py`
  - `src/app/ui/panels/tools_panel.py`
- Acceptance criteria:
  - Click-drag line paints contiguous grid line on plane.
- Tests required:
  - Unit test for known start/end line voxel sets.

## Task 8: Plane Tools v1 - Flood Fill (bounded)
- Goal: add fill on contiguous same-color region for current plane.
- Files/modules likely touched:
  - `src/core/commands/` (fill command)
  - `src/core/voxels/voxel_grid.py` (neighbor helpers if needed)
- Acceptance criteria:
  - Fill replaces connected region; undo restores prior state.
- Tests required:
  - Unit tests for fill boundaries and undo/redo.

## Task 9: Mirror Modes (X/Y/Z) for Voxel Tools
- Goal: add mirror toggles and mirrored writes for paint/erase/box/line/fill.
- Files/modules likely touched:
  - `src/app/app_context.py` (mirror flags)
  - `src/core/commands/` (mirror-aware command generation)
  - `src/app/ui/panels/tools_panel.py`
- Acceptance criteria:
  - Toggling axes mirrors edits as expected.
- Tests required:
  - Unit tests for mirrored coordinate generation.

## Task 10: Full 3D Picking v1 (replace plane-only painting)
- Goal: raycast against voxel surface candidates (or near-cell volume) for true 3D paint/erase.
- Files/modules likely touched:
  - `src/app/viewport/gl_widget.py`
  - `src/core/voxels/voxel_grid.py` (query helpers)
- Acceptance criteria:
  - Clicking visible voxel faces paints adjacent cell/erases selected cell in 3D.
- Tests required:
  - Core math tests for ray-cell intersection helpers.

## Task 11: Solidify v1 - Surface Extraction Mesh
- Goal: produce explicit mesh from voxel surface faces (already partially mirrored by OBJ culling, now reusable mesh buffers).
- Files/modules likely touched:
  - `src/core/meshing/surface_extractor.py` (new under active tree)
  - `src/core/models` or new mesh struct module
- Acceptance criteria:
  - Build mesh buffers from current part voxels; face count matches culling logic.
- Tests required:
  - Unit tests for simple voxel configurations.

## Task 12: Solidify v1 - Greedy Meshing
- Goal: merge coplanar voxel faces to reduce polygons.
- Files/modules likely touched:
  - `src/core/meshing/greedy_mesher.py` (active tree implementation)
  - integration with solidify path
- Acceptance criteria:
  - Adjacent planar faces reduce compared to non-greedy extraction.
- Tests required:
  - Face count comparison tests (greedy < naive for known scenes).

## Task 13: Export Pipeline Expansion (OBJ settings + GLTF)
- Goal: keep OBJ path but add one additional format aligned to spec future recommendation (`glTF/GLB` preferred).
- Files/modules likely touched:
  - `src/core/export/obj_exporter.py`
  - `src/core/export/gltf_exporter.py` (new)
  - `src/app/ui/main_window.py` export actions/options
- Acceptance criteria:
  - User can export solidified mesh to OBJ and GLTF.
- Tests required:
  - Core exporter smoke tests for non-empty outputs and primitive counts.

## Task 14: Analysis Panel v1 (scene/object stats)
- Goal: surface per-object + scene totals (verts/faces/tris/bounds/material slots used placeholder).
- Files/modules likely touched:
  - `src/app/ui/panels/stats_panel.py`
  - `src/core/analysis/stats.py` (new)
- Acceptance criteria:
  - Stats panel updates live and after export/solidify.
- Tests required:
  - Unit tests for stat calculations.

## Task 15: Windows Packaging Milestone (Phase 0/1 boundary)
- Goal: produce repeatable Windows build artifact and run instructions.
- Files/modules likely touched:
  - `tools/build_pyinstaller.spec`
  - `run.ps1` / packaging scripts
  - `README.md`
- Acceptance criteria:
  - Clean machine can build and launch packaged `.exe`.
- Tests required:
  - Manual packaging checklist + startup smoke verification.
