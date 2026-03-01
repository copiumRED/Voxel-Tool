# CURRENT_STATE

Date: 2026-03-01
Branch baseline: `main`

## Phase Completion Estimates
- Phase 0 (Foundations): **97%**
- Phase 1 (Voxel MVP + Qubicle-competitive workflow): **92%**
- Phase 2 (Mesh Edit MVP): **9%**

Reasoning:
- Phase 0 is nearly complete: app shell, viewport, scene/part model, project IO, export entry points, tests, and packaging scripts are present and runnable.
- Phase 1 has broad feature coverage but still misses several parity-critical behaviors (true 3D edit targeting for non-brush tools, palette/material parity, robust export correctness, and workflow polish).
- Phase 2 is still mostly unimplemented by design: no half-edge edit mode, no vertex/edge/face selection workflows.

## Correction vs Prior Docs
- Correction 1: prior docs describe broad "Qubicle parity" progress, but code truth shows important gaps remain in targeting behavior and edit-plane semantics.
- Correction 2: prior docs reported export options as mostly complete; current code applies scale only for OBJ and does not apply scale to glTF/VOX output.
- Correction 3: prior docs implied strong import parity; VOX import supports SIZE/XYZI/RGBA but not transform/hierarchy chunks common in richer VOX scenes.
- Correction 4: prior docs mention near-finished viewport UX parity; current viewport has view presets but no orthographic projection mode.
- Correction 5: prior docs emphasize current-path stability, but duplicate source trees (`src/app` and `src/voxel_tool`) still create maintenance risk.
- Correction 6: Task 01 completed canonical edit-plane alignment by wiring grid rendering and plane-hit targeting to the same `z=0` contract.

## Implemented vs Not Implemented

### UI
Implemented:
- Main window with File/Edit/View/Voxels/Debug menus.
- Tools panel: shape/mode, brush profile, pick mode, mirror + offsets.
- Inspector panel: part add/rename/duplicate/delete, move up/down, visibility/lock, transform fields, grouping controls.
- Palette panel: swatches, RGB edit, add/remove/swap, save/load preset.
- Stats panel with scene/object stats and runtime metrics.

Not Implemented:
- Shortcut customization UI.
- Palette metadata/tagging and richer preset browser.
- Contextual tooltip/help system beyond static hints.
- Orthographic toggle UX.

### Project/IO
Implemented:
- JSON project save/load with scene parts, groups, editor state.
- Legacy voxels field fallback path.
- Autosave snapshot + startup recovery prompt.

Not Implemented:
- Forward-compatible schema handling for unknown keys.
- Project migration/version strategy beyond strict schema acceptance.
- Import/export of full scene transform metadata from VOX ecosystem formats.

### Voxels
Implemented:
- Sparse voxel grid storage.
- Paint/erase, box, line, fill commands.
- Mirror XYZ + per-axis offset expansion.
- Brush size/shape (cube/sphere).

Not Implemented:
- Volume (3D) box/line/fill operations.
- Layer/part-level voxel masking and selection sets.
- Advanced brush falloff/noise/smoothing profiles.

### Tools
Implemented:
- Brush continuous drag with transaction-grouped undo.
- Fill safety threshold.
- Pick mode for brush (`surface` / `plane_lock`).

Not Implemented:
- Full pick-mode parity for line/box/fill.
- Face-normal/axis lock editing controls.
- Selection tools and transform gizmo for voxel subsets.

### Viewport
Implemented:
- OpenGL viewport, grid, orbit/pan/zoom, frame/reset.
- View presets (top/front/left/right/back/bottom).
- Grid visibility/spacing and camera snap settings.
- Hover/ghost previews and mirror guides.

Not Implemented:
- Orthographic camera mode.
- Robust large-scene LOD/culling strategy.
- Multi-plane editing workflow UI.

### Export
Implemented:
- OBJ export with greedy/triangulate toggles, pivot mode, UV output, MTL output, vertex-color extension.
- glTF export (geometry-only baseline).
- VOX export and VOX import (single/multi-model basic chunks).

Not Implemented:
- FBX export.
- glTF normals/UV/color/material support.
- OBJ per-palette material strategy and strict DCC compatibility path.
- Qubicle `.qb` import/export.

### Perf
Implemented:
- Runtime frame/rebuild metrics in Stats panel.
- Perf baseline test harness.
- Incremental mesh rebuild v1 using dirty bounds.

Not Implemented:
- Performance budget enforcement thresholds in CI.
- Memory profiling dashboard.
- Chunked meshing/streaming strategy for very large scenes.

### Packaging
Implemented:
- PyInstaller spec + packaging script.
- Packaged EXE launch smoke path.
- Packaging checklist doc.

Not Implemented:
- Installer build (Inno Setup or equivalent).
- Portable zip artifact pipeline with hash/signing checks.
- Clean-machine matrix validation record.

## Top 10 Known Issues / Bugs (Ranked)
1. Palette slot lock protection is not implemented
- Symptoms: accidental edits/removals of important palette slots cannot be prevented.
- Suspected root cause: palette panel has no lock state model per slot.
- Exact files: `src/app/ui/panels/palette_panel.py`, `src/app/app_context.py`.
- Fastest confirmation: attempt to lock a slot; no lock control exists.

