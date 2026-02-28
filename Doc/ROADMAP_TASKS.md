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

## Remaining Tasks

### Task 02: Non-Brush Hover Ghosting (Line/Box/Fill)
- Goal:
  - Add live ghost preview for line, box, and fill tools before commit.
- Files/modules likely touched:
  - `src/app/viewport/gl_widget.py`
  - `src/app/ui/panels/tools_panel.py`
- Acceptance criteria (human-testable):
  - Hover/drag preview appears for line and box extents.
  - Fill hover target is clearly indicated.
  - Final operation matches previewed cells.
- Tests required:
  - Unit tests for preview target generation.
  - Manual viewport preview smoke on all tool modes.

### Task 03: Pick Mode Toggle (Surface vs Plane Lock)
- Goal:
  - Add explicit pick mode control for surface-only or plane-locked targeting.
- Files/modules likely touched:
  - `src/app/app_context.py`
  - `src/app/ui/panels/tools_panel.py`
  - `src/app/viewport/gl_widget.py`
- Acceptance criteria (human-testable):
  - Toggle is visible in Tools panel.
  - Surface mode edits only on detected voxel surfaces.
  - Plane-lock mode allows predictable empty-space editing.
- Tests required:
  - Raycast mode tests for both pick modes.
  - Manual test across empty and dense scene.

### Task 04: Part Transform Controls (Position/Rotation/Scale)
- Goal:
  - Introduce per-part transform editing in inspector.
- Files/modules likely touched:
  - `src/core/part.py`
  - `src/app/ui/panels/inspector_panel.py`
  - `src/app/viewport/gl_widget.py`
  - `src/core/io/project_io.py`
- Acceptance criteria (human-testable):
  - Active part transform fields are editable.
  - Viewport reflects transform changes immediately.
  - Save/open roundtrip restores transform values.
- Tests required:
  - IO tests for transform persistence.
  - Manual transform edit + save/open smoke.
- Risk/rollback note:
  - If transform wiring destabilizes render path, disable rotation/scale and keep translation-only for safe merge.

### Task 05: Part Reorder in Inspector + Persistence
- Goal:
  - Allow part list reordering and persist stable order.
- Files/modules likely touched:
  - `src/core/scene.py`
  - `src/app/ui/panels/inspector_panel.py`
  - `src/core/io/project_io.py`
- Acceptance criteria (human-testable):
  - User can move selected part up/down.
  - Reordered list persists after save/open.
- Tests required:
  - Scene ordering tests.
  - Project IO order roundtrip tests.

### Task 06: Grouping v1 (Create Group, Add/Remove Parts, Group Visibility/Lock)
- Goal:
  - Add lightweight part grouping for organization and batch control.
- Files/modules likely touched:
  - `src/core/scene.py`
  - `src/core/project.py`
  - `src/app/ui/panels/inspector_panel.py`
  - `src/core/io/project_io.py`
- Acceptance criteria (human-testable):
  - Create/delete groups from inspector.
  - Assign/unassign parts to groups.
  - Group visibility/lock affects member parts.
- Tests required:
  - Unit tests for group membership and flags.
  - Save/open tests for group persistence.
- Risk/rollback note:
  - If group model destabilizes existing part flows, merge group metadata first and defer UI actions.

### Task 07: Palette Editing v1 (Add/Remove/Edit/Swap Colors)
- Goal:
  - Enable in-app palette edits, not just preset load/save.
- Files/modules likely touched:
  - `src/app/ui/panels/palette_panel.py`
  - `src/core/palette.py`
  - `src/app/app_context.py`
- Acceptance criteria (human-testable):
  - User can add/remove/edit/swap palette colors.
  - Active color remains valid after edits.
- Tests required:
  - Palette normalization and clamping tests.
  - UI-level behavior tests for palette mutations.

### Task 08: Palette Quick Hotkeys (1-0)
- Goal:
  - Add numeric hotkeys for quick active-color selection.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/app/ui/panels/palette_panel.py`
- Acceptance criteria (human-testable):
  - Pressing `1-0` selects corresponding palette slots.
  - Status bar confirms active color change.
- Tests required:
  - Shortcut mapping tests.
  - Manual quick-switch paint smoke.

### Task 09: Camera View Presets (Top/Front/Left/Right/Back/Bottom)
- Goal:
  - Add orthographic-style workflow presets for precision editing.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/app/viewport/gl_widget.py`
- Acceptance criteria (human-testable):
  - Menu/shortcut actions switch to all six preset views.
  - Orbit/zoom/pan still works after preset switch.
- Tests required:
  - Camera orientation tests.
  - Manual preset switching smoke.

### Task 10: Grid Controls + Camera Snap Settings
- Goal:
  - Expose grid visibility/spacing and camera snap controls.
- Files/modules likely touched:
  - `src/app/ui/main_window.py`
  - `src/app/viewport/gl_widget.py`
  - `src/app/settings.py`
- Acceptance criteria (human-testable):
  - User can toggle grid and adjust spacing.
  - Snap setting changes camera behavior consistently.
  - Settings persist across relaunch.
- Tests required:
  - Settings persistence tests.
  - Manual viewport behavior smoke.

### Task 11: VOX Import v1 (Single-Part Path)
- Goal:
  - Import Magica/Qubicle-compatible `.vox` into active project as one part.
- Files/modules likely touched:
  - `src/core/io/` (new import helper)
  - `src/core/project.py`
  - `src/app/ui/main_window.py`
- Acceptance criteria (human-testable):
  - `File -> Import VOX` loads a `.vox` model into scene.
  - Imported geometry and palette appear correctly.
  - App remains stable after save/open and export.
- Tests required:
  - VOX import parser tests with fixture files.
  - Import -> save/open -> export smoke test.
- Risk/rollback note:
  - If complex VOX variants fail, keep strict v1 parser for common chunks only and reject unsupported files with clear error.

### Task 12: VOX Import v2 (Multi-Model Mapping + Palette Fidelity)
- Goal:
  - Handle multi-model VOX content and better palette-index fidelity.
- Files/modules likely touched:
  - `src/core/io/` import helpers
  - `src/core/scene.py`
  - `src/app/ui/main_window.py`
- Acceptance criteria (human-testable):
  - Multi-model VOX imports as multiple parts.
  - Colors remain stable after import and re-export.
- Tests required:
  - Multi-model import unit tests.
  - Palette mapping regression tests.

### Task 13: Qubicle `.qb` Feasibility Note + Guardrail
- Goal:
  - Add explicit technical decision note for `.qb` support scope/risk.
- Files/modules likely touched:
  - `Doc/QUBICLE_GAP_ANALYSIS.md`
  - `Doc/CURRENT_STATE.md`
  - `Doc/DAILY_REPORT.md`
- Acceptance criteria (human-testable):
  - Decision note exists with go/no-go criteria and rationale.
  - Team can point to documented scope boundary for current phase.
- Tests required:
  - Documentation review only (no code test changes).

### Task 14: OBJ Export Quality Pass (Scale/Pivot/Material Strategy)
- Goal:
  - Improve OBJ output reliability for downstream DCC/engine import.
- Files/modules likely touched:
  - `src/core/export/obj_exporter.py`
  - `src/app/ui/main_window.py`
- Acceptance criteria (human-testable):
  - Export options correctly affect output scale and pivot behavior.
  - OBJ + MTL import predictably in at least one DCC and one engine smoke path.
- Tests required:
  - Export option unit tests.
  - Manual external import smoke checklist.
- Risk/rollback note:
  - Keep previous exporter path behind fallback option if new output regresses compatibility.

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
