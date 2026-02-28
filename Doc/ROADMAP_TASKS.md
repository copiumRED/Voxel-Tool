# ROADMAP_TASKS (Next Workday Roadmap)

This roadmap is optimized for Phase 1 execution (Voxel MVP + Qubicle-like usability), with each task sized for one atomic 1-2-3-4 cycle.

## Completed Today

### Task 01: Viewport Health Overlay + Startup Diagnostics
- Commit: `3e9e38a`
- Added explicit viewport diagnostics status messaging (`READY`/`UNAVAILABLE`) including shader profile and OpenGL info in startup/status bar flow.
- Ensured viewport pipeline failures always display clear in-viewport error text, even when debug overlay is toggled off.
- Verified startup smoke and full automated tests (`pytest -q`) remained green.

### Task 02: First-Voxel UX Preview (Hover Cell/Face)
- Commit: `665f469`
- Added brush-mode hover preview marker with clear paint/erase coloring, rendered directly in the viewport.
- Implemented reusable brush target resolution helper with plane fallback support for empty-scene preview.
- Added core math tests for hover target resolution paths and validated full test suite pass.

### Task 03: Part Actions v1 (Delete/Duplicate)
- Commit: `c312b52`
- Added scene-level duplicate and delete operations with active-part reassignment and guard against deleting the last part.
- Added inspector UI actions for duplicate/delete part and status feedback messages in main window.
- Added tests for duplicate copy behavior, active-part switching after delete, and minimum-part guard.

### Task 04: Part Visibility/Lock Flags
- Commit: `9fda1e3`
- Added per-part `visible` and `locked` flags in the core model and persisted them through project save/load.
- Added Inspector visibility/lock toggles and viewport lock guard to block edits on locked active part.
- Updated viewport drawing/camera framing to use only visible parts and added tests for visibility filtering and flag persistence.

### Task 05: Shortcut Map v1
- Commit: `eb5941c`
- Added keyboard hotkeys for tool shape switching (Brush/Box/Line/Fill) and mode switching (Paint/Erase).
- Added camera hotkeys for frame/reset (`Shift+F` / `Shift+R`) with matching View menu shortcuts.
- Wired shortcuts through tools panel state setters to keep UI and context behavior synchronized.

### Task 06: Undo Transaction Grouping for Drag Tools
- Commit: `1455599`
- Added command-stack transaction support (`begin_transaction` / `end_transaction`) with compound undo/redo behavior.
- Added tests verifying multi-command transactions collapse to one undo step.
- Added mirror-enabled drag-tool tests asserting Box/Line/Fill remain single-step undo operations.

### Task 07: Mirror Plane Visual Gizmos
- Commit: `8cb5943`
- Added viewport-rendered mirror plane guide gizmos for active X/Y/Z mirror toggles.
- Added color-coded guide planes so mirror axes are visible and distinguishable during editing.
- Updated tools panel mirror toggle labels to `Mirror X/Y/Z` for clearer control-to-guide mapping.

### Task 08: Custom Mirror Plane Offsets
- Commit: `aeb9bea`
- Added per-axis mirror offset configuration in app context (`mirror_x/y/z_offset`) and offset-aware mirrored coordinate expansion.
- Added Tools panel per-axis offset controls and status messaging when offsets change.
- Added tests verifying mirrored coordinate generation and paint commands honor configured mirror plane offsets.

### Task 09: Export Options Panel v1 (OBJ/glTF/VOX)
- Commit: `59aa157`
- Added export options dialog flow with session-persisted options across export actions.
- Added OBJ options wiring for greedy meshing and triangulation controls.
- Added scale preset placeholder option surfaced for OBJ/glTF/VOX and persisted during the session.

### Task 10: VOX Export Compatibility Validation Pass
- Commit: `aaa8935`
- Hardened VOX exporter validation with deterministic palette-index mapping helper and expanded binary structure tests.
- Confirmed manual interoperability by importing exported `.vox` into Qubicle without corruption.
- Verified palette index mapping stability for current palette set with automated test coverage.

### Task 11: Palette Management v1 (Save/Load Presets)
- Commit: `9c600c5`
- Added palette preset save/load IO helpers with schema validation and roundtrip support.
- Added Palette panel Save/Load preset actions and status feedback in the main window.
- Ensured active color index is clamped after palette load and covered by automated tests.

### Task 12: Brush Stroke Drag Paint (Continuous)
- Commit: `4b38dc3`
- Added continuous brush stroke painting across drag movement with contiguous segment rasterization.
- Grouped each brush stroke into a single command transaction so one undo reverts the full stroke.
- Added command tests for stroke segment rasterization and single-step undo behavior.

### Task 13: Fill Tool Constraints + Safety Guards
- Commit: `8c7d5f8`
- Added bounded fill threshold (`fill_max_cells`) to prevent oversized fill operations from freezing interaction.
- Added explicit fill abort signaling and user-visible status feedback when threshold is exceeded.
- Added unit test coverage for threshold-blocked fill behavior.

### Task 14: Solidify UI Action + Mesh Cache Refresh
- Commit: `2813f10`
- Added explicit `Voxels -> Solidify/Rebuild Mesh` action that rebuilds and caches the active part mesh.
- Added per-part mesh cache plumbing and cache invalidation on voxel edits.
- Updated stats/export paths to consume refreshed mesh buffers consistently when cache is present.

### Task 15: Bounds + Unit-Aware Stats Display
- Commit: `c6b8353`
- Added unit-aware part bounds metrics (`bounds_meters`) in analysis stats output.
- Updated stats panel object display to show both voxel bounds and metric bounds (`m`) clearly.
- Extended stats tests to assert bounds values remain accurate in both voxel and meter units.

### Task 16: Save/Open Workflow Hardening
- Commit: `f630b18`
- Added editor-state persistence in project IO for key tool/mirror/session fields.
- Added editor-state restoration on open and save-time capture in main window.
- Added clear user error dialog for invalid/corrupt project files and IO tests for new schema behavior.

### Task 17: Performance Baseline Harness (Voxel Operations)
- Commit: `5bffb80`
- Added automated performance harness test for brush paint, fill, and solidify timings.
- Added stored baseline file (`tests/perf_baseline.json`) for regression tracking.
- Added non-blocking threshold assertions via configurable multiplier to flag major regressions without overfitting local variance.

### Task 18: Clean-Machine Packaging Validation
- Commit: `20c71cf`
- Hardened packaging scripts/spec path resolution and fail-fast behavior for reproducible execution.
- Validated packaging build completion and packaged EXE launch smoke in this environment.
- Updated `Doc/PACKAGING_CHECKLIST.md` with concrete run notes and expectations.

### Task 19: In-App Quick Help / Status Hints
- Commit: `4d745d1`
- Added in-panel tool behavior hints including modifier guidance for active tool mode/shape.
- Added first-use workflow guidance directly in Tools panel (no external docs required).
- Added shortcut reminder line in the same visible hint block for onboarding/discoverability.

### Task 20: Phase 1 QA Gate + Bugfix Buffer
- Commit: `COMMIT_HASH_PENDING`
- Ran Phase 1 QA gate checks: app launch smoke, full test suite, project save/open smoke, and OBJ/glTF/VOX export smoke.
- Verified packaged app launch smoke (`dist\\VoxelTool\\VoxelTool.exe`) and confirmed packaging pipeline remains runnable.
- Consolidated go/no-go readiness notes for operator human validation handoff.

## Remaining Tasks
- None.
