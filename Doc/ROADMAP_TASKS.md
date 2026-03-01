# ROADMAP_TASKS (Day Start Board)

Date: 2026-03-01
Mode: Docs-planned execution board for next coding run.
Correction: expanded from 30 to 40 tasks per operator direction (30 core delivery + 10 interface polish).
Execution rule: One task per branch, strict gate before merge to `main`.

## Remaining Tasks

### Task 14: Fill Preview Confidence Layer
- Goal: Add preview indicators for fill reach before commit.
- Likely files/modules touched: `src/app/viewport/gl_widget.py`, `src/core/commands/demo_commands.py`.
- Acceptance criteria (human-testable): Fill tool previews affected region boundary prior to click confirm.
- Tests required: Add fill preview cell-count tests for plane and volume modes.
- Risk/rollback note: Keep preview bounded and lightweight.

### Task 15: Mirror Visual Plane Overlays
- Goal: Render active mirror planes and offsets in viewport.
- Likely files/modules touched: `src/app/viewport/gl_widget.py`, `src/app/app_context.py`.
- Acceptance criteria (human-testable): Enabling mirror axes shows clear plane guides at proper offsets.
- Tests required: Add geometry helper tests for mirror guide generation.
- Risk/rollback note: Allow guide toggle for performance-sensitive scenes.

### Task 16: Palette Metadata Schema v1
- Goal: Add optional palette metadata fields (name/tags/source).
- Likely files/modules touched: `src/core/io/palette_io.py`, `src/app/ui/panels/palette_panel.py`.
- Acceptance criteria (human-testable): Palette metadata can be edited, saved, and reloaded.
- Tests required: Add metadata roundtrip tests for JSON/GPL compatibility behavior.
- Risk/rollback note: Preserve backward compatibility with existing palette files.

### Task 17: Palette Browser and Quick Filter
- Goal: Add palette preset browser with search/filter.
- Likely files/modules touched: `src/app/ui/panels/palette_panel.py`.
- Acceptance criteria (human-testable): Users can search presets quickly and apply one-click load.
- Tests required: Add panel logic tests for filter/apply actions.
- Risk/rollback note: Keep current slot editor behavior unchanged.

### Task 18: glTF UV Export
- Goal: Emit `TEXCOORD_0` in glTF export.
- Likely files/modules touched: `src/core/export/gltf_exporter.py`, `tests/test_gltf_exporter.py`.
- Acceptance criteria (human-testable): Exported glTF contains valid UV accessor and attribute binding.
- Tests required: Add glTF structure tests for UV accessor count/type.
- Risk/rollback note: Keep fallback path for geometry-only export if UV generation fails.

### Task 19: glTF Vertex Color Export
- Goal: Emit `COLOR_0` in glTF export.
- Likely files/modules touched: `src/core/export/gltf_exporter.py`, `tests/test_gltf_exporter.py`.
- Acceptance criteria (human-testable): Multi-color model exports with vertex colors recognized by viewers.
- Tests required: Add color accessor + primitive attribute tests.
- Risk/rollback note: Clamp and normalize color ranges consistently.

