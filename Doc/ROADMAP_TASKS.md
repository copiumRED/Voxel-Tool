# ROADMAP_TASKS (Day Start Board)

Date: 2026-03-01
Mode: Docs-planned execution board for next coding run.
Correction: expanded from 30 to 40 tasks per operator direction (30 core delivery + 10 interface polish).
Execution rule: One task per branch, strict gate before merge to `main`.

## Remaining Tasks

- None.

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
- Commit: `c64a469`
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

### Task 14: Fill Preview Confidence Layer
- Commit: `f27010b`
- Added `compute_fill_preview_cells` helper in command module for previewing connected fill regions.
- Implemented plane-mode preview region computation using bounded flood-fill over current edit plane.
- Implemented volume-mode preview region computation using bounded 3D flood-fill.
- Reused existing safety thresholds (`fill_max_cells`) so preview remains bounded under large regions.
- Kept preview non-destructive by reading current voxel state only and applying no edits.
- Updated viewport fill-hover path to resolve target cell using existing pick/plane rules.
- Replaced single-cell fill hover marker with connected-region preview outlines.
- Preserved mirror behavior by expanding preview cells through existing mirror expansion logic.
- Preserved temporary erase preview color behavior while adding region-wide preview coverage.
- Added regression test validating plane fill preview connected cell count/content.
- Added regression test validating volume fill preview connected cell count/content.
- Kept implementation lightweight and scoped to fill preview only (no command behavior changes).
- Maintained compatibility with existing fill execution and threshold-block command behavior.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`148 passed`)

### Task 15: Mirror Visual Plane Overlays
- Commit: `7d1e828`
- Refactored mirror guide rendering to use a dedicated geometry helper (`_mirror_guide_segments`).
- Added deterministic mirror-guide segment generation for X/Y/Z axes with configurable extent and step.
- Preserved axis color coding (X red, Y green, Z blue) for visual clarity.
- Preserved offset-driven plane placement and ensured guide geometry respects configured mirror offsets.
- Simplified draw path by converting helper segments directly into GL line vertices.
- Added mirror overlay HUD label with active axis offsets (`X@`, `Y@`, `Z@`) for fast visual confirmation.
- Shifted error-text overlay line down to avoid overlap with new mirror HUD label.
- Kept rendering scope non-destructive (visualization only; no voxel edit behavior changes).
- Added regression test for mirror segment helper behavior under enabled/disabled axis states.
- Added regression test for mirror segment offset correctness on generated geometry.
- Added regression test for mirror HUD label content with enabled axes and offsets.
- Kept implementation dependency-free and viewport-scoped.
- Maintained compatibility with existing mirror edit behavior and existing tool flows.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`150 passed`)

### Task 16: Palette Metadata Schema v1
- Commit: `2231a82`
- Added optional palette metadata normalization helper (`name`, `tags`, `source`) in palette IO layer.
- Extended JSON palette preset save payload to include `metadata` object alongside color entries.
- Added metadata-aware load API (`load_palette_preset_with_metadata`) with backward-compatible defaults.
- Kept existing `load_palette_preset` API stable by returning palette-only values for legacy call sites.
- Preserved GPL compatibility by returning empty metadata for GPL load paths.
- Added metadata validation guard for malformed JSON metadata payload types.
- Added AppContext `palette_metadata` state with default empty metadata values.
- Added palette panel metadata editors (Name, Tags, Source) with live context update on edit commit.
- Wired palette preset save path to write current metadata from context.
- Wired palette preset load path to restore metadata and palette together.
- Preserved existing palette color workflow and slot-lock behavior unchanged.
- Added JSON metadata roundtrip regression test for save/load parity.
- Added GPL metadata compatibility regression test verifying empty metadata fallback behavior.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`152 passed`)