2. Pick mode only affects brush, not line/box/fill
- Symptoms: toggling `Surface` vs `Plane Lock` changes brush behavior only.
- Suspected root cause: non-brush handlers do not call surface ray-hit resolver.
- Exact files: `src/app/viewport/gl_widget.py`, `src/app/ui/panels/tools_panel.py`.
- Fastest confirmation: toggle pick mode and run box/line/fill; behavior remains unchanged.

3. Non-brush tool plane selection is not user-configurable yet
- Symptoms: line/box/fill operate on canonical plane only and cannot switch XY/YZ/XZ interactively.
- Suspected root cause: no active edit-plane selector in context/UI.
- Exact files: `src/app/viewport/gl_widget.py`, `src/app/ui/panels/tools_panel.py`, `src/app/app_context.py`.
- Fastest confirmation: attempt to change non-brush edit plane in UI (control does not exist).

4. glTF export ignores scale preset and outputs positions/indices only
- Symptoms: scale preset shown in UI but does not affect glTF geometry; no normals/UV/colors/materials.
- Suspected root cause: exporter API lacks options and writes only POSITION + indices.
- Exact files: `src/app/ui/main_window.py`, `src/core/export/gltf_exporter.py`.
- Fastest confirmation: export with Unity vs Unreal preset and diff files; geometry values remain unchanged.

5. VOX export ignores scale preset (UI shows setting without effect)
- Symptoms: status includes scale, but VOX payload is unaffected.
- Suspected root cause: VOX exporter has no scale parameter and always writes raw grid-local coordinates.
- Exact files: `src/app/ui/main_window.py`, `src/core/export/vox_exporter.py`.
- Fastest confirmation: export VOX with different presets and compare XYZI coordinates.

6. Strict project schema rejects unknown keys
- Symptoms: opening a project with extra metadata fails instead of tolerant load.
- Suspected root cause: `load_project()` hard-fails on any unexpected top-level key.
- Exact files: `src/core/io/project_io.py`.
- Fastest confirmation: add harmless top-level field to saved JSON, reopen, observe failure.

7. Part/group IDs are non-deterministic per process and may collide across sessions in merged scenes
- Symptoms: IDs are counter-based, reset per run, not globally unique.
- Suspected root cause: `_PART_ID_COUNTER`/`_GROUP_ID_COUNTER` global counters.
- Exact files: `src/core/scene.py`.
- Fastest confirmation: create projects in separate runs and inspect repeated IDs (`part-1`, `group-1`).

8. OBJ material strategy collapses all faces into one material
- Symptoms: exported MTL has one `voxel_default`; palette/material richness lost.
- Suspected root cause: single-material write path and no face-group material split.
- Exact files: `src/core/export/obj_exporter.py`.
- Fastest confirmation: build multi-color model, inspect OBJ/MTL for multiple `usemtl` entries (none).

9. Duplicate source trees can drift (`src/app` vs `src/voxel_tool`)
- Symptoms: contributors may edit wrong tree and ship stale paths.
- Suspected root cause: historical layout retained without deprecation guardrails.
- Exact files: `src/app/**`, `src/voxel_tool/**`.
- Fastest confirmation: compare files with same conceptual role (e.g., `main.py`, `gl_widget.py`).

10. Crash recovery cadence can miss up to autosave interval of edits
- Symptoms: forced-close may lose recent edits if timer has not fired.
- Suspected root cause: interval-based autosave only; no edit-triggered debounce save.
- Exact files: `src/app/ui/main_window.py`, `src/core/io/recovery_io.py`.
- Fastest confirmation: make edit and force-close immediately before 60s tick; recovery lacks latest change.

## Top 10 Technical Risks (Ranked) + Mitigation
1. Full 3D targeting consistency remains incomplete for non-brush tools
- Mitigation: complete shared non-brush 3D resolver and pick-mode parity tests (Tasks 02-03).

2. Export-format trust gap (glTF/OBJ parity deficits)
- Mitigation: add goldens + external roundtrip smoke matrix (Blender, Unity, Qubicle).

3. Duplicate source-tree drift risk
- Mitigation: freeze `src/voxel_tool` as legacy, add CI check/lint guard, and plan removal task.

4. Strict schema parser blocks forward compatibility
- Mitigation: tolerate unknown fields with warnings and preserve pass-through metadata.

5. Counter-based IDs reduce interoperability robustness
- Mitigation: migrate to UUID-based part/group IDs with loader compatibility fallback.

6. Incremental meshing v1 complexity could hide subtle geometry defects
- Mitigation: increase equivalence tests on random edit sequences and force periodic full-rebuild checks.

7. Command-stack transaction handling can regress under nested/aborted interactions
- Mitigation: add nested transaction guard tests and UI-level cancellation tests.

8. Performance baseline thresholds are permissive (20x)
- Mitigation: tighten thresholds progressively and add scene-size tiers.

9. Autosave snapshot lifecycle may not cover all failure modes
- Mitigation: add debounce-on-edit saves and recovery version stamping.

10. Packaging confidence remains environment-biased
- Mitigation: run checklist on clean Windows VM + second physical machine before stable promotion.