### Task 20: glTF Material Baseline
- Goal: Add basic material block generation for glTF exports.
- Likely files/modules touched: `src/core/export/gltf_exporter.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Exported glTF includes minimal valid materials and references.
- Tests required: Add material presence and index wiring tests.
- Risk/rollback note: Keep simple default material if richer mapping is unstable.

### Task 21: VOX Transform Chunk Mapping v1
- Goal: Parse and map common VOX transform chunk semantics into scene parts.
- Likely files/modules touched: `src/core/io/vox_io.py`, `tests/test_vox_io.py`.
- Acceptance criteria (human-testable): VOX files with transform chunks import with expected part offsets.
- Tests required: Add fixture tests with transform chunk expectations.
- Risk/rollback note: Maintain warning path for unsupported variants.

### Task 22: VOX Multi-part Naming and Grouping
- Goal: Improve naming/group mapping for imported multi-model VOX files.
- Likely files/modules touched: `src/core/io/vox_io.py`, `src/core/scene.py`.
- Acceptance criteria (human-testable): Imported models have stable names and optional grouping.
- Tests required: Add VOX import naming/grouping tests.
- Risk/rollback note: Keep deterministic fallback naming when metadata absent.

### Task 23: Qubicle QB Import Feasibility Slice
- Goal: Implement bounded `.qb` importer for core voxel data only.
- Likely files/modules touched: `src/core/io/qb_io.py` (new), `src/app/ui/main_window.py`, `tests/test_qb_io.py` (new).
- Acceptance criteria (human-testable): Import simple `.qb` fixture into scene parts without crash.
- Tests required: Add parser tests using curated tiny fixtures.
- Risk/rollback note: Gate unsupported features with explicit warnings.

### Task 24: Qubicle QB Export Feasibility Slice
- Goal: Implement bounded `.qb` exporter for current scene voxel data.
- Likely files/modules touched: `src/core/export/qb_exporter.py` (new), `src/app/ui/main_window.py`, `tests/test_qb_exporter.py` (new).
- Acceptance criteria (human-testable): Exported `.qb` from simple scene can be re-imported by our importer.
- Tests required: Add roundtrip tests for small scenes.
- Risk/rollback note: Keep feature flagged if compatibility is partial.

### Task 25: Solidify QA Diagnostics
- Goal: Add mesh QA counters (degenerate quads, non-manifold risk hints).
- Likely files/modules touched: `src/core/meshing/solidify.py`, `src/core/analysis/stats.py`, `src/app/ui/panels/stats_panel.py`.
- Acceptance criteria (human-testable): Solidify reports QA counters in stats panel.
- Tests required: Add diagnostic computation tests with synthetic meshes.
- Risk/rollback note: Diagnostics should not block mesh generation.

### Task 26: Incremental Rebuild Telemetry
- Goal: Track and display incremental fallback frequency.
- Likely files/modules touched: `src/core/meshing/solidify.py`, `src/app/ui/panels/stats_panel.py`.
- Acceptance criteria (human-testable): User can see when incremental path falls back to full rebuild.
- Tests required: Add telemetry counter tests and UI formatting tests.
- Risk/rollback note: Keep telemetry lightweight.

### Task 27: Dense Scene Stress Harness (64/96/128)
- Goal: Add repeatable dense-scene perf harness for key operations.
- Likely files/modules touched: `tests/test_perf_baseline.py`, `tests/perf_baseline.json`.
- Acceptance criteria (human-testable): Perf suite reports separate budgets for 64^3, 96^3, 128^3 workloads.
- Tests required: Add tiered perf tests and baseline update.
- Risk/rollback note: Start with conservative thresholds to avoid flaky CI.

### Task 28: Frame-Time Hotspot Pass
- Goal: Reduce viewport frame-time hotspots during dense scene navigation.
- Likely files/modules touched: `src/app/viewport/gl_widget.py`.
- Acceptance criteria (human-testable): Noticeably smoother orbit/pan on dense test scenes.
- Tests required: Extend perf surrogate checks for viewport path.
- Risk/rollback note: Preserve rendering correctness over aggressive optimization.

### Task 29: Memory Budget Instrumentation
- Goal: Add basic memory usage stats for scene/mesh buffers.
- Likely files/modules touched: `src/core/analysis/stats.py`, `src/app/ui/panels/stats_panel.py`.
- Acceptance criteria (human-testable): Stats panel shows estimated voxel/mesh memory usage.
- Tests required: Add deterministic memory estimate tests.
- Risk/rollback note: Clearly label as estimate, not OS-level exact measure.

### Task 30: End-to-End Correctness Sweep
- Goal: Consolidate and validate tool/IO/export correctness with expanded regression tests.
- Likely files/modules touched: `tests/test_command_stack.py`, `tests/test_project_io.py`, `tests/test_vox_io.py`, `tests/test_gltf_exporter.py`.
- Acceptance criteria (human-testable): Full `pytest -q` remains green with new parity coverage.
- Tests required: Add cross-feature regression matrix tests.
- Risk/rollback note: If failures spike, split high-risk assertions behind temporary xfail notes with follow-up tasks.

### Task 31: Interface Polish - Top Toolbar Quick Actions
- Goal: Add compact top toolbar for frequent actions (new/save/open/undo/redo/solidify/export).
- Likely files/modules touched: `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Key actions available without menu diving.
- Tests required: Add action wiring tests where feasible.
- Risk/rollback note: Keep menu actions as source of truth.