### Task 17: Palette Browser and Quick Filter
- Commit: `dac7964`
- Added palette preset browser section to palette panel with filter input and preset list.
- Added one-click load path (`Load Selected`) and double-click load behavior for browser entries.
- Added preset browser directory helper rooted at app temp (`palette_presets`) with auto-create behavior.
- Updated save/load preset dialogs to default into preset browser directory for faster workflow.
- Added preset filtering helper with case-insensitive substring matching.
- Added deterministic preset sorting for stable list behavior across refreshes.
- Added browser refresh path on panel refresh and after successful preset save.
- Added shared preset load helper to avoid duplicated load/apply logic between dialog and browser actions.
- Preserved existing palette edit/add/remove/swap/lock workflows.
- Preserved metadata-aware preset load/save behavior introduced in Task 16.
- Added regression test for preset quick-filter helper behavior and stable sorting output.
- Kept implementation panel-scoped without introducing dependencies.
- Maintained compatibility with direct file dialog load/save fallback.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`153 passed`)

### Task 18: glTF UV Export
- Commit: `0f305bf`
- Added UV generation path for glTF export (`_build_vertex_uvs`) derived from normalized X/Z bounds.
- Added per-vertex UV buffer serialization (`<2f`) and 4-byte alignment handling.
- Added dedicated glTF bufferView for UV data with array-buffer target.
- Added dedicated glTF accessor for UVs (`componentType=FLOAT`, `type=VEC2`).
- Updated primitive attributes to include `TEXCOORD_0` binding.
- Updated primitive index accessor wiring to account for inserted UV accessor.
- Preserved existing position and normal export paths unchanged.
- Preserved existing empty-mesh export path behavior.
- Kept UV generation deterministic and dependency-free.
- Added regression assertions for `TEXCOORD_0` attribute index and UV accessor type/count.
- Added regression assertion for index accessor shift after UV insertion.
- Maintained backward-compatible glTF structure for viewers expecting POSITION/NORMAL.
- Kept scope strictly to UV emission (material/color tasks remain separate).
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`153 passed`)

### Task 19: glTF Vertex Color Export
- Commit: `72fc235`
- Added vertex-color generation helper for glTF export (`_build_vertex_colors`) using mesh face-color indices.
- Added palette-aware color mapping path with default palette fallback when palette is not supplied.
- Normalized RGB output to float color space (`0.0-1.0`) for glTF `COLOR_0` compatibility.
- Added per-vertex color buffer serialization (`<3f`) with 4-byte alignment handling.
- Added dedicated glTF color bufferView (`ARRAY_BUFFER`) and color accessor (`VEC3`, float).
- Updated glTF primitive attributes to include `COLOR_0`.
- Updated glTF primitive index accessor reference to account for inserted color accessor.
- Wired main-window glTF export call to pass active app palette for accurate color emission.
- Preserved existing POSITION/NORMAL/TEXCOORD_0 export behavior.
- Kept empty-mesh glTF export path behavior unchanged.
- Added regression assertions for `COLOR_0` attribute binding and accessor wiring.
- Added regression test decoding glTF buffer payload and verifying multi-color output emits distinct vertex colors.
- Kept implementation dependency-free and scoped to vertex-color parity only.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`154 passed`)

### Task 20: glTF Material Baseline
- Commit: `d8bef92`
- Added glTF material baseline helper (`_build_material_baseline`) in exporter.
- Added `materials` array emission with one default PBR material.
- Added primitive material binding (`material: 0`) on exported mesh primitive.
- Set baseline material to `doubleSided: true` for reliable voxel shell rendering.
- Added minimal `pbrMetallicRoughness` payload with conservative defaults.
- Initialized material base color from palette/face-color context for stable default tint.
- Preserved existing POSITION/NORMAL/TEXCOORD_0/COLOR_0 attribute export paths.
- Preserved existing index buffer/accessor wiring and triangle mode.
- Preserved empty-mesh glTF export behavior (no materials when no mesh payload).
- Kept material generation dependency-free and deterministic.
- Added regression assertions for material array presence and primitive material index wiring.
- Added regression assertions for baseline PBR structure and baseColorFactor shape.
- Kept implementation scoped strictly to glTF material baseline (no UI behavior changes).
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`154 passed`)

