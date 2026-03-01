# ROADMAP_TASKS (Next Day-Cycle Board)

Date: 2026-03-01
Scope: Full workday plan with exactly 30 atomic tasks.
Execution rule: Complete in order (Task 01 -> Task 30), one task per branch, merge to `main` only after gates pass.

## Remaining Tasks

### Task 25: Autosave Debounce on Edit
- Goal: Trigger short-delay snapshot saves after voxel edits in addition to periodic timer.
- Likely files/modules touched: `src/app/ui/main_window.py`, `src/core/io/recovery_io.py`.
- Acceptance criteria (human-testable): Forced close shortly after edit still restores latest change.
- Tests required: Add autosave debounce timing tests.
- Risk/rollback note: Debounce must avoid excessive disk writes.

### Task 26: Recovery Snapshot Version Stamp
- Goal: Add explicit recovery schema/version metadata for safer restore handling.
- Likely files/modules touched: `src/core/io/recovery_io.py`, `src/core/io/project_io.py`.
- Acceptance criteria (human-testable): Incompatible recovery snapshot yields clear prompt and safe skip option.
- Tests required: Add recovery version mismatch tests.
- Risk/rollback note: Keep backward restore path for current snapshot format.

### Task 27: Canonical Source Tree Guardrail
- Goal: Prevent accidental edits under legacy `src/voxel_tool` tree.
- Likely files/modules touched: `README.md`, `Doc/INDEX.md`, optional test/lint guard file.
- Acceptance criteria (human-testable): Contributor docs clearly define canonical runtime path and guardrail is testable.
- Tests required: Add lightweight test/CI check for banned-path edits if feasible.
- Risk/rollback note: If guardrail automation is noisy, keep documentation warning and pre-commit note.

### Task 28: Packaging Script Hardening + Exit Diagnostics
- Goal: Improve packaging script diagnostics and deterministic artifact checks.
- Likely files/modules touched: `tools/package_windows.ps1`, `Doc/PACKAGING_CHECKLIST.md`.
- Acceptance criteria (human-testable): Packaging script outputs clear pass/fail steps and artifact paths.
- Tests required: Add script smoke checklist updates in docs and optional script test harness.
- Risk/rollback note: Preserve existing build path if new checks block valid builds.

### Task 29: Portable Zip + Installer Prep Checklist
- Goal: Add documented portable zip workflow and installer prerequisites (no installer build yet).
- Likely files/modules touched: `Doc/PACKAGING_CHECKLIST.md`, `Doc/NEXT_WORKDAY.md`.
- Acceptance criteria (human-testable): Operator can produce and verify portable zip via checklist.
- Tests required: Add packaging checklist verification steps to daily report template.
- Risk/rollback note: Keep scope to docs/process if build tooling is not ready.

### Task 30: Day-End Full QA + Handoff Pack
- Goal: Execute complete gate, update run docs, and produce operator-ready handoff checklist.
- Likely files/modules touched: `Doc/DAILY_REPORT.md`, `Doc/CURRENT_STATE.md`, `Doc/NEXT_WORKDAY.md`.
- Acceptance criteria (human-testable): App launch, pytest, viewport smoke, IO smoke, export smoke all pass and are documented.
- Tests required: `pytest -q` full run plus manual smoke checklist record.
- Risk/rollback note: If any gate fails, stop merges and document blocker with next experiment.

## Completed Today
### Task 01: Unify Edit Plane Axis Contract
- Commit: `6658fd1`
- Added shared axis-plane intersection helper (`intersect_axis_plane`) in voxel raycast core for consistent plane hit math.
- Wired viewport plane-hit placement (`_screen_to_plane_cell`) to the shared helper and canonical edit-plane constants.
- Updated world-grid rendering to use the same canonical edit plane (`z=0`) as default placement operations.
- Added regression tests for plane-hit semantics: valid hit, parallel ray miss, and behind-origin miss cases.
- Kept camera/orbit input behavior unchanged to avoid introducing movement regressions in this task.
- Preserved brush and non-brush command behavior scope (no tool-mode expansion in Task 01).
- Maintained mirror/palette/export logic untouched to keep task scope atomic.
- Confirmed startup viewport initialization remains successful with active OpenGL pipeline.
- Verified task does not change persisted project schema or editor-state compatibility.
- Established groundwork for Task 02/03 shared targeting improvements with reusable core helper.
- Kept implementation minimal and production-safe with no new dependencies.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`85 passed`)