### Task 32: Interface Polish - Status HUD Badges
- Goal: Show active tool, pick mode, plane, mirror, projection, and nav preset in viewport HUD.
- Likely files/modules touched: `src/app/viewport/gl_widget.py`, `src/app/app_context.py`.
- Acceptance criteria (human-testable): HUD badges always reflect current editing state.
- Tests required: Add state-to-label formatting tests.
- Risk/rollback note: Allow HUD toggle if visual noise is high.

### Task 33: Interface Polish - Command Palette (Quick Search)
- Goal: Add command palette for fast action search/execute.
- Likely files/modules touched: `src/app/ui/main_window.py`, `src/app/ui/dialogs/`.
- Acceptance criteria (human-testable): Press shortcut, search command name, execute action.
- Tests required: Add command registry/filter tests.
- Risk/rollback note: Keep all actions reachable via existing UI paths.

### Task 34: Interface Polish - Dock Layout Presets
- Goal: Add save/restore UI dock layout presets.
- Likely files/modules touched: `src/app/ui/main_window.py`, `src/app/settings.py`.
- Acceptance criteria (human-testable): User can save and restore at least two layouts.
- Tests required: Add settings persistence tests for layout blobs.
- Risk/rollback note: Fallback to default layout on corrupt settings.

### Task 35: Interface Polish - Theme and Contrast Pass
- Goal: Improve readability and visual hierarchy across panels.
- Likely files/modules touched: `src/app/ui/main_window.py`, panel widgets styles.
- Acceptance criteria (human-testable): Labels, controls, and active states are clearly distinguishable.
- Tests required: Add snapshot/smoke checks for style loading.
- Risk/rollback note: Keep high-contrast default option.

### Task 36: Interface Polish - Numeric Field Drag Scrub
- Goal: Add drag-scrub interaction for numeric transform fields.
- Likely files/modules touched: `src/app/ui/panels/inspector_panel.py`.
- Acceptance criteria (human-testable): Dragging numeric labels adjusts transform smoothly.
- Tests required: Add value clamping and delta mapping tests.
- Risk/rollback note: Preserve direct text entry mode.

### Task 37: Interface Polish - Tool Hotkey Overlay
- Goal: Add in-app hotkey cheat-sheet overlay.
- Likely files/modules touched: `src/app/ui/main_window.py`, `Doc/NEXT_WORKDAY.md`.
- Acceptance criteria (human-testable): Overlay lists current active hotkeys and closes quickly.
- Tests required: Add hotkey registry tests for duplicate conflicts.
- Risk/rollback note: Keep overlay non-modal where possible.

### Task 38: Interface Polish - Precision Input Mode
- Goal: Add temporary precision modifier for camera and transform operations.
- Likely files/modules touched: `src/app/viewport/gl_widget.py`, `src/app/ui/panels/inspector_panel.py`.
- Acceptance criteria (human-testable): Holding precision modifier reduces movement sensitivity.
- Tests required: Add precision scale factor tests.
- Risk/rollback note: Do not alter default speed when modifier is not held.

### Task 39: Interface Polish - Startup Workspace Recovery UX
- Goal: Improve startup dialogs for recovery + last project continuity.
- Likely files/modules touched: `src/app/ui/main_window.py`, `src/core/io/recovery_io.py`.
- Acceptance criteria (human-testable): Startup presents clear choices: restore, discard, open recent.
- Tests required: Add startup choice-path tests.
- Risk/rollback note: Safe default must avoid data loss.

### Task 40: Interface Polish - Final UX Regression and Operator Pack
- Goal: Run final UX polish QA pass and prepare operator validation scripts/checklists.
- Likely files/modules touched: `Doc/DAILY_REPORT.md`, `Doc/NEXT_WORKDAY.md`, `Doc/PACKAGING_CHECKLIST.md`.
- Acceptance criteria (human-testable): Operator can execute full validation checklist with no ambiguity.
- Tests required: Full `pytest -q` and documented manual smoke matrix.
- Risk/rollback note: If unresolved P0 remains, hold merge and document blocker clearly.

