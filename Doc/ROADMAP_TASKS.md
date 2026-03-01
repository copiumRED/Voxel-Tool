# ROADMAP_TASKS (Next Day-Cycle Board)

Date: 2026-03-01
Scope: Full workday plan with exactly 30 atomic tasks.
Execution rule: Complete in order (Task 01 -> Task 30), one task per branch, merge to `main` only after gates pass.

## Remaining Tasks

### Task 05: Export Options Truthfulness Pass
- Goal: Show only options that actually affect each export format.
- Likely files/modules touched: `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): glTF/VOX dialogs no longer imply unsupported scale/material options.
- Tests required: Add dialog option visibility tests by format.
- Risk/rollback note: If dialog complexity increases, retain core options and defer advanced controls.

### Task 06: glTF Scale Preset Application
- Goal: Apply export scale presets to glTF output positions.
- Likely files/modules touched: `src/core/export/gltf_exporter.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Unity vs Unreal preset produces expected scaled geometry.
- Tests required: Add glTF numeric coordinate scale regression test.
- Risk/rollback note: If binary payload alignment breaks, keep JSON path with tested alignment padding.

### Task 07: glTF Normals Export v1
- Goal: Add vertex normals to glTF primitive attributes.
- Likely files/modules touched: `src/core/export/gltf_exporter.py`, `src/core/meshing/mesh.py`.
- Acceptance criteria (human-testable): Imported glTF shading is consistent in external viewer.
- Tests required: Add glTF accessor test for `NORMAL` and count parity.
- Risk/rollback note: If normal generation is unstable, gate behind exporter option default-on after validation.

### Task 08: Project IO Forward-Compatibility Loader
- Goal: Allow unknown JSON keys without failing project load.
- Likely files/modules touched: `src/core/io/project_io.py`.
- Acceptance criteria (human-testable): Project with extra metadata opens successfully.
- Tests required: Add project schema compatibility tests with unknown keys.
- Risk/rollback note: Preserve strict validation for required structural keys.

### Task 09: Scene IDs Migration to UUID
- Goal: Replace counter-based part/group IDs with UUID generation while loading legacy IDs.
- Likely files/modules touched: `src/core/scene.py`, `src/core/io/project_io.py`, tests.
- Acceptance criteria (human-testable): New parts/groups receive UUIDs; old projects still load.
- Tests required: Add mixed legacy/UUID load-save roundtrip tests.
- Risk/rollback note: Keep backward-compatible parse path for counter IDs.

### Task 10: Non-Brush Preview Accuracy Sweep
- Goal: Ensure ghost previews exactly match applied cells across plane and surface modes.
- Likely files/modules touched: `src/app/viewport/gl_widget.py`, `src/core/commands/demo_commands.py`.
- Acceptance criteria (human-testable): In 10+ manual drags, committed result matches preview every time.
- Tests required: Add preview-vs-command helper equivalence tests.
- Risk/rollback note: If mismatch persists for one shape, temporarily disable that preview with warning.

### Task 11: Orthographic Camera Mode v1
- Goal: Add orthographic projection toggle for precision modeling.
- Likely files/modules touched: `src/app/viewport/gl_widget.py`, `src/app/ui/main_window.py`, `src/app/app_context.py`.
- Acceptance criteria (human-testable): User can toggle ortho/perspective and continue editing without tool breakage.
- Tests required: Add editor-state persistence test for projection mode.
- Risk/rollback note: If orbit feels unusable, add orthographic pan/zoom-only fallback behavior.

### Task 12: Camera Preset + Plane Selector Integration
- Goal: Align view presets with active edit plane and improve orientation feedback.
- Likely files/modules touched: `src/app/ui/main_window.py`, `src/app/viewport/gl_widget.py`.
- Acceptance criteria (human-testable): Switching presets updates expected edit plane hints and remains intuitive.
- Tests required: Add preset mapping unit tests.
- Risk/rollback note: Keep existing preset values as fallback if mapping confusion appears.

### Task 13: Fill 3D Connectivity Mode (Optional Toggle)
- Goal: Add fill mode toggle between plane-connected and full 3D-connected regions.
- Likely files/modules touched: `src/core/commands/demo_commands.py`, `src/app/ui/panels/tools_panel.py`, `src/app/app_context.py`.
- Acceptance criteria (human-testable): User can choose fill scope and see expected region behavior.
- Tests required: Add fill mode tests for plane vs 3D connectivity.
- Risk/rollback note: Default remains current bounded plane fill if 3D mode risks performance.

### Task 14: Brush Size Cycle Hotkey
- Goal: Add keyboard shortcut to cycle brush size quickly.
- Likely files/modules touched: `src/app/ui/main_window.py`, `src/app/ui/panels/tools_panel.py`.
- Acceptance criteria (human-testable): Hotkey cycles 1->2->3->1 and updates UI immediately.
- Tests required: Add shortcut handling tests.
- Risk/rollback note: Avoid conflicts with existing shortcuts.