### Task 02: Non-Brush 3D Target Resolver v1
- Commit: `0181e89`
- Added shared non-brush target resolver (`resolve_shape_target_cell`) in voxel raycast core with surface-adjacent paint and surface-hit erase behavior.
- Updated viewport non-brush execution paths (box/line/fill) to use shared 3D ray-hit targeting with plane fallback.
- Updated line/box drag preview targeting to reuse the same resolver path, keeping preview/apply behavior aligned.
- Removed hard dependency on direct `_screen_to_plane_cell()` for non-brush tool application path.
- Preserved brush targeting behavior unchanged to avoid cross-tool regressions in this task.
- Preserved fill threshold and command transaction behavior while swapping target resolution source.
- Kept default fallback behavior on empty space (plane fallback) for continuity before Task 03 mode expansion.
- Added raycast unit tests for non-brush resolver behavior in paint, erase, and fallback scenarios.
- Confirmed no project schema, palette, export, or packaging code changes were introduced.
- Established shared targeting foundation for Task 03 pick-mode parity work.
- Maintained production-safe scope with no dependency additions.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`88 passed`)

### Task 03: Apply Pick Mode to Line/Box/Fill
- Commit: `47a3437`
- Updated non-brush target resolution path to respect global pick mode semantics.
- Added plane-fallback gating for non-brush tools: fallback is enabled only in `Plane Lock` and paint mode.
- Ensured `Surface` mode for non-brush tools now rejects empty-space paint targets (no implicit plane placement).
- Kept erase behavior surface-hit-only, matching existing brush-mode semantics.
- Reused shared resolver path so preview and apply behavior stay aligned under pick-mode changes.
- Avoided UI refactors by leveraging existing pick-mode control already present in Tools panel.
- Preserved command stack, fill threshold, and mirror workflows untouched in this task.
- Added regression coverage for no-fallback target resolution behavior (shape resolver without fallback returns `None`).
- Confirmed no changes to project schema, exporter behavior, or packaging scripts.
- Completed scope exactly for pick-mode parity without introducing edit-plane selector changes (Task 04).
- Implementation remains dependency-free and production-safe.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`89 passed`)

### Task 04: Edit Plane Selector UI (XY/YZ/XZ)
- Commit: `deb5010`
- Added explicit edit-plane state (`xy/yz/xz`) in `AppContext` with validation API.
- Added Tools panel edit-plane selector (`XY/YZ/XZ`) and change signal wiring.
- Wired MainWindow to react to edit-plane changes with status updates and UI refresh.
- Persisted `edit_plane` in editor-state capture/apply flow for save/open continuity.
- Updated viewport plane hit-testing to use selected plane axis dynamically.
- Updated grid rendering to visualize the currently selected edit plane orientation.
- Preserved existing pick-mode and mirror behavior while extending plane-selection capability.
- Added app-context validation test coverage for edit-plane API.
- Added project IO roundtrip coverage that includes `editor_state.edit_plane`.
- Kept task scope atomic without introducing orthographic or camera-control changes.
- Implementation remained dependency-free and aligned to roadmap sequence.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`90 passed`)

### Task 05: Export Options Truthfulness Pass
- Commit: `a13d94a`
- Added explicit export-dialog capability mapping to control per-format option visibility.
- Restricted OBJ-only controls (greedy/triangulate/pivot) to OBJ export dialog only.
- Hid unsupported scale preset control for glTF and VOX dialogs.
- Updated option serialization flow so non-supported controls are not applied to non-OBJ formats.
- Updated glTF/VOX status messaging to remove misleading scale text.
- Preserved existing OBJ behavior and session option persistence for supported controls.
- Added focused tests for export-dialog capability mapping (OBJ vs glTF vs VOX).
- Confirmed no changes to exporter geometry logic in this task (format truthfulness only).
- Kept implementation in UI/options layer without dependency changes.
- Preserved compatibility with upcoming Task 06 (glTF scale support) by centralizing capability mapping.
- Maintained atomic scope and production-safe behavior.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`93 passed`)