### Task 21: VOX Transform Chunk Mapping v1
- Commit: `9da9a48`
- Added bounded `nTRN` parsing support in VOX IO for translation frame extraction (`_t`).
- Added VOX dict reader helper to parse key/value dictionaries used by scene-graph chunks.
- Added nTRN translation parser that reads frame dictionaries and extracts integer XYZ offsets.
- Applied parsed translation offsets to the next imported model's XYZI voxel coordinates.
- Reset pending translation after model import to avoid leaking transform to subsequent models.
- Preserved fallback behavior when no transform is present (`0,0,0` translation).
- Preserved warning pathway for malformed/unsupported `nTRN` chunk payloads.
- Kept unsupported chunk reporting unchanged for non-main unknown chunks.
- Kept current public load APIs stable (`load_vox`, `load_vox_models`, warning wrapper).
- Added VOX test helper for writing chunk dictionaries in fixture payloads.
- Added regression test verifying nTRN translation offset maps into imported voxel coordinates.
- Preserved backward compatibility for existing multi-model and unsupported-chunk tests.
- Kept implementation bounded and non-invasive (translation only, no full scene graph resolver yet).
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`155 passed`)

### Task 22: VOX Multi-part Naming and Grouping
- Commit: `c13180e`
- Added deterministic VOX import naming helper for part labels (`Base Part 01`, `Base Part 02`, ...).
- Added deterministic VOX import grouping helper (`<Base> Import`) for multi-model imports.
- Updated VOX import flow to create a group automatically when importing multiple VOX models.
- Updated VOX import flow to assign each imported part to the created import group.
- Preserved single-model import naming behavior (base filename only).
- Kept fallback naming for empty/missing base names (`Imported VOX`).
- Ensured part numbering width remains stable and readable for larger import counts.
- Preserved active imported part selection behavior after import.
- Preserved existing palette apply behavior after VOX import.
- Kept warnings flow unchanged for unsupported VOX chunks.
- Added regression tests for VOX import naming helper behavior.
- Added regression tests for VOX import grouping helper behavior.
- Kept implementation scoped to import naming/grouping without scene schema changes.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`156 passed`)

### Task 23: Qubicle QB Import Feasibility Slice
- Commit: `a32bd8b`
- Added new QB IO module (`core/io/qb_io.py`) for bounded Qubicle `.qb` import.
- Implemented QB header parsing (version/format/compression/visibility/matrix count).
- Implemented uncompressed matrix parsing for voxel payloads with matrix position offsets.
- Implemented RGBA voxel unpacking and alpha-aware occupancy handling (alpha zero skipped).
- Implemented palette extraction from encountered matrix voxel colors with deterministic indexing.
- Added explicit rejection for compressed QB payloads in this feasibility slice.
- Added public IO exports for QB loaders in `core/io/__init__.py`.
- Added File menu action `Import QB` and wired it to new main-window import flow.
- Added QB import scene integration with deterministic part naming and optional grouping for multi-matrix files.
- Added QB import palette apply behavior and post-import status/warning messaging.
- Added regression test for QB single-matrix import with positional offset mapping.
- Added regression test for compressed QB rejection path.
- Kept scope bounded to core voxel import feasibility (no advanced QB features/compression yet).
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`158 passed`)

### Task 24: Qubicle QB Export Feasibility Slice
- Commit: `4c32f65`
- Added new QB exporter module (`core/export/qb_exporter.py`) for bounded `.qb` write support.
- Implemented QB header/matrix emission for uncompressed single-matrix export payloads.
- Implemented voxel bounds extraction and matrix-position offset emission for negative/positive coordinates.
- Implemented voxel color write path using palette-indexed RGBA packing.
- Implemented empty-scene QB export handling with zero-matrix payload.
- Added export stats model (`QbExportStats`) with voxel count and matrix size reporting.
- Exported QB helpers through `core/export/__init__.py`.
- Added File menu action `Export QB` and wired main-window handler.
- Added QB export status reporting in UI (empty and non-empty paths).
- Preserved existing OBJ/glTF/VOX export flows unchanged.
- Added regression roundtrip test (QB export then QB import) verifying coordinates and palette mapping.
- Added regression test for empty-grid QB export behavior.
- Kept implementation bounded to feasibility slice (single active-part voxel grid export).
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`160 passed`)

