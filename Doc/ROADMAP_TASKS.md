# ROADMAP_TASKS

Date: 2026-03-01
Mode: Phase 1 Parity Closure Board (v1)
Scope: Docs-first plan for closing P0/P1 parity gaps before Phase 2 mesh editing work.
Task model: One task = one branch = one commit = merge to `main`.

## Milestone A: Core Voxel Editing Parity (tools + selection + 2D/3D ergonomics)

### Task 01: Slice Mode Core State + Data Contract
- Parity items reduced: `F02`, `W06`
- Goal: Introduce dedicated slice/canvas mode state model independent from plane-lock.
- Files/modules likely touched: `src/app/app_context.py`, `src/app/ui/panels/tools_panel.py`, `src/core/project.py`, `src/core/io/project_io.py`.
- Acceptance criteria (human-testable): A distinct "Slice Mode" toggle exists; state persists across save/open.
- Tests required (pytest): editor-state roundtrip tests for slice mode keys; context validation tests.
- Risk/rollback note: Keep existing plane-lock behavior unchanged if slice mode is off.

### Task 02: Slice Mode Viewport Rendering + Clip Plane UX
- Parity items reduced: `F02`, `W06`
- Goal: Render a true 2D slice canvas view with configurable slice index and axis.
- Files/modules likely touched: `src/app/viewport/gl_widget.py`, `src/app/ui/panels/tools_panel.py`.
- Acceptance criteria (human-testable): In slice mode, only active slice is editable/visible with clear axis/index indicator.
- Tests required (pytest): slice visibility/filter helper tests; HUD/slice label tests.
- Risk/rollback note: Fallback to current 3D rendering path if slice pipeline fails.

### Task 03: Slice Paint/Erase Tooling
- Parity items reduced: `F02`, `F03`, `W06`
- Goal: Enable paint/erase operations constrained to active 2D slice canvas.
- Files/modules likely touched: `src/app/viewport/gl_widget.py`, `src/core/commands/demo_commands.py`.
- Acceptance criteria (human-testable): Paint/erase modifies only active slice, undo/redo works.
- Tests required (pytest): slice-constrained edit tests; undo/redo slice command tests.
- Risk/rollback note: Do not regress 3D brush stroke path.

### Task 04: Slice Selection + Marquee Operations
- Parity items reduced: `F05`, `W03`, `W06`
- Goal: Add slice-local rectangular selection and basic selection actions.
- Files/modules likely touched: `src/app/viewport/gl_widget.py`, `src/app/app_context.py`, `src/core/commands/demo_commands.py`.
- Acceptance criteria (human-testable): Drag-select on slice selects expected cells; selection actions apply only to selected cells.
- Tests required (pytest): selection bounding-box tests on slice coordinates.
- Risk/rollback note: Preserve existing 3D selection mode behavior.

### Task 05: Fast 3D<->2D Mode Switching UX
- Parity items reduced: `W06`, `W05`
- Goal: Add low-friction hotkey/button switch between 3D and slice modes with remembered state.
- Files/modules likely touched: `src/app/ui/main_window.py`, `src/app/ui/panels/tools_panel.py`.
- Acceptance criteria (human-testable): Single shortcut/toggle swaps modes without losing active tool/selection unexpectedly.
- Tests required (pytest): mode-switch state retention tests.
- Risk/rollback note: Ensure mode switch cannot corrupt active tool context.

### Task 06: Primitive Tool Framework
- Parity items reduced: `F04`, `F06`
- Goal: Add shared primitive-generation command pipeline and UI hooks.
- Files/modules likely touched: `src/core/commands/demo_commands.py`, `src/app/ui/panels/tools_panel.py`, `src/app/viewport/gl_widget.py`.
- Acceptance criteria (human-testable): Primitive tool options panel exists with preview/apply flow.
- Tests required (pytest): primitive command validation tests.
- Risk/rollback note: Keep existing box/line tools isolated from primitive builder.

### Task 07: Primitive Tools Pack I (Cube + Sphere)
- Parity items reduced: `F04`
- Goal: Implement cube and sphere primitive creation tools with preview.
- Files/modules likely touched: `src/core/commands/demo_commands.py`, `src/app/viewport/gl_widget.py`.
- Acceptance criteria (human-testable): Users can place cube and sphere primitives with expected dimensions.
- Tests required (pytest): deterministic voxel-count/shape tests for cube and sphere outputs.
- Risk/rollback note: Cap primitive bounds to avoid accidental huge allocations.