### Task 06: glTF Scale Preset Application
- Commit: `b6a6219`
- Extended glTF exporter API to accept `scale_factor` and apply it to exported vertex positions.
- Wired MainWindow glTF export path to pass scale factor derived from current export preset.
- Updated glTF export status messaging to include applied scale preset now that it is functional.
- Updated export dialog capability mapping so glTF exposes scale preset control.
- Preserved VOX dialog behavior (scale remains hidden there until explicit support exists).
- Kept OBJ export behavior unchanged while sharing existing preset conversion helper.
- Added numeric regression test validating glTF accessor bounds scale proportionally with scale factor.
- Updated export-capability tests to reflect glTF scale support.
- Confirmed exporter output remains valid JSON glTF with unchanged topology/indices semantics.
- Avoided introducing binary layout changes beyond scaled position values.
- Maintained dependency-free implementation and roadmap-aligned scope.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`94 passed`)

### Task 07: glTF Normals Export v1
- Commit: `6d120b0`
- Added per-vertex normal generation for glTF exports by accumulating mesh quad normals and normalizing per vertex.
- Extended glTF buffer layout to include dedicated normal data block and accessor.
- Updated glTF primitive attributes to emit both `POSITION` and `NORMAL`.
- Updated index accessor wiring after introducing normals buffer view.
- Preserved triangle topology and index ordering while extending attribute payload.
- Added default fallback normal for degenerate/zero-length accumulations to keep export valid.
- Kept exporter output as JSON `.gltf` with embedded data URI payload (no format migration).
- Updated glTF tests to assert normal attribute presence.
- Added count parity assertion between position and normal accessors.
- Preserved scale-factor support added in Task 06 without behavioral regression.
- Kept implementation dependency-free and contained to exporter/test scope.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`94 passed`)

### Task 08: Project IO Forward-Compatibility Loader
- Commit: `7dd9f09`
- Removed strict rejection of unknown top-level project JSON keys during load.
- Preserved required-key validation and existing structural schema checks.
- Kept scene/part/editor_state parsing behavior unchanged for known fields.
- Added forward-compat regression test with extra top-level metadata.
- Verified legacy schema pathways (`scene` missing / root `voxels`) remain intact.
- Maintained explicit error behavior for invalid required-key scenarios.
- Avoided introducing metadata pass-through persistence in this task (load tolerance only).
- Kept JSON save format stable to avoid unplanned migration behavior.
- Confirmed no impact to runtime editor-state capture/apply logic.
- Scope remained atomic to project IO compatibility objective.
- Implementation remained dependency-free and production-safe.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`95 passed`)

### Task 09: Scene IDs Migration to UUID
- Commit: `cba9626`
- Replaced counter-based part ID generation with UUID-backed IDs for newly created parts.
- Replaced counter-based group ID generation with UUID-backed IDs for newly created groups.
- Preserved compatibility with legacy scene files that already contain counter-style IDs.
- Verified loader behavior remains stable when reading legacy IDs from project JSON.
- Added mixed legacy/new-ID regression test path (load legacy `part-1`, then add a new UUID-based part).
- Kept save/load schema unchanged (IDs remain opaque strings in project payload).
- Avoided introducing any migration step that rewrites existing legacy IDs.
- Preserved part/group operations (duplicate/delete/reorder/assign) without API changes.
- Maintained deterministic behavior for active-part selection despite UUID migration.
- Scoped changes to ID generation + compatibility tests only.
- Kept implementation dependency-free and production-safe.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`96 passed`)