### Task 15: Group Membership Visibility in Inspector
- Goal: Show active part group memberships directly in inspector for quicker workflow.
- Likely files/modules touched: `src/app/ui/panels/inspector_panel.py`.
- Acceptance criteria (human-testable): Selecting a part clearly reveals its group memberships.
- Tests required: Add inspector model-view tests for membership display.
- Risk/rollback note: Keep simple read-only label if interactive chips are too large for task scope.

### Task 16: Palette Import/Export GPL Support v1
- Goal: Add GPL palette format import/export alongside JSON.
- Likely files/modules touched: `src/core/io/palette_io.py`, `src/app/ui/panels/palette_panel.py`.
- Acceptance criteria (human-testable): GPL file can be imported and re-exported with color fidelity.
- Tests required: Add GPL parser/writer roundtrip tests.
- Risk/rollback note: Keep strict parser with clear error messages for malformed GPL files.

### Task 17: Palette Slot Lock Protection
- Goal: Prevent accidental overwrite/removal of protected palette slots (user toggle).
- Likely files/modules touched: `src/app/ui/panels/palette_panel.py`, `src/app/app_context.py`.
- Acceptance criteria (human-testable): Locked slot cannot be edited/removed until unlocked.
- Tests required: Add palette lock behavior tests.
- Risk/rollback note: If state complexity grows, scope lock to active slot only for v1.

### Task 18: OBJ Multi-Material Export Option
- Goal: Add optional per-color material splitting in OBJ/MTL output.
- Likely files/modules touched: `src/core/export/obj_exporter.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Multi-color model exports with multiple materials and expected assignments.
- Tests required: Add OBJ/MTL content tests for `newmtl` and `usemtl` mapping.
- Risk/rollback note: Keep existing single-material path as default fallback.

### Task 19: OBJ Vertex Color Policy Clarification
- Goal: Make vertex color behavior deterministic when faces with different colors share vertices.
- Likely files/modules touched: `src/core/export/obj_exporter.py`.
- Acceptance criteria (human-testable): Export behavior matches documented policy and test fixtures.
- Tests required: Add mixed-color shared-vertex fixture test.
- Risk/rollback note: If per-face policy requires topology split, guard behind option.

### Task 20: VOX Import Unsupported-Chunk Diagnostics
- Goal: Report unsupported VOX chunks (transform/hierarchy) clearly to user.
- Likely files/modules touched: `src/core/io/vox_io.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Import completes with warning listing unsupported chunk types.
- Tests required: Add parser test for warning collection on synthetic chunks.
- Risk/rollback note: Keep import permissive; warnings must not crash flow.

### Task 21: Incremental Solidify Stress Equivalence Expansion
- Goal: Increase confidence in incremental rebuild by randomized equivalence testing.
- Likely files/modules touched: `tests/test_solidify_incremental.py`, `src/core/meshing/solidify.py`.
- Acceptance criteria (human-testable): Randomized localized edit sequences produce same mesh signature as full rebuild.
- Tests required: Add multi-seed equivalence tests.
- Risk/rollback note: If inconsistencies found, auto-fallback to full rebuild for affected bounds cases.

### Task 22: Viewport Per-Frame Data Caching
- Goal: Reduce redundant visible-voxel recomputation in each paint cycle.
- Likely files/modules touched: `src/app/viewport/gl_widget.py`.
- Acceptance criteria (human-testable): Dense scene interaction is visibly smoother; no rendering regressions.
- Tests required: Extend perf baseline with viewport draw-time surrogate benchmark.
- Risk/rollback note: Invalidate cache aggressively on edits to avoid stale draws.

### Task 23: Performance Gate Tightening (CI-friendly)
- Goal: Reduce permissive perf multiplier and add tiered thresholds.
- Likely files/modules touched: `tests/perf_baseline.json`, `tests/test_perf_baseline.py`.
- Acceptance criteria (human-testable): Perf tests remain stable locally while catching meaningful regressions.
- Tests required: Update perf baseline tests with tiered budgets.
- Risk/rollback note: If flakiness rises, tune percentile-based tolerance.

### Task 24: Runtime Stats Label Clarity Pass
- Goal: Distinguish active-part vs scene-level runtime stats.
- Likely files/modules touched: `src/app/ui/panels/stats_panel.py`, `src/app/ui/main_window.py`.
- Acceptance criteria (human-testable): Stats panel clearly labels scene vs active-part values.
- Tests required: Add stats panel formatting tests.
- Risk/rollback note: Keep current row if formatting work exceeds scope.

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