### Task 25: Solidify QA Diagnostics
- Commit: `6ada55d`
- Added mesh QA diagnostic fields to part stats (`degenerate_quads`, `non_manifold_edge_hints`).
- Added degenerate-quad detection in stats analysis (quads with fewer than 4 unique vertices).
- Added non-manifold edge risk hint counter (edges referenced by more than two quads).
- Kept diagnostics non-blocking and analysis-only (no mesh generation interruption).
- Preserved existing scene/part triangle/face/edge/vertex/material computations.
- Updated stats panel object label to display QA counters for active part.
- Kept diagnostics compatible with cached-mesh and rebuilt-mesh analysis paths.
- Added regression test with synthetic mesh cache to verify degenerate-quad counter.
- Added regression test with synthetic mesh cache to verify non-manifold edge hint detection.
- Preserved runtime stats label format and scene summary label behavior.
- Kept implementation scoped to diagnostics; no export/tool behavior changes.
- Avoided introducing any new dependencies.
- Maintained existing compute_scene_stats public API shape aside from additive fields.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`161 passed`)

### Task 26: Incremental Rebuild Telemetry
- Commit: `0f4cd4e`
- Added incremental rebuild telemetry fields to part model (`incremental_rebuild_attempts`, `incremental_rebuild_fallbacks`).
- Added attempt counter increments when incremental rebuild path is executed.
- Added fallback counter increments when incremental candidate falls back to full rebuild.
- Added fallback counter increments when dirty volume exceeds incremental threshold.
- Exposed telemetry counters through part stats in analysis layer.
- Updated stats panel object line to display incremental attempt/fallback counters.
- Kept telemetry non-blocking and lightweight (simple integer counters).
- Preserved existing mesh rebuild behavior and correctness checks.
- Preserved existing runtime metrics emission behavior.
- Added regression assertions ensuring incremental attempts are recorded on local edit rebuilds.
- Added regression assertions ensuring attempts are recorded across randomized local edit sequences.
- Kept implementation scoped to telemetry and display only.
- No new dependencies or schema changes introduced.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`161 passed`)

### Task 27: Dense Scene Stress Harness (64/96/128)
- Commit: `f9266bd`
- Extended performance baseline harness with explicit dense-scene tier workloads (`64`, `96`, `128` bounds).
- Added dense-scene measurement helper that scales working volume while keeping sparse fill deterministic.
- Added dedicated perf assertions for `dense_64_seconds`, `dense_96_seconds`, and `dense_128_seconds`.
- Kept thresholds non-blocking via existing multiplier strategy to reduce CI flake risk.
- Updated `tests/perf_baseline.json` with per-tier dense-scene baseline values.
- Added per-tier metric multipliers for dense-scene keys.
- Preserved existing brush/fill/solidify/viewport surrogate baseline checks.
- Preserved existing JSON baseline schema compatibility through additive keys only.
- Kept test runtime bounded by sparse voxel sampling strategy in dense tiers.
- Ensured dense tiers still represent larger workload domains for relative scaling checks.
- Maintained deterministic operation order for repeatable measurement behavior.
- Kept implementation test-only (no runtime/editor behavior changes).
- No dependencies introduced.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`161 passed`)