### Task 08: Primitive Tools Pack II (Pyramid + Cone + Cylinder)
- Parity items reduced: `F04`
- Goal: Implement pyramid, cone, and cylinder primitive tools.
- Files/modules likely touched: `src/core/commands/demo_commands.py`, `src/app/viewport/gl_widget.py`.
- Acceptance criteria (human-testable): Each primitive type is placeable with predictable axis alignment.
- Tests required (pytest): shape fixture tests for each primitive family.
- Risk/rollback note: Disable unsupported parameter combos instead of undefined output.

### Task 09: Contiguous/Magic Selection Mode
- Parity items reduced: `F05`, `W03`
- Goal: Add contiguous-region (magic-wand style) selection by color/connectivity.
- Files/modules likely touched: `src/core/commands/demo_commands.py`, `src/app/viewport/gl_widget.py`, `src/app/ui/panels/tools_panel.py`.
- Acceptance criteria (human-testable): Clicking voxel selects contiguous matching region per selected rule.
- Tests required (pytest): contiguous selection algorithm tests (plane/volume options).
- Risk/rollback note: Bounded traversal guards required for large regions.

### Task 10: Freehand Paint Selection Mode
- Parity items reduced: `F05`, `W03`
- Goal: Add paint-through selection brush for rapid selection authoring.
- Files/modules likely touched: `src/app/viewport/gl_widget.py`, `src/app/app_context.py`.
- Acceptance criteria (human-testable): Dragging in selection mode paints selection cells continuously.
- Tests required (pytest): stroke-based selection accumulation tests.
- Risk/rollback note: Keep edit and selection stroke transactions separated.

### Task 11: Selection Action Set v1
- Parity items reduced: `F06`, `W03`
- Goal: Add invert/expand/shrink/clear selection actions.
- Files/modules likely touched: `src/core/commands/demo_commands.py`, `src/app/ui/main_window.py`, `src/app/ui/panels/tools_panel.py`.
- Acceptance criteria (human-testable): Selection actions are available and produce expected cell sets.
- Tests required (pytest): selection morphology tests and command undo/redo tests.
- Risk/rollback note: Feature-flag advanced actions if performance degrades.

### Task 12: Transform Action Set v1 (Rotate/Flip Selected Voxels)
- Parity items reduced: `F06`
- Goal: Implement rotate/flip transforms for selected voxels around pivot.
- Files/modules likely touched: `src/core/commands/demo_commands.py`, `src/app/ui/panels/tools_panel.py`.
- Acceptance criteria (human-testable): Selected voxels rotate/flip correctly with undo/redo support.
- Tests required (pytest): transform mapping tests for each axis/operation.
- Risk/rollback note: Block operations causing collisions unless overwrite mode is explicit.

### Task 13: Hierarchy Model v1 (Nested Groups/Compounds)
- Parity items reduced: `F09`, `W09`
- Goal: Extend scene model to support nested groups/compound hierarchy.
- Files/modules likely touched: `src/core/scene.py`, `src/core/project.py`, `src/core/io/project_io.py`.
- Acceptance criteria (human-testable): Groups can contain groups and parts; hierarchy persists after save/open.
- Tests required (pytest): hierarchy CRUD + serialization tests.
- Risk/rollback note: Provide migration fallback for flat-group legacy projects.

### Task 14: Hierarchy Outliner Tree UI
- Parity items reduced: `F09`, `W09`
- Goal: Replace flat group list with tree outliner supporting expand/collapse and selection.
- Files/modules likely touched: `src/app/ui/panels/inspector_panel.py`.
- Acceptance criteria (human-testable): Hierarchy is visible and navigable with parent/child relationships.
- Tests required (pytest): outliner tree-data mapping tests.
- Risk/rollback note: Keep existing part list path available behind fallback toggle during rollout.

