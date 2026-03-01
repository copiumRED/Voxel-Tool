# ROADMAP_TASKS (Next Workday Board)

Date: 2026-02-28  
Scope: Next full workday run, tasks 01-20 only.  
Driver: `Doc/QUBICLE_GAP_ANALYSIS.md` P0/P1 gaps.  
Rule: One task = one branch = one merge commit to `main` after all gates pass.

## Completed Today

### Task 01: Brush Size + Shape Controls v1
- Commit: `COMMIT_PENDING`
- Added brush profile state in `AppContext` (`brush_size` 1-3 and `brush_shape` cube/sphere) with validation setters.
- Updated paint/erase commands to apply configurable brush footprints while preserving mirrored edit behavior.
- Added Tools panel controls for brush size/shape and viewport hover preview rendering for multi-cell brush footprints.

### Task 02: Non-Brush Hover Ghosting (Line/Box/Fill)
- Commit: `COMMIT_PENDING`
- Added shared line/box cell-generation helpers used by both command execution and preview rendering to keep preview-to-apply parity.
- Added viewport drag ghost previews for line and box tools, including mirror-aware preview cell expansion.
- Added fill hover target preview and tests validating preview-generation helper outputs for line/box paths.

### Task 03: Pick Mode Toggle (Surface vs Plane Lock)
- Commit: `COMMIT_PENDING`
- Added pick mode state to `AppContext` with explicit `surface` vs `plane_lock` validation and persisted editor-state support.
- Added Tools panel pick mode selector (brush workflow) with status updates and quick-help hint integration.
- Updated brush targeting so surface mode disables plane fallback while plane-lock mode preserves empty-scene placement behavior.

### Task 04: Part Transform Controls (Position/Rotation/Scale)
- Commit: `COMMIT_PENDING`
- Added transform fields (`position`, `rotation`, `scale`) to part model plus project IO save/load support.
- Added Inspector transform controls (Pos/Rot/Scale) with immediate active-part updates and status messaging.
- Updated viewport rendering/frame logic to apply per-part transforms so transform edits are visible immediately.

### Task 05: Part Reorder in Inspector + Persistence
- Commit: `COMMIT_PENDING`
- Added explicit `Scene.part_order` with move-up/move-down support and ordered iteration helpers.
- Added Inspector `Move Up`/`Move Down` actions for part list reordering with immediate list refresh.
- Updated project IO to persist/load part order and added tests for scene reorder behavior and IO roundtrip order stability.

### Task 06: Grouping v1 (Create Group, Add/Remove Parts, Group Visibility/Lock)
- Commit: `COMMIT_PENDING`
- Added lightweight `PartGroup` model with ordered group storage and scene APIs for create/delete/assign/unassign operations.
- Added group visibility/lock propagation so group toggles update member part visibility/lock flags.
- Added Inspector group controls and project IO persistence with regression tests for group membership/state roundtrip.

### Task 07: Palette Editing v1 (Add/Remove/Edit/Swap Colors)
- Commit: `COMMIT_PENDING`
- Added palette helper APIs for add/remove/swap color operations with validation.
- Added Palette panel editing controls for RGB channel editing, add/remove color, and adjacent swap actions.
- Updated swatch UI to rebuild dynamically with palette size changes and added helper regression tests.

### Task 08: Palette Quick Hotkeys (1-0)
- Commit: `COMMIT_PENDING`
- Added numeric shortcut bindings (`1-0`) for direct active-color slot selection.
- Added active color setter path in main window to clamp to palette bounds and refresh UI consistently.
- Wired status updates so hotkey-driven color changes are visible immediately in the status bar.

### Task 09: Camera View Presets (Top/Front/Left/Right/Back/Bottom)
- Commit: `COMMIT_PENDING`
- Added viewport camera preset API for top/front/left/right/back/bottom orientations.
- Added View menu preset actions with shortcuts (`Ctrl+1` to `Ctrl+6`).
- Added status feedback for preset switches while preserving existing orbit/zoom/pan interaction.

### Task 10: Grid Controls + Camera Snap Settings
- Commit: `COMMIT_PENDING`
- Added View menu controls for grid visibility toggle and adjustable grid spacing.
- Added camera snap toggle and snap-angle setting with state applied during orbit interaction.
- Added editor-state persistence for grid/snap settings so values survive save/open workflows.

### Task 11: VOX Import v1 (Single-Part Path)
- Commit: `COMMIT_PENDING`
- Added VOX file loader support for `SIZE`/`XYZI`/`RGBA` chunk parsing and palette extraction.
- Added `File -> Import VOX` flow that creates a new part from imported voxels and activates it.
- Added importer roundtrip test coverage using exported VOX fixtures.