### Task 28: Frame-Time Hotspot Pass
- Commit: `d083f64`
- Added viewport render-data cache for point/line vertex buffers and voxel count.
- Added cache signature keyed by visible parts, transforms, visibility, and voxel revision counters.
- Added lightweight voxel revision tracking to `VoxelGrid` to drive deterministic cache invalidation.
- Updated `VoxelGrid` mutators to bump revision only when data actually changes.
- Added static render-signature helper for deterministic signature computation and testability.
- Preserved rendering correctness by rebuilding cached buffers whenever signature changes.
- Preserved existing draw pipeline and OpenGL shader behavior.
- Kept cache scope local to viewport render-data hot path only.
- Added regression test verifying voxel-grid revision increments only on real mutations.
- Added regression test verifying render signature changes after voxel revision updates.
- Extended perf surrogate baseline with repeat hot-path check (`viewport_surrogate_repeat_seconds`).
- Updated perf baseline JSON with repeat viewport surrogate thresholds.
- Kept performance assertions conservative to avoid flaky environments.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`163 passed`)

### Task 29: Memory Budget Instrumentation
- Commit: `33b5085`
- Added memory budget fields to part stats (voxel bytes, mesh bytes, total bytes).
- Added memory budget fields to scene stats (voxel bytes, mesh bytes, total bytes).
- Implemented deterministic voxel memory estimate based on active voxel count.
- Implemented deterministic mesh memory estimate based on vertices/quads/face-color arrays.
- Aggregated per-part memory budgets into scene-level totals during stats computation.
- Added memory label formatter for human-readable byte units.
- Updated scene stats label to display total estimated scene memory.
- Updated object stats label to display per-part voxel and mesh memory estimates.
- Preserved existing runtime stats formatting and update flow.
- Kept memory reporting explicitly estimate-oriented (not OS-level allocation exactness).
- Added regression tests for deterministic memory estimate stability.
- Added regression tests for memory label unit formatting behavior.
- Preserved existing scene stats regression assertions and behavior.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`165 passed`)

### Task 30: End-to-End Correctness Sweep
- Commit: `bbfa6b6`
- Added cross-feature command regression for selection move + duplicate with undo/redo sequencing.
- Added extended project IO regression ensuring modern editor-state keys roundtrip cleanly.
- Added VOX import regression combining transform mapping and unknown-chunk warning handling.
- Added glTF regression validating primitive/accessor index consistency across POSITION/NORMAL/UV/COLOR/indices.
- Kept regression additions isolated to test suite with no runtime behavior changes.
- Preserved existing tests and fixtures while extending parity coverage for recently added features.
- Validated command stack behavior under combined workflows instead of single-operation-only tests.
- Validated IO forward stability for expanded editor-state payload variants.
- Validated import pipeline correctness under mixed supported/unsupported chunk scenarios.
- Validated export payload structural integrity for downstream loader compatibility.
- Maintained deterministic fixture construction patterns for reproducible test runs.
- Kept assertions human-readable for quicker triage of parity regressions.
- No dependencies or schema migrations introduced.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`169 passed`)

### Task 31: Interface Polish - Top Toolbar Quick Actions
- Commit: `f79723a`
- Added top toolbar (`quick_actions_toolbar`) to main window for high-frequency actions.
- Added quick actions for `New`, `Open`, `Save`.
- Added quick actions for `Undo`, `Redo`.
- Added quick action for `Solidify`.
- Added quick export actions for `Export OBJ`, `Export glTF`, and `Export VOX`.
- Wired quick-toolbar actions directly to existing main-window handlers.
- Kept existing menu actions intact as source-of-truth pathways.
- Added toolbar labels helper for lightweight regression validation.
- Added regression test verifying expected quick-toolbar action set coverage.
- Preserved existing shortcut behavior and menu layout.
- Kept toolbar non-movable for stable top-level layout.
- No dependency changes.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`170 passed`)

### Task 32: Interface Polish - Status HUD Badges
- Commit: `253bc50`
- Added viewport HUD badge formatter for core editing context state.
- Added badges for tool/mode, pick mode, edit plane, mirror axes, projection, and navigation preset.
- Rendered HUD badges in overlay with distinct color styling for quick glance readability.
- Preserved existing overlay metrics (voxel count/camera/target) and mirror plane label.
- Shifted error overlay line to avoid collision with new badge line.
- Kept badge rendering optional with existing overlay toggle behavior.
- Added regression test validating badge output for representative context state.
- Kept badge logic static and testable (`_hud_badges` helper).
- Preserved all edit/render behavior (display-only change).
- No dependency additions.
- Maintained compatibility with existing mirror overlay helpers.
- Kept formatting compact to avoid excessive viewport clutter.
- Added no new persistence or schema surface.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`171 passed`)