### Task 15: Hierarchy Drag/Drop + Reparenting
- Parity items reduced: `F09`, `W09`
- Goal: Add drag/drop reparenting for parts/groups within outliner.
- Files/modules likely touched: `src/app/ui/panels/inspector_panel.py`, `src/core/scene.py`.
- Acceptance criteria (human-testable): Users can reparent nodes and order is preserved across restart.
- Tests required (pytest): reparent validation tests (cycle prevention, root constraints).
- Risk/rollback note: Disallow illegal cycles and auto-revert invalid drops.

### Task 16: Palette Library Management v1
- Parity items reduced: `F10`
- Goal: Add named palette library browser (project + global) with tagging/filtering.
- Files/modules likely touched: `src/app/ui/panels/palette_panel.py`, `src/core/io/`.
- Acceptance criteria (human-testable): Users can save/load/search named palette entries from library.
- Tests required (pytest): library metadata persistence tests.
- Risk/rollback note: Keep existing simple palette import/export fully functional.

## Milestone B: Format Parity (imports/exports breadth)

### Task 17: Import Registry + Pluggable Loader Framework
- Parity items reduced: `F12`, `Q04`
- Goal: Introduce normalized import registry/dispatcher for multi-format support.
- Files/modules likely touched: `src/core/io/__init__.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): File dialog supports multiple importers via unified flow.
- Tests required (pytest): loader registry resolution tests.
- Risk/rollback note: Maintain existing VOX/QB import code paths via adapters.

### Task 18: QEF Importer (Baseline Reader)
- Parity items reduced: `F12`
- Goal: Implement baseline QEF import support.
- Files/modules likely touched: `src/core/io/qef_io.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): QEF sample imports into editable scene with colors.
- Tests required (pytest): QEF fixture parse tests.
- Risk/rollback note: Explicitly reject unsupported QEF variants with clear warnings.

### Task 19: QBT Importer (Baseline Reader)
- Parity items reduced: `F12`
- Goal: Implement baseline QBT import support.
- Files/modules likely touched: `src/core/io/qbt_io.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): QBT sample imports with expected part structure.
- Tests required (pytest): QBT fixture parse tests.
- Risk/rollback note: Keep parser bounded against malformed payload sizes.

### Task 20: QMO Importer (Baseline Reader)
- Parity items reduced: `F12`
- Goal: Implement baseline QMO import support.
- Files/modules likely touched: `src/core/io/qmo_io.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): QMO sample loads with stable scene mapping.
- Tests required (pytest): QMO fixture parse tests.
- Risk/rollback note: Unknown chunk classes should warn, not crash.

### Task 21: QBCL Importer (Baseline Reader)
- Parity items reduced: `F12`
- Goal: Implement baseline QBCL import support.
- Files/modules likely touched: `src/core/io/qbcl_io.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): QBCL sample imports and is editable.
- Tests required (pytest): QBCL fixture parse tests.
- Risk/rollback note: Fail closed on unsupported compression/encryption variants.

### Task 22: Minecraft Schematic Importer v1
- Parity items reduced: `F12`
- Goal: Add schematic import pipeline with block-color mapping policy.
- Files/modules likely touched: `src/core/io/schematic_io.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Schematic imports to voxels with deterministic palette mapping.
- Tests required (pytest): schematic fixture mapping tests.
- Risk/rollback note: Document mapping fallback for unknown block IDs.

### Task 23: FBX Exporter Baseline
- Parity items reduced: `F13`
- Goal: Add functional FBX export baseline (or documented bridge path if direct writer constrained).
- Files/modules likely touched: `src/core/export/fbx_exporter.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): FBX export option exists and outputs a readable FBX file.
- Tests required (pytest): exporter smoke + structural sanity tests.
- Risk/rollback note: If bridge strategy used, gate with explicit dependency checks and fallback errors.

### Task 24: Collada Exporter Baseline
- Parity items reduced: `F13`
- Goal: Add Collada (`.dae`) export baseline.
- Files/modules likely touched: `src/core/export/collada_exporter.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Collada export generates non-empty `.dae` and loads in external viewer.
- Tests required (pytest): Collada XML structure sanity tests.
- Risk/rollback note: Keep feature flag if fidelity remains partial.

