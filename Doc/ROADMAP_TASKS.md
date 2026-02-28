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
- Commit: `COMMIT_HASH_PENDING`
- Added scene-level duplicate and delete operations with active-part reassignment and guard against deleting the last part.
- Added inspector UI actions for duplicate/delete part and status feedback messages in main window.
- Added tests for duplicate copy behavior, active-part switching after delete, and minimum-part guard.

## Remaining Tasks

## Task 04: Part Visibility/Lock Flags
- Goal: add minimum scene control parity with expected voxel editor workflow.
- Files/modules likely touched:
  - `src/core/part.py`
  - `src/app/ui/panels/inspector_panel.py`
  - `src/app/viewport/gl_widget.py`
- Acceptance criteria:
  - Hidden parts do not render.
  - Locked parts do not accept edits.
- Tests required:
  - Core tests for lock/visible behavior.

## Task 05: Shortcut Map v1
- Goal: establish productivity keybindings for core tools and camera actions.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/app/ui/panels/tools_panel.py`
- Acceptance criteria:
  - Hotkeys switch Brush/Box/Line/Fill and Paint/Erase.
  - Hotkeys for frame/reset camera work reliably.
- Tests required:
  - Manual shortcut smoke list in docs.

## Task 06: Undo Transaction Grouping for Drag Tools
- Goal: ensure all drag operations remain one undo step under all conditions.
- Files/modules likely touched:
  - `src/core/commands/command_stack.py`
  - `src/core/commands/demo_commands.py`
- Acceptance criteria:
  - Box/Line/Fill remain single-step undo with mirrors enabled.
- Tests required:
  - Unit tests covering grouped operations and mirror combinations.

## Task 07: Mirror Plane Visual Gizmos
- Goal: improve mirror discoverability and confidence.
- Files/modules likely touched:
  - `src/app/viewport/gl_widget.py`
  - `src/app/ui/panels/tools_panel.py`
- Acceptance criteria:
  - Active mirror axes are visible in viewport.
  - Mirror toggles clearly map to rendered guides.
- Tests required:
  - Manual visual verification.

## Task 08: Custom Mirror Plane Offsets
- Goal: move beyond origin-only symmetry.
- Files/modules likely touched:
  - `src/app/app_context.py`
  - `src/core/commands/demo_commands.py`
  - `src/app/ui/panels/tools_panel.py`
- Acceptance criteria:
  - User can set per-axis mirror offset.
  - Mirrored edits honor configured planes.
- Tests required:
  - Unit tests for mirrored coordinate generation with offsets.
- Stop if risky:
  - Stop if offset logic destabilizes existing mirror behavior.

## Task 09: Export Options Panel v1 (OBJ/glTF/VOX)
- Goal: expose practical export controls in UI.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/core/export/obj_exporter.py`
  - `src/core/export/gltf_exporter.py`
- Acceptance criteria:
  - User can choose basic options (greedy/triangulate for OBJ, scale preset placeholder).
  - Export commands persist last-used options in session.
- Tests required:
  - Export smoke tests for option permutations.

## Task 10: VOX Export Compatibility Validation Pass
- Goal: harden `.vox` interoperability with common voxel tools.
- Files/modules likely touched:
  - `src/core/export/vox_exporter.py`
  - `tests/test_vox_exporter.py`
- Acceptance criteria:
  - Exported `.vox` opens in at least one external voxel editor without corruption.
  - Palette index mapping remains stable for current palette set.
- Tests required:
  - Unit tests + manual external import check.

## Task 11: Palette Management v1 (Save/Load Presets)
- Goal: improve color workflow parity.
- Files/modules likely touched:
  - `src/app/ui/panels/palette_panel.py`
  - `src/core/palette.py`
  - `src/core/io/`
- Acceptance criteria:
  - User can save and load palette presets from disk.
  - Active color remains valid after palette changes.
- Tests required:
  - Serialization tests for palette preset roundtrip.