### Task 33: Interface Polish - Command Palette (Quick Search)
- Commit: `f2938a9`
- Added new command palette dialog (`app/ui/dialogs/command_palette_dialog.py`).
- Added command palette launch action in Edit menu.
- Added command palette shortcut binding (`Ctrl+Shift+P`).
- Added command registry in main window with common project/import/export/edit/view actions.
- Added command execution dispatcher to invoke existing handlers from selected command id.
- Added palette filtering helper for case-insensitive quick search with sorted results.
- Kept all commands reachable through original menus and shortcuts (no path removal).
- Added dialogs package init file for explicit module packaging.
- Kept command palette non-destructive; it reuses existing action handlers.
- Added regression test for command palette filter behavior.
- Preserved shortcut help and existing shortcut registration behavior.
- Maintained no-dependency implementation with native Qt widgets.
- Kept integration scoped to UI layer only.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`172 passed`)

### Task 34: Interface Polish - Dock Layout Presets
- Commit: `84752b8`
- Added layout preset setting-key helper with slot validation (`1` and `2`).
- Added View menu actions for saving/loading layout preset 1.
- Added View menu actions for saving/loading layout preset 2.
- Added main-window save-layout-preset handler that stores serialized dock state.
- Added main-window load-layout-preset handler with empty-preset guard messaging.
- Added restore failure fallback to default layout when preset state is invalid/corrupt.
- Added status-bar feedback for successful preset save/load operations.
- Kept existing reset-layout workflow intact.
- Preserved existing geometry/state persistence on close.
- Added regression test for layout preset key helper + slot validation.
- Kept implementation scoped to dock-state presets only (no settings backend changes required).
- No dependency additions.
- Existing menu/dock behavior remains backward compatible.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`173 passed`)

### Task 35: Interface Polish - Theme and Contrast Pass
- Commit: `1bdeb04`
- Added centralized application stylesheet helper for consistent theme/contrast definitions.
- Applied stylesheet at main-window startup for immediate UI visual consistency.
- Tuned menu/menu-bar contrast for clearer hover/selection readability.
- Tuned toolbar button visuals for stronger action affordance.
- Tuned dock title styling for clearer panel hierarchy.
- Tuned form/list input controls for improved edge contrast and legibility.
- Tuned button hover/pressed states for stronger interaction feedback.
- Tuned status bar styling for consistent panel boundary visibility.
- Kept theme implementation lightweight via Qt stylesheet only.
- Preserved existing functional behavior; purely presentation-layer changes.
- Added regression test validating stylesheet includes key widget-class rules.
- Kept high-contrast-friendly color choices in neutral blue/gray palette.
- No new dependencies introduced.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`174 passed`)

### Task 36: Interface Polish - Numeric Field Drag Scrub
- Commit: `0b9802a`
- Added drag-scrub row label widget for numeric transform controls in inspector panel.
- Added horizontal drag detection with per-move pixel delta emission.
- Added transform row labels as active scrub controls for position, rotation, and scale fields.
- Added spinbox scrub handler that maps pixel delta to value delta via spin single-step.
- Added clamp-safe value application helper so scrubbed values stay within spinbox bounds.
- Preserved direct numeric text entry on all transform spinboxes.
- Preserved existing transform-changed signal pathway and status messaging.
- Added drag-scrub tooltip/cursor affordance for discoverable label interaction.
- Kept implementation scoped to inspector transform controls only.
- Added unit test for scrub delta mapping behavior against single-step values.
- Added unit test for scrubbed-value clamping behavior at min/max limits.
- Kept dependency surface unchanged with no new packages.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`176 passed`)