### Task 10: Non-Brush Preview Accuracy Sweep
- Commit: `2c732ed`
- Added shared shape-plane cell generator (`build_shape_plane_cells`) for box/line preview calculations.
- Updated viewport drag-preview path to use shared shape helper rather than duplicated shape branching.
- Kept command execution logic unchanged while aligning preview generation source of truth.
- Added parity test verifying helper dispatch matches existing box/line generators.
- Added parity test verifying mirrored preview cells match actual applied voxels for box operations.
- Added parity test verifying mirrored preview cells match actual applied voxels for line operations.
- Preserved pick-mode and edit-plane behavior from prior tasks while tightening preview correctness confidence.
- Avoided scope creep into fill/brush logic for this task.
- Kept implementation local to command helpers + tests + preview path.
- No schema, IO, or export behavior changed.
- Dependency footprint unchanged.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`98 passed`)

### Task 11: Orthographic Camera Mode v1
- Commit: `61a34d1`
- Added camera projection state to `AppContext` with validation (`perspective` / `orthographic`).
- Added View menu toggle for orthographic projection mode.
- Wired projection toggle through MainWindow to update viewport rendering immediately.
- Added editor-state persistence for camera projection mode.
- Updated editor-state restore logic to apply persisted projection mode safely.
- Extended viewport projection matrix builder to support orthographic projection path.
- Kept existing perspective camera behavior unchanged as default mode.
- Added app-context validation test for camera projection setter.
- Extended project IO editor_state roundtrip test with `camera_projection`.
- Preserved tool behavior and input interactions while changing projection math only.
- Implementation remained dependency-free and roadmap-scoped.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`99 passed`)

### Task 12: Camera Preset + Plane Selector Integration
- Commit: `1489b01`
- Added explicit view-preset to edit-plane mapping helper (`top/bottom->XZ`, `left/right->YZ`, `front/back->XY`).
- Updated view preset action handler to apply mapped edit plane automatically.
- Improved status messaging to include both selected view preset and resulting edit plane.
- Triggered UI refresh after preset selection so Tools panel reflects updated plane state immediately.
- Preserved camera preset orientation logic while integrating plane-selection context.
- Kept edit-plane selector manual override available after preset-based updates.
- Added unit tests for preset-to-plane mapping across all preset groups.
- Maintained orthographic/perspective handling unchanged from Task 11.
- Avoided changes to command execution and picking logic in this task.
- Implementation remained dependency-free and isolated to UI/view-flow alignment.
- Scope aligned to roadmap acceptance for orientation feedback polish.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`102 passed`)

### Task 13: Fill 3D Connectivity Mode (Optional Toggle)
- Commit: `aafece9`
- Added fill connectivity mode state in `AppContext` (`plane` / `volume`) with validation API.
- Added Tools panel connectivity selector (`Plane` / `3D`) scoped to fill workflow.
- Wired fill connectivity UI signal through MainWindow with status feedback refresh.
- Added editor-state persistence for fill connectivity mode.
- Extended editor-state restore logic to apply persisted fill connectivity safely.
- Updated fill command execution to branch between plane flood and volume flood logic.
- Added bounded 3D flood-fill implementation with threshold protection.
- Preserved existing plane fill behavior as default mode.
- Added tests validating plane-vs-volume fill behavior differences.
- Added app-context validation coverage for fill connectivity setter.
- Extended project IO editor_state roundtrip test with fill connectivity state.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`104 passed`)

### Task 14: Brush Size Cycle Hotkey
- Commit: `2def624`
- Added deterministic brush-size cycle helper for 1->2->3->1 progression.
- Added brush-size cycle shortcut binding (`]`) in main window shortcut map.
- Wired shortcut action to update context brush size and refresh UI immediately.
- Added status feedback message when cycling brush size from keyboard.
- Preserved existing brush profile controls in Tools panel (hotkey complements UI control).
- Kept brush shape and tool-mode behavior unchanged.
- Added tests validating brush-size cycle progression and invalid-input fallback behavior.
- Avoided key collisions with existing tool/mode/palette shortcuts.
- Kept implementation scoped to shortcut behavior only (no command logic changes).
- Maintained dependency-free implementation.
- Scope matches roadmap acceptance for quick brush-size cycling.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`106 passed`)

