# CURRENT_STATE

Date: 2026-03-01
Branch baseline: `main`

## Phase Completion Estimates
- Phase 0 (Core Editor Foundations): **100%**
- Phase 1 (Qubicle-competitive voxel workflow): **92%**
- Phase 2 (Mesh Edit MVP): **10%**

Reasoning:
- Phase 0 is complete for MVP scope: app shell, viewport, parts/palette, undo/redo, save/load, autosave/recovery, meshing, and export pipeline are implemented and passing tests.
- Phase 1 is near complete for current day-cycle: tooling, selection move/duplicate, mirror overlays, hotkeys/command palette/HUD, VOX/QB import-export feasibility, and glTF/OBJ parity slices are integrated.
- Phase 2 remains early: no production mesh-edit mode (vertex/edge/face selection + editing ops) in the current runtime path.
- Correction: previous state understated delivered navigation presets, selection workflows, memory instrumentation, QB IO, and glTF color/material/UV support.

## Implemented vs Not Implemented

### UI
Implemented:
- Main window with menu actions for file/view/voxel/debug flows.
- Tools panel with shape/mode/pick/edit-plane/fill-connectivity and mirror controls.
- Inspector panel for parts/groups management and transforms.
- Palette panel with slot editing, GPL/JSON import-export, slot locking.
- Stats panel with scene and active-part metrics.

Not Implemented:
- Shortcut editor/custom keymap UI.
- Context-sensitive tooltips/onboarding overlays.
- Dedicated precision modeling HUD (axis lock indicators, snap state badges).

### Viewport
Implemented:
- OpenGL viewport with perspective + orthographic projections.
- Orbit/pan/zoom, frame voxels, camera snap options.
- Navigation profiles: `classic`, `mmb_orbit`, and `blender_mix`.
- Precision modifier mode (`Alt`) for reduced camera sensitivity.
- Hover and drag previews for voxel tools.
- Debug test-voxel workflow and grid controls.

Not Implemented:
- Ortho quad-view layout (front/top/side simultaneous).
- High-density scene culling and level-of-detail strategy.

### Tools
Implemented:
- Brush paint/erase with drag stroke + grouped undo.
- Box/line/fill tools with preview and mirror support.
- Pick modes (`surface` vs `plane_lock`) and fill plane/volume connectivity.
- Brush shape/size and cycle hotkey support.
- Voxel selection mode with click/drag-box selection.
- Selected voxel move and duplicate workflows with undo/redo.
- Mirror visual plane overlays and fill confidence preview region.

Not Implemented:
- Lasso/freeform voxel selection mode.
- Tool-level symmetry visualization overlays per axis plane.
- Macro tools (stamp library, noise/falloff brushes).

### Scene
Implemented:
- Multi-part scene with UUID part/group IDs.
- Part reorder/duplicate/delete and visibility/lock.
- Group creation, assignment, lock/visibility propagation.

Not Implemented:
- Nested hierarchy (groups inside groups).
- Scene outliner filtering/search and bulk operations.
- Per-part instancing workflow.

### IO
Implemented:
- Project save/load with editor-state persistence.
- Forward-compatible top-level unknown-key tolerance.
- Recovery snapshots with version marker and compatibility checks.

Not Implemented:
- Full schema migration framework with explicit version transforms.
- Crash report bundle export for failed recovery cases.
- Multi-file project package format (`.vxlproj` container) from spec.

### Export
Implemented:
- OBJ export with greedy/triangulate/pivot/scale/UV/vertex-color options.
- OBJ multi-material by color and explicit vertex-color policy.
- glTF export with scale, normals, UVs, vertex colors, and baseline material payload.
- VOX export and VOX import with transform mapping v1 + warnings for unsupported chunks.
- Qubicle `.qb` import/export feasibility slices.

Not Implemented:
- FBX exporter path.
- Rich VOX transform/hierarchy chunk reconstruction.

### Solidify
Implemented:
- Surface extraction + greedy meshing.
- Incremental rebuild with correctness fallback to full rebuild.
- Mesh cache integration with part dirty-bounds tracking.

Not Implemented:
- Mesh diagnostics panel (non-manifold/degenerate counters).
- Optional AO/smoothing toggles at solidify stage.
- Advanced incremental chunk scheduling for huge scenes.

### Perf
Implemented:
- Runtime frame/rebuild metrics.
- Perf baseline tests with per-metric thresholds.
- Reduced redundant viewport per-frame traversal.
- Dense-scene tier harness (64/96/128) and memory budget instrumentation.

Not Implemented:
- CI-enforced strict perf budgets per scene tier.
- Stress scene replay harness with trend history.

### Packaging
Implemented:
- PyInstaller script/spec and deterministic artifact diagnostics.
- Portable zip workflow checklist and SHA256 recording steps.
- Legacy-tree guardrail test to avoid editing wrong source path.

Not Implemented:
- Installer authoring and unattended install/uninstall tests.
- Signed release pipeline and clean-machine matrix evidence.
- Automatic artifact publishing workflow.

## Top 10 Blockers / Risks + Confirmation Experiments
1. Missing mesh edit mode blocks full spec completion
- Confirmation experiment: search runtime for vertex/edge/face edit command path and run manual UI pass for mesh edit tools.

2. FBX exporter path is still absent
- Confirmation experiment: inspect export menu and code for FBX wiring; verify no enabled export flow exists.

3. VOX hierarchy reconstruction is partial (`nTRN` translation v1 only)
- Confirmation experiment: import VOX scene with layered transforms/groups and verify flattening/warning behavior.

4. QB interoperability is feasibility-level only
- Confirmation experiment: run import/export on varied QB files (compressed, multi-matrix variants) and log unsupported cases.

5. Startup recovery/open-recent paths rely on interactive prompts that need operator validation
- Confirmation experiment: create recovery snapshot + recent-path scenarios and validate all dialog choices manually.

6. High-density render path still depends on cache invalidation correctness
- Confirmation experiment: perform rapid dense-scene edits and verify viewport updates remain correct without stale geometry.

7. Incremental meshing fallback rate may rise on complex edits
- Confirmation experiment: monitor `inc tries/fallbacks` stats during large localized edit sessions.

8. Packaging confidence still machine-dependent
- Confirmation experiment: run packaging and portable smoke on a clean VM and second machine.

9. Duplicate source trees remain a maintenance hazard
- Confirmation experiment: run guardrails and ensure only canonical source paths are edited.

10. Scope risk: "Qubicle + better" still exceeds current phase boundaries without controlled follow-up slicing
- Confirmation experiment: track remaining parity gaps against next-day roadmap and enforce gate criteria per task.