### Task 37: Interface Polish - Tool Hotkey Overlay
- Commit: `6434e82`
- Added modeless in-app hotkey overlay dialog from Edit -> Shortcut Help.
- Added overlay content rendering from current registered shortcut bindings.
- Added close button + non-modal behavior for quick open/close without workflow interruption.
- Added text-selectable hotkey list for quick reference while editing.
- Added shortcut binding registry tracking during shortcut registration.
- Added duplicate shortcut sequence detector helper with case-insensitive comparison.
- Added startup conflict warning log for duplicate shortcut registrations.
- Updated shortcut registration calls to include human-readable labels.
- Preserved all existing shortcut behavior and callback routing.
- Added unit test for duplicate shortcut conflict detection.
- Added unit test for unique shortcut registry no-conflict path.
- Added unit test for hotkey overlay text formatting output.
- Kept implementation dependency-free and UI-scoped.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`179 passed`)

### Task 38: Interface Polish - Precision Input Mode
- Commit: `2e5cc92`
- Added temporary precision modifier for camera orbit/pan/zoom using `Alt` key hold.
- Applied precision scale factor to left-drag navigate orbit sensitivity.
- Applied precision scale factor to middle-button orbit sensitivity.
- Applied precision scale factor to middle-button pan distance in Blender-Mix shift-pan mode.
- Applied precision scale factor to right-button pan movement sensitivity.
- Applied precision scale factor to mouse-wheel zoom sensitivity.
- Added viewport helper for deterministic precision scale factor calculation.
- Added precision-aware transform label drag-scrub behavior in inspector controls.
- Added inspector helper for transform scrub precision factor.
- Preserved default camera and transform movement speed when precision modifier is not held.
- Added regression test for camera precision scale factor behavior (`Alt` vs no modifier).
- Added regression test for inspector scrub precision factor behavior.
- Kept implementation dependency-free and scoped to input sensitivity only.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`181 passed`)

### Task 39: Interface Polish - Startup Workspace Recovery UX
- Commit: `e6e675e`
- Added recent-project settings key helper and startup-choice helper for recovery flows.
- Added recent project path persistence on save/open success paths.
- Added shared `_open_project_path` loader path for reuse by startup and manual open.
- Added startup recovery prompt with explicit actions: Restore Snapshot, Discard Snapshot, Open Recent, Cancel.
- Added startup flow to open recent project when no snapshot exists and user confirms.
- Added startup flow to open recent project directly from recovery prompt while discarding stale snapshot.
- Added startup recovery restore extraction into dedicated helper method for clearer flow control.
- Preserved recovery diagnostic write behavior on snapshot load failure.
- Preserved safe default behavior: cancel keeps snapshot untouched and avoids destructive action.
- Added regression test for startup recovery choice combinations.
- Added regression test for recent project settings key stability.
- Kept implementation scoped to startup UX and project-open flow reuse.
- No dependency changes or schema changes introduced.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`183 passed`)

### Task 40: Interface Polish - Final UX Regression and Operator Pack
- Commit: `COMMIT_PENDING`
- Ran full final gate pass for day-end (`python src/app/main.py` launch smoke + full `pytest -q`).
- Verified gate summary remains green at task close (`183 passed`).
- Refreshed `Doc/NEXT_WORKDAY.md` into operator-validation mode (no new task starts).
- Added explicit operator validation checklist covering viewport/tools/scene/io/export/packaging.
- Added precise startup-recovery validation steps including restore/discard/open-recent/cancel paths.
- Added packaging validation matrix for packaged EXE behavior and key editing/export flows.
- Added packaging evidence capture requirements (artifact path/hash + zip hash + smoke status).
- Updated `Doc/CURRENT_STATE.md` completion percentages and corrected stale feature-status entries.
- Updated `Doc/CURRENT_STATE.md` top risk list to match current implemented baseline.
- Kept scope docs-only for end-of-day operator handoff readiness.
- Preserved no-feature-change requirement in this final polish task.
- No dependency or runtime code changes in this task.
- Gate results:
  - `python src/app/main.py`: PASS (launch smoke)
  - `pytest -q`: PASS (`183 passed`)