### Task 15: Group Membership Visibility in Inspector
- Commit: `1314998`
- Added scene API helper (`group_names_for_part`) to query ordered group memberships for a part.
- Added active-part group membership summary label to inspector panel.
- Updated inspector refresh path to render concise membership summary text.
- Added fallback membership text when active part is not in any group.
- Preserved existing group assignment/unassignment controls and behavior.
- Preserved group visibility/lock controls and scene mutation logic unchanged.
- Added scene regression test validating membership summary ordering/content.
- Kept implementation lightweight (read-only summary, no interactive chips yet).
- Avoided UI layout refactor beyond adding one summary label row.
- Implementation remained dependency-free and roadmap-scoped.
- No project schema changes were introduced.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`107 passed`)

### Task 16: Palette Import/Export GPL Support v1
- Commit: `23e9ee7`
- Added palette preset IO support for GPL (`.gpl`) alongside existing JSON format.
- Added GPL writer with standard header and RGB row emission.
- Added GPL loader with header validation and robust row parsing.
- Added extension-based format dispatch in palette save/load APIs.
- Added file dialog filters for both JSON and GPL palette formats.
- Preserved existing JSON preset behavior and schema compatibility.
- Added GPL roundtrip test coverage for save/load fidelity.
- Added GPL invalid-header validation test coverage.
- Kept palette normalization behavior consistent across JSON and GPL paths.
- Avoided introducing palette metadata migration in this task.
- Implementation remained dependency-free and roadmap-scoped.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`109 passed`)

### Task 17: Palette Slot Lock Protection
- Commit: `5f23b46`
- Added palette slot lock state to `AppContext` with lock/unlock APIs.
- Added lock state persistence in editor-state capture/apply flow.
- Added active-slot lock toggle control in palette panel.
- Added lock guards that block RGB edits on locked active slot.
- Added lock guards that block remove action when active slot is locked.
- Added lock guards that block swap operations involving locked slots.
- Added lock-index maintenance logic on add/remove operations to keep lock state aligned to slot indices.
- Preserved existing palette add/remove/swap/edit behavior for unlocked slots.
- Added app-context lock API regression test coverage.
- Extended project IO editor_state roundtrip test with locked slot list.
- Kept implementation dependency-free and scoped to palette safety behavior.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`110 passed`)

### Task 18: OBJ Multi-Material Export Option
- Commit: `2b7b00c`
- Added OBJ export option to split materials by face color index.
- Added OBJ export dialog control (`Split Materials By Color`) for OBJ path.
- Wired UI export options into OBJ exporter multi-material strategy.
- Extended MTL writer to emit per-color material entries when multi-material mode is enabled.
- Added face-material switching (`usemtl`) during OBJ face emission by face color index.
- Preserved single-material default behavior when option is disabled.
- Kept existing UV/vertex-color output paths compatible with new material mode.
- Added helper for used face-color index extraction to minimize emitted materials.
- Added regression test asserting multi-material `newmtl`/`usemtl` output presence.
- Maintained backward-compatible `voxel_default` material naming for color index 0.
- Implementation remained dependency-free and exporter-scoped.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`111 passed`)

### Task 19: OBJ Vertex Color Policy Clarification
- Commit: `5dc16e8`
- Added explicit OBJ vertex-color policy option (`first_face` / `last_face`) to exporter options.
- Kept deterministic default policy as `first_face` for backward compatibility.
- Added policy validation with clear error for unsupported mode values.
- Wired vertex-color assignment logic through explicit policy branch instead of implicit behavior.
- Preserved existing vertex-color extension output format (`v x y z r g b`).
- Added shared-vertex fixture test validating `first_face` behavior.
- Added shared-vertex fixture test validating `last_face` behavior.
- Kept OBJ material/UV writing behavior unchanged in this task.
- Avoided topology splitting or vertex duplication changes for this iteration.
- Implementation remained dependency-free and exporter-scoped.
- Clarified behavior through tests as executable policy documentation.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`113 passed`)