### Task 25: Slice PNG Export
- Parity items reduced: `F14`
- Goal: Export active slice or slice stack as PNG images.
- Files/modules likely touched: `src/core/export/slice_png_exporter.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Users can export slice PNG(s) from slice mode with expected dimensions/colors.
- Tests required (pytest): pixel output tests for deterministic slice fixtures.
- Risk/rollback note: Bound batch export sizes to prevent runaway output.

### Task 26: Format Fidelity Harness + Golden Fixtures
- Parity items reduced: `Q04`, `F12`, `F13`
- Goal: Add cross-format golden fixture suite for import/export fidelity checks.
- Files/modules likely touched: `tests/fixtures/*`, `tests/test_*_io.py`, `tests/test_*_exporter.py`.
- Acceptance criteria (human-testable): Roundtrip/report command identifies fidelity deltas across supported formats.
- Tests required (pytest): new golden equivalence tests and tolerances.
- Risk/rollback note: Keep fixture sets small and deterministic to avoid flaky CI.

## Milestone C: Voxelizer/Utility/Mesh-module Equivalents (Phase 1.5)

### Task 27: Voxelizer Pipeline Skeleton (OBJ+MTL Intake)
- Parity items reduced: `F15`
- Goal: Add mesh-intake workflow to prepare voxelization jobs from OBJ(+MTL).
- Files/modules likely touched: `src/core/io/obj_mesh_io.py`, `src/app/ui/main_window.py`, `src/app/ui/dialogs/`.
- Acceptance criteria (human-testable): Import mesh for voxelization opens job dialog with source summary.
- Tests required (pytest): OBJ mesh intake parser tests.
- Risk/rollback note: Reject unsupported mesh features with explicit diagnostics.

### Task 28: Voxelizer Conversion v1 (Mesh->Voxel)
- Parity items reduced: `F15`
- Goal: Convert intake meshes to voxel volume with configurable resolution.
- Files/modules likely touched: `src/core/voxelizer/voxelize.py`, `src/app/ui/dialogs/`.
- Acceptance criteria (human-testable): Users can voxelize simple OBJ assets into editable scene parts.
- Tests required (pytest): voxelizer output shape/count regression tests.
- Risk/rollback note: Bound resolution and memory use to prevent lockups.

### Task 29: Voxelizer Texture/Material Sampling v1
- Parity items reduced: `F15`, `F10`
- Goal: Map mesh material/texture color data into voxel palette indices.
- Files/modules likely touched: `src/core/voxelizer/color_sampling.py`, `src/app/ui/panels/palette_panel.py`.
- Acceptance criteria (human-testable): Voxelized result keeps recognizable color distribution from source texture/material.
- Tests required (pytest): color quantization/mapping tests.
- Risk/rollback note: Provide fallback flat-color mode if texture sampling fails.

### Task 30: Utility Terrain Generator v1
- Parity items reduced: `F17`
- Goal: Add procedural terrain/landscape generator for voxel parts.
- Files/modules likely touched: `src/core/tools/terrain_generator.py`, `src/app/ui/dialogs/`.
- Acceptance criteria (human-testable): Users can generate bounded terrain in a new/existing part.
- Tests required (pytest): deterministic terrain seed tests.
- Risk/rollback note: Clamp generation dimensions and seed ranges.

### Task 31: Utility Heightmap Import v1
- Parity items reduced: `F17`
- Goal: Build terrain from grayscale heightmap images.
- Files/modules likely touched: `src/core/tools/heightmap_import.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Heightmap import creates expected relief and scale mapping.
- Tests required (pytest): fixture-based heightmap conversion tests.
- Risk/rollback note: Validate image dimensions and color mode before import.

### Task 32: Compound Operations Toolkit
- Parity items reduced: `F17`, `F09`
- Goal: Add compound-oriented operations (merge/split/promote child) for hierarchy workflows.
- Files/modules likely touched: `src/core/scene.py`, `src/app/ui/panels/inspector_panel.py`.
- Acceptance criteria (human-testable): Users can perform compound operations without hierarchy corruption.
- Tests required (pytest): hierarchy operation invariants tests.
- Risk/rollback note: Transaction-wrap all compound edits for safe undo.

### Task 33: Mesh-Module Optimization Presets v1
- Parity items reduced: `F16`, `Q05`
- Goal: Add explicit optimization presets for mesh export (quality vs size).
- Files/modules likely touched: `src/core/export/obj_exporter.py`, `src/core/export/gltf_exporter.py`, `src/app/ui/dialogs/`.
- Acceptance criteria (human-testable): Export preset selection shows measurable mesh complexity differences.
- Tests required (pytest): preset output triangle-count comparison tests.
- Risk/rollback note: Keep existing default export output unchanged unless preset selected.

### Task 34: Advanced Module Exports (Colored STL + Cubes)
- Parity items reduced: `F16`
- Goal: Add colored STL export and "export as cubes" option.
- Files/modules likely touched: `src/core/export/stl_exporter.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): STL and cube-export options produce valid files.
- Tests required (pytest): STL writer structure tests and cube-export topology tests.
- Risk/rollback note: Mark colored STL capability limits clearly in UI.

## Milestone D: Keymap + Workflow Polish + Release Hardening

### Task 35: Keymap Editor UI v1
- Parity items reduced: `F11`, `W08`
- Goal: Add user-editable shortcut map for primary commands/tools.
- Files/modules likely touched: `src/app/ui/dialogs/keymap_dialog.py`, `src/app/ui/main_window.py`, `src/app/settings.py`.
- Acceptance criteria (human-testable): Users can change, save, and restore shortcut bindings.
- Tests required (pytest): keymap validation/conflict tests.
- Risk/rollback note: Provide one-click reset to default keymap.

### Task 36: Shortcut Profiles Import/Export
- Parity items reduced: `F11`, `W08`
- Goal: Support keymap profile import/export (JSON).
- Files/modules likely touched: `src/core/io/keymap_io.py`, `src/app/ui/dialogs/keymap_dialog.py`.
- Acceptance criteria (human-testable): Keymap profiles can be exported, imported, and applied correctly.
- Tests required (pytest): profile roundtrip + schema validation tests.
- Risk/rollback note: Reject invalid profile files with detailed error.

### Task 37: Large-Scene Scale Validation Campaign
- Parity items reduced: `F08`, `Q05`
- Goal: Add stress scenarios and runtime checks for large scene/object behavior.
- Files/modules likely touched: `tests/test_perf_baseline.py`, `tests/perf_baseline.json`, `src/core/analysis/stats.py`.
- Acceptance criteria (human-testable): Defined large-scene scenarios run without crash and report stable telemetry.
- Tests required (pytest): new large-scene perf/stability tests.
- Risk/rollback note: Keep thresholds environment-tolerant to avoid flaky failures.

### Task 38: Packaging Matrix Automation v1
- Parity items reduced: `Q07`, `Q08`
- Goal: Automate clean-machine style packaging verification matrix output.
- Files/modules likely touched: `tools/package_windows.ps1`, `Doc/OPERATIONS.md`, `tests/`.
- Acceptance criteria (human-testable): Packaging run emits machine/profile matrix report artifact.
- Tests required (pytest): packaging diagnostics parser tests (if applicable).
- Risk/rollback note: Keep manual packaging path intact as fallback.

### Task 39: Publish/Print Integration Hooks (Baseline)
- Parity items reduced: `F18`
- Goal: Add baseline hooks/workflow for print/export handoff and optional publish targets.
- Files/modules likely touched: `src/app/ui/main_window.py`, `Doc/OPERATIONS.md`.
- Acceptance criteria (human-testable): Users can prepare/export assets for print/publish with documented path.
- Tests required (pytest): command routing tests for new menu actions.
- Risk/rollback note: If external API dependency is high, ship as documented handoff workflow first.

### Task 40: End-of-Board QA + Parity Recheck Run
- Parity items reduced: `Q04`, `Q07`, `Q08` (verification closure)
- Goal: Execute full QA gate and re-score parity using reusable prompt.
- Files/modules likely touched: `Doc/CURRENT_STATE.md`, `Doc/PARITY_SCORECARD.md`, `Doc/DAILY_REPORT.md`, `Doc/PARITY_RECHECK_PROMPT.md`.
- Acceptance criteria (human-testable): Updated parity percentages and delta report are published with clear pass/fail decision.
- Tests required (pytest): full `pytest -q` and documented manual QA matrix.
- Risk/rollback note: If P0/P1 items remain <1.0, hold stable promotion and roll to next closure board.

## Board Notes
- This board intentionally excludes Phase 2 mesh-edit feature work (`vertex/edge/face` editing).
- Completion target: move all P0/P1 scorecard items to at least `1.0` where feasible in Phase 1/1.5 scope.