## Completed Today
### Task 01: Input State Machine Split (Edit vs Navigate)
- Commit: `64a6ea4`
- Added explicit left-interaction mode state in viewport (`edit` vs `navigate`) to separate camera and tool intent.
- Initialized left interaction mode to navigate and reset it on left-release for deterministic state transitions.
- Added interaction mode resolver that maps voxel tool shapes to edit-mode and non-tool/no-context flows to navigate-mode.
- Updated left mouse press flow to begin brush/shape edit setup only when resolved mode is edit.
- Updated left drag move flow to apply orbit only when resolved mode is navigate.
- Updated left drag move flow to apply brush stroke continuation and shape preview updates only when resolved mode is edit.
- Preserved right-button pan behavior and wheel zoom behavior unchanged.
- Preserved camera snap behavior during navigate drags.
- Added focused tests for interaction-mode resolver behavior across brush/box/line/fill shapes.
- Added focused test for resolver fallback to navigate mode when no context is available.
- Kept implementation scoped to input-state split only (no MMB profile changes in this task).
- No new dependencies introduced; behavior remains production-safe and deterministic.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`123 passed`)

### Task 02: MMB Orbit Navigation Profile
- Commit: `12840b9`
- Added navigation profile state in app context with explicit validated modes (`classic`, `mmb_orbit`).
- Added app-context setter validation for navigation profile updates.
- Added View menu toggle action (`MMB Orbit Navigation`) to switch profiles at runtime.
- Added status feedback when navigation profile is changed.
- Added editor-state persistence for navigation profile in capture flow.
- Added editor-state restore handling for navigation profile in apply flow.
- Updated viewport input handling to track middle-button drag state.
- Added middle-button orbit behavior when `mmb_orbit` profile is active.
- Kept right-button pan behavior intact for both navigation profiles.
- Disabled left-button navigate orbit when `mmb_orbit` profile is active to avoid dual-orbit ambiguity.
- Added regression tests for navigation profile validation and orbit-routing helpers.
- Extended project IO roundtrip editor-state test to include navigation profile persistence key.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`125 passed`)

### Task 03: Blender-Mix Navigation Preset
- Commit: `dbd0bc4`
- Added `blender_mix` as a validated third navigation profile in app context.
- Expanded valid navigation profile set to include classic, mmb_orbit, and blender_mix.
- Replaced single MMB toggle with a dedicated `Navigation Profile` menu.
- Added exclusive profile actions for `Classic`, `MMB Orbit`, and `Blender-Mix`.
- Added direct profile setter handler for runtime profile switching.
- Extended editor-state restore validation to accept `blender_mix` profile values.
- Extended MMB orbit routing so Blender-Mix uses middle-drag orbit.
- Added Blender-Mix modifier behavior: `Shift + Middle Drag` pans camera.
- Preserved right-drag pan behavior across all profiles for compatibility.
- Preserved classic-only left navigate orbit to avoid dual orbit bindings in MMB-based profiles.
- Added app-context regression test coverage for blender-mix profile validation.
- Added viewport helper regression test for Blender-Mix shift-middle pan detection.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`126 passed`)

### Task 04: Navigation Sensitivity Controls
- Commit: `89843ab`
- Added camera sensitivity fields to app context for orbit, pan, and zoom controls.
- Added validated context setter for camera sensitivity axes with bounded range checks.
- Added view-menu actions to set orbit, pan, and zoom sensitivity at runtime.
- Added shared main-window handler to edit sensitivity values through bounded numeric input.
- Added editor-state capture keys for orbit/pan/zoom sensitivity persistence.
- Added editor-state apply logic with clamped restoration for saved sensitivity values.
- Applied orbit sensitivity multiplier to left and middle orbit drag camera rotation.
- Applied pan sensitivity multiplier to camera pan offset math.
- Applied zoom sensitivity multiplier to mouse-wheel zoom response.
- Added app-context regression test coverage for sensitivity validation across all axes.
- Extended project IO roundtrip editor-state fixture with sensitivity fields.
- Added viewport helper regression tests validating sensitivity helper outputs.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`128 passed`)