### Task 20: VOX Import Unsupported-Chunk Diagnostics
- Commit: `8cca40f`
- Added warning-capable VOX loader path (`load_vox_models_with_warnings`) that reports unsupported chunk IDs.
- Kept existing `load_vox_models` API backward-compatible by delegating and discarding warnings.
- Added unsupported chunk collection logic in parser while preserving permissive import behavior.
- Updated VOX import UI flow to consume warning-capable loader path.
- Added user-facing warning dialog when unsupported chunks are encountered during import.
- Preserved successful import behavior for supported model/palette chunks.
- Added parser test using synthetic VOX payload with unknown chunk (`nTRN`) and warning assertion.
- Added compatibility assertion that legacy loader wrapper still works on same payload.
- Ensured unsupported chunk diagnostics do not block import success path.
- Kept implementation dependency-free and parser/UI-scoped.
- Fixed one indentation regression in import handler and re-ran full gate successfully.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`114 passed`)

### Task 21: Incremental Solidify Stress Equivalence Expansion
- Commit: `4a155e1`
- Added multi-seed randomized localized-edit equivalence test for incremental vs full rebuild.
- Stress test exposed real divergence cases in incremental patch merge path.
- Added safety check in incremental rebuild path comparing mesh signatures against full rebuild.
- Added automatic fallback to full rebuild when incremental signature diverges.
- Preserved incremental path for matching cases while prioritizing correctness.
- Kept dirty-bound threshold behavior unchanged.
- Added shared mesh-signature helper in solidify module for correctness checks.
- Maintained active part cache update flow and dirty-bound clearing behavior.
- Strengthened reliability for export/stats consumers relying on mesh cache correctness.
- Preserved dependency-free implementation.
- Task includes corrective stabilization prompted by new stress coverage.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`115 passed`)

### Task 22: Viewport Per-Frame Data Caching
- Commit: `0a5ea93`
- Reduced redundant per-frame visibility traversal in `paintGL` by building render buffers and voxel count in one pass.
- Added unified helper that returns point vertices, line vertices, and visible voxel count together.
- Replaced separate per-frame calls that previously recomputed visibility data for count and render buffers.
- Preserved frame metrics emission and overlay behavior after data-path consolidation.
- Kept existing scene iteration semantics (visible parts only) unchanged.
- Avoided altering frame-to-voxels camera framing logic in this task.
- Added viewport-surrogate performance timing path to perf baseline harness.
- Extended perf baseline JSON with viewport-surrogate threshold.
- Preserved conservative non-blocking multiplier strategy in this task.
- Kept implementation dependency-free and low-risk.
- No project schema or export behavior changes introduced.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`115 passed`)

### Task 23: Performance Gate Tightening (CI-friendly)
- Commit: `4ebaf93`
- Tightened global perf regression multiplier from 20x to 12x baseline.
- Added per-metric multipliers for brush/fill/solidify/viewport-surrogate metrics.
- Updated perf harness assertions to consume metric-specific multipliers with fallback to global multiplier.
- Preserved non-blocking philosophy while increasing regression sensitivity.
- Kept baseline thresholds conservative enough to remain stable on current machine.
- Retained existing perf metrics and baseline file structure compatibility.
- Added tiered budget behavior without introducing external benchmarking dependencies.
- No runtime/editor code changes in this task (test-gate hardening only).
- Maintained deterministic baseline parsing and float conversion safeguards.
- Prepared harness for further tightening in future cycles by metric.
- Scope aligns with roadmap risk note for CI-friendly tightening.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`115 passed`)

### Task 24: Runtime Stats Label Clarity Pass
- Commit: `TASK24_HASH_PENDING`
- Updated stats label wording to clearly separate scene-level vs active-part voxel context.
- Renamed active voxel label to `Active Part Voxels` for explicit scope.
- Extended runtime row to include both `scene voxels` and `active-part voxels`.
- Added dedicated runtime-label formatting helper for deterministic text generation.
- Updated main window runtime updates to provide both scene voxel totals and active-part voxel counts.
- Preserved existing scene/object triangle/face/edge/bounds statistics output.
- Added unit test validating runtime label includes both scene and active-part scopes.
- Kept runtime metrics sources unchanged (frame/rebuild timings preserved).
- Avoided UI layout or panel hierarchy refactors in this task.
- Implementation remained dependency-free and roadmap-scoped.
- Human-facing stats readability improved for multi-part scenes.
- Smoke tests passed on branch:
  - `python src/app/main.py` (launch succeeded; app stayed open until timeout)
  - `pytest -q` (`116 passed`)