### Task 12: VOX Import v2 (Multi-Model Mapping + Palette Fidelity)
- Commit: `COMMIT_PENDING`
- Added multi-model VOX parser path that reads repeated model chunks into separate voxel grids.
- Updated `File -> Import VOX` workflow to create one part per imported model with deterministic naming.
- Added multi-model parser regression test validating per-model voxel data and RGBA palette fidelity.

### Task 13: Qubicle `.qb` Feasibility Note + Guardrail
- Commit: `COMMIT_PENDING`
- Added explicit `.qb` feasibility decision note in `Doc/QUBICLE_GAP_ANALYSIS.md`.
- Documented go/no-go criteria and required fixture matrix before `.qb` implementation can begin.
- Added scope guardrail to prevent premature `.qb` parser work in current phase.

### Task 14: OBJ Export Quality Pass (Scale/Pivot/Material Strategy)
- Commit: `COMMIT_PENDING`
- Expanded OBJ export options to apply scale factor and pivot mode transformations at write time.
- Added MTL material file emission (`voxel_default`) with OBJ `mtllib`/`usemtl` references.
- Wired export dialog options so OBJ scale preset and pivot mode flow into exporter behavior with test coverage.

## Remaining Tasks

### Task 15: Mesh Normals Validation + Fixups
- Goal:
  - Ensure generated meshes have correct winding and consistent normals.
- Files/modules likely touched:
  - `src/core/meshing/surface_extractor.py`
  - `src/core/meshing/greedy_mesher.py`
  - `src/core/meshing/mesh.py`
- Acceptance criteria (human-testable):
  - No inverted normals on canonical test shapes.
  - External viewer shading appears correct without manual recalc.
- Tests required:
  - Normals/winding unit tests on fixtures.
  - Export/import shading smoke test.

### Task 16: Basic UV Projection + Vertex Color Export Path
- Goal:
  - Add basic UV coordinates and preserve color path as defined in spec scope.
- Files/modules likely touched:
  - `src/core/meshing/*`
  - `src/core/export/obj_exporter.py`
  - `src/core/export/gltf_exporter.py`
- Acceptance criteria (human-testable):
  - Exported mesh contains UVs for basic projection workflow.
  - Vertex color path remains intact for supported exporter targets.
- Tests required:
  - UV buffer generation tests.
  - Export structure tests for UV/color presence.
- Risk/rollback note:
  - If UV generation introduces topology bugs, ship UV-disabled fallback toggle and keep color path stable.

### Task 17: Incremental Solidify Rebuild (Dirty Region v1)
- Goal:
  - Reduce rebuild cost by processing changed regions only.
- Files/modules likely touched:
  - `src/core/meshing/solidify.py`
  - `src/core/commands/demo_commands.py`
  - `src/core/part.py`
- Acceptance criteria (human-testable):
  - Localized edits trigger faster rebuild than full-scene baseline.
  - Mesh output remains functionally identical to full rebuild on test fixtures.
- Tests required:
  - Perf regression tests against stored baseline.
  - Equivalence tests full-rebuild vs incremental-rebuild.

### Task 18: Runtime Performance Diagnostics in Stats Panel
- Goal:
  - Surface live runtime metrics for frame and mesh performance.
- Files/modules likely touched:
  - `src/app/ui/panels/stats_panel.py`
  - `src/app/viewport/gl_widget.py`
  - `src/core/analysis/stats.py`
- Acceptance criteria (human-testable):
  - Stats panel shows frame time, voxel count, triangle count, rebuild timing.
  - Metrics update during editing without UI freeze.
- Tests required:
  - Stats formatting tests.
  - Manual stress-scene metrics smoke.

### Task 19: Autosave + Crash Recovery v1
- Goal:
  - Add periodic autosave and startup recovery prompt.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/core/io/project_io.py`
  - `src/app/settings.py`
- Acceptance criteria (human-testable):
  - Autosave file updates on configured interval.
  - Forced-close session prompts recovery on next launch.
  - Recovery restore opens without corruption.
- Tests required:
  - Autosave write/load tests.
  - Recovery flow tests for interrupted session.
- Risk/rollback note:
  - If autosave causes IO contention, increase interval and gate writes to idle periods.

### Task 20: Shortcut/Undo Depth Preferences + Day-End QA Gate
- Goal:
  - Finalize usability controls and run full gate before operator handoff.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/core/commands/command_stack.py`
  - `src/app/settings.py`
  - `Doc/DAILY_REPORT.md`
- Acceptance criteria (human-testable):
  - Undo depth preference is configurable and applied.
  - Shortcut map additions are discoverable in UI/help.
  - Full gate passes: launch, `pytest -q`, save/open, export OBJ/VOX, viewport interaction.
- Tests required:
  - Command stack cap tests.
  - End-to-end smoke checklist execution.