### Task 05: Drag Transaction Abort Hardening
- Commit: `381e833`
- Added command-stack `transaction_active` property to expose active transaction state explicitly.
- Added command-stack `cancel_transaction()` API with optional rollback behavior.
- Implemented rollback path that undoes staged transaction commands in reverse order.
- Added runtime guard for cancel attempts without active transaction.
- Added context requirement validation for rollback-enabled transaction cancel.
- Updated viewport leave-event flow to abort active brush stroke transactions safely.
- Added viewport focus-out handler to abort active brush stroke transactions on focus loss.
- Added dedicated brush-stroke abort helper in viewport that cancels transaction and emits status.
- Preserved normal brush stroke commit path (`end_transaction`) on successful mouse release.
- Added regression test for rollback cancellation restoring voxel state and keeping undo stack clean.
- Added regression test for cancel-without-active-transaction error behavior.
- Kept scope limited to transaction lifecycle hardening with no tool algorithm changes.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`130 passed`)

### Task 06: Recovery Diagnostic Report
- Commit: `21916d7`
- Added dedicated recovery diagnostic file path helper in recovery IO module.
- Added recovery diagnostic writer utility that records stage, error, snapshot path, and UTC timestamp.
- Added JSON diagnostic payload schema for operator triage of recovery failures.
- Wired main-window recovery-failure path to emit diagnostic file on load exceptions.
- Added defensive fallback logging if diagnostic file writing itself fails.
- Extended recovery failure warning dialog to include diagnostic file path when available.
- Preserved existing safe-fail behavior (clear snapshot and continue startup) on recovery load failure.
- Kept recovery save/load schema behavior unchanged for successful paths.
- Added recovery diagnostic regression test validating payload content and file creation.
- Preserved compatibility with existing recovery snapshot tests and version mismatch guards.
- Kept implementation dependency-free and IO/UI scoped.
- Improved operator triage signal without blocking normal app startup behavior.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`131 passed`)

### Task 07: Project Schema Version Handshake
- Commit: `ffe7c1b`
- Added explicit project schema version constants for current and minimum supported versions.
- Added load-time version type validation with clear error for non-integer schema versions.
- Added deterministic rejection path for schema versions older than supported minimum.
- Added deterministic rejection path for schema versions newer than supported runtime version.
- Added migration hook scaffolding function to centralize future payload version upgrades.
- Wired payload migration stage into project loading flow before model materialization.
- Kept current schema happy-path behavior unchanged for version-1 project payloads.
- Preserved legacy voxels fallback behavior under supported schema versions.
- Added regression test for too-old schema version rejection behavior.
- Added regression test for newer-than-supported schema version rejection behavior.
- Kept save format stable and dependency footprint unchanged.
- Implemented changes in IO layer only (no UI behavior regressions introduced).
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`133 passed`)

### Task 08: Save/Open Robustness Sweep
- Commit: `008bd30`
- Added project IO error-detail helper to produce actionable open/save failure messaging with path context.
- Updated open-project failure dialog to include operation name, path, and raw exception detail.
- Updated save-as flow to set `current_path` only after successful write.
- Added save-path helper return status to prevent state mutation on failed save.
- Added save failure dialog path with operation-aware error text.
- Preserved successful save path behavior and status-bar success messaging.
- Preserved open success path behavior and post-load UI refresh flow.
- Kept IO hardening scoped to main-window open/save entry points (no export changes).
- Added regression test for project-IO error detail formatting.
- Improved operator/user triage signal for path/permission errors.
- Avoided adding new dependencies or changing project schema.
- Maintained compatibility with existing open/save roundtrip tests.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`134 passed`)

### Task 09: Scene Outliner Search Filter
- Commit: `09d34a6`
- Added part filter input control to inspector panel with live refresh binding.
- Added group filter input control to inspector panel with live refresh binding.
- Added filtered list-population logic for parts during inspector refresh.
- Added filtered list-population logic for groups during inspector refresh.
- Preserved active-part transform/visibility/lock control behavior under filtered list states.
- Preserved group visibility/lock control behavior under filtered list states.
- Added reusable case-insensitive substring matcher helper for filter checks.
- Ensured empty filter string returns full list for both parts and groups.
- Kept filtering scope non-destructive (view-only; no scene mutation side effects).
- Added regression test coverage for filter matcher behavior and case-insensitive matching.
- Kept implementation UI-scoped with no new dependencies.
- Maintained existing part/group selection signal contracts.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`135 passed`)