## Task 12: Brush Stroke Drag Paint (Continuous)
- Goal: move from click-only brush to continuous drag painting.
- Files/modules likely touched:
  - `src/app/viewport/gl_widget.py`
  - `src/core/commands/demo_commands.py`
- Acceptance criteria:
  - Dragging paints contiguous voxels.
  - Undo reverts one stroke transaction.
- Tests required:
  - Command tests for stroke cell set + undo behavior.

## Task 13: Fill Tool Constraints + Safety Guards
- Goal: prevent accidental heavy fill operations in large regions.
- Files/modules likely touched:
  - `src/core/commands/demo_commands.py`
  - `src/app/ui/main_window.py`
- Acceptance criteria:
  - Fill operation has bounded safety threshold with user feedback.
  - No UI freeze on large connected regions.
- Tests required:
  - Unit tests for threshold behavior.

## Task 14: Solidify UI Action + Mesh Cache Refresh
- Goal: expose explicit “Solidify/Rebuild Mesh” control.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/core/meshing/solidify.py`
  - `src/core/part.py`
- Acceptance criteria:
  - User can trigger mesh rebuild from active part.
  - Stats/export consume refreshed mesh buffers consistently.
- Tests required:
  - Core integration tests for rebuild-triggered mesh updates.

## Task 15: Bounds + Unit-Aware Stats Display
- Goal: improve scene/object analysis usefulness for production constraints.
- Files/modules likely touched:
  - `src/core/analysis/stats.py`
  - `src/app/ui/panels/stats_panel.py`
- Acceptance criteria:
  - Stats panel shows per-part bounds in editor units clearly.
  - Scene totals remain accurate with multi-part scenes.
- Tests required:
  - Unit tests for bounds and totals.

## Task 16: Save/Open Workflow Hardening
- Goal: reduce data-loss risk and improve reliability.
- Files/modules likely touched:
  - `src/core/io/project_io.py`
  - `src/app/ui/main_window.py`
- Acceptance criteria:
  - Save/open roundtrip preserves parts, active part, tool state essentials.
  - User gets clear error message for invalid/corrupt files.
- Tests required:
  - IO regression tests + legacy-compat tests.

## Task 17: Performance Baseline Harness (Voxel Operations)
- Goal: establish measurable perf baseline for Phase 1.
- Files/modules likely touched:
  - `tests/`
  - `src/core/commands/demo_commands.py`
  - `src/core/meshing/`
- Acceptance criteria:
  - Automated benchmark-style test script records brush/fill/solidify timings.
  - Baseline stored for regression tracking.
- Tests required:
  - Perf harness execution (non-blocking threshold assertions).

## Task 18: Clean-Machine Packaging Validation
- Goal: verify packaging reproducibility and startup reliability.
- Files/modules likely touched:
  - `tools/package_windows.ps1`
  - `tools/build_pyinstaller.spec`
  - `Doc/PACKAGING_CHECKLIST.md`
- Acceptance criteria:
  - Fresh environment can build and launch packaged app.
  - Checklist updated with any required environment notes.
- Tests required:
  - Manual packaging checklist.
- Stop if risky:
  - Stop merge if packaged app launch fails on validation machine.

## Task 19: In-App Quick Help / Status Hints
- Goal: improve discoverability for new users.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/app/ui/panels/tools_panel.py`
- Acceptance criteria:
  - Status hints explain selected tool behavior and modifiers.
  - First-use workflow guidance visible without opening docs.
- Tests required:
  - Manual UX smoke.

## Task 20: Phase 1 QA Gate + Bugfix Buffer
- Goal: run full Phase 1 smoke suite and close top blockers before Phase 2 planning.
- Files/modules likely touched:
  - `Doc/DAILY_REPORT.md`
  - targeted bugfix files from QA
- Acceptance criteria:
  - Full smoke checklist passes (run, edit, save/open, export OBJ/glTF/VOX, packaging smoke).
  - Remaining issues ranked with go/no-go recommendation for Phase 2.
- Tests required:
  - `pytest -q` and manual end-to-end checklist.