### Task 10: Multi-select Part Actions
- Commit: `d5d8b4c`
- Enabled extended multi-selection mode for part list in inspector panel.
- Added batch part action buttons: show selected, hide selected, lock selected, unlock selected, delete selected.
- Added inspector helper to collect selected part IDs with current-item fallback.
- Added batch visibility update flow for selected part IDs.
- Added batch lock update flow for selected part IDs.
- Added batch delete flow with confirmation and \"at least one part remains\" guard.
- Added scene-level batch APIs for part visibility, lock state, and deletion operations.
- Added scene batch-delete validation to reject deleting all parts.
- Preserved existing single-part controls and behavior as compatible subset.
- Added scene regression tests for batch visibility, lock, and delete semantics.
- Kept implementation dependency-free and scoped to inspector/scene workflow.
- Maintained existing active-part selection signaling after batch deletion.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`138 passed`)

### Task 11: Voxel Selection Set v1
- Commit: `5552389`
- Added voxel selection mode state in app context (`voxel_selection_mode`) with validated setter.
- Added selected voxel set state in app context (`selected_voxels`) with explicit set/clear helpers.
- Added tools-panel checkbox (`Voxel Selection Mode`) and signal wiring to toggle selection mode from UI.
- Synced tools-panel refresh path so checkbox mirrors context state on project/editor updates.
- Connected main-window tools signal to context handler and persisted selection mode in editor-state capture/apply.
- Added selection-mode apply safety to clear selected voxels when mode is turned off.
- Added viewport selection rendering path with highlighted wireframe for selected cells.
- Added selection click behavior (single replace, `Ctrl` add/remove toggle).
- Added selection drag-box behavior on active edit plane with live preview.
- Disabled edit hover preview while selection mode is active to reduce visual conflict.
- Added interaction-mode resolver override so selection mode routes left input into selection flow.
- Added regression tests for app-context selection state and selection interaction routing helper.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`140 passed`)

### Task 12: Selected Voxel Move Tool
- Commit: `8df078a`
- Added command `MoveSelectedVoxelsCommand` to move selected voxel sets by integer axis delta.
- Implemented deterministic source filtering so only existing selected cells participate in move.
- Implemented collision blocking when destination contains non-selected voxels.
- Preserved per-voxel color values during move by carrying source color map into target cells.
- Updated command to refresh selection set to moved coordinates after successful move.
- Added undo path that restores original voxel positions/colors and original selection set.
- Wired viewport key input mapping for selection moves: arrows (`X/Y`) and `PageUp/PageDown` (`Z`).
- Added viewport key handler that routes mapped move keys through command stack for undo/redo support.
- Added focus-policy hardening so viewport receives key events after click interaction.
- Added status messages for move success, collision block, empty selection, and missing-source no-op.
- Added command regression test for move + undo/redo correctness and selection sync.
- Added command regression test for destination collision-block behavior.
- Added shortcut regression test for key-to-delta mapping coverage.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`143 passed`)

### Task 13: Selected Voxel Duplicate Tool
- Commit: `COMMIT_PENDING`
- Added command `DuplicateSelectedVoxelsCommand` for offset duplication of selected voxel sets.
- Implemented source filtering so only existing selected cells are used as duplication input.
- Added deterministic destination-occupancy collision blocking to avoid destructive overwrite.
- Added safety cap guard (`50,000` selected cells) to prevent accidental explosive duplication.
- Preserved source voxels and colors while creating duplicated target copies.
- Updated selection set after duplicate to target copy cells for immediate follow-up edits.
- Added undo path removing duplicated voxels and restoring prior selection coordinates.
- Added tools-panel duplicate controls with X/Y/Z offset spinboxes and one-click duplicate action.
- Wired tools-panel duplicate signal into main-window command execution flow.
- Added status feedback for duplicate success, no selection, collision block, and cap block cases.
- Added regression tests for duplicate undo/redo behavior and destination-collision blocking.
- Added regression test confirming duplicate behavior is independent of mirror mode state.
- Kept implementation dependency-free and scoped to selection duplicate workflow only.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`146 passed`)
