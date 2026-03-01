# CURRENT_STATE

Date: 2026-03-01
Branch baseline: `main`

## Phase Completion Estimates
- Phase 0 (Core Editor Foundations): **98%**
- Phase 1 (Qubicle-competitive voxel workflow): **74%**
- Phase 2 (Mesh Edit MVP): **10%**

Reasoning:
- Phase 0 is mostly complete: app shell, viewport, parts/palette, undo/redo, save/load, autosave/recovery, meshing, and baseline exports are implemented and tested.
- Phase 1 is partially complete: core voxel editing is usable, but full Qubicle parity is still blocked by missing advanced selection workflows, richer viewport controls, and broad import/export compatibility.
- Phase 2 remains early: no production mesh-edit mode (vertex/edge/face selection + editing ops) in the current runtime path.

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
- Hover and drag previews for voxel tools.
- Debug test-voxel workflow and grid controls.

Not Implemented:
- Industry-standard control profile (MMB orbit variant / Blender-like navigation profile).
- Ortho quad-view layout (front/top/side simultaneous).
- High-density scene culling and level-of-detail strategy.

### Tools
Implemented:
- Brush paint/erase with drag stroke + grouped undo.
- Box/line/fill tools with preview and mirror support.
- Pick modes (`surface` vs `plane_lock`) and fill plane/volume connectivity.
- Brush shape/size and cycle hotkey support.

Not Implemented:
- Lasso/rect voxel selection and transform of selected voxel sets.
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
- glTF export with scale and normals.
- VOX export and VOX import warning path for unsupported chunks.

Not Implemented:
- FBX exporter path.
- glTF color/material/UV payload parity.
- Qubicle `.qb` import/export.
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

Not Implemented:
- CI-enforced strict perf budgets per scene tier.
- Memory profile instrumentation for 64^3/96^3/128^3 targets.
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
1. Missing mesh edit mode blocks "full MVP" target from project spec
- Confirmation experiment: search runtime code paths for active vertex/edge/face edit mode and execute manual UI pass; verify no usable mesh-edit toolchain is exposed.

2. No FBX export path despite spec target
- Confirmation experiment: run export menu smoke and code search for FBX exporter integration; verify no functional FBX export action exists.

3. No `.qb` interoperability
- Confirmation experiment: attempt to import/export `.qb` via UI and verify option absence; confirm no parser/writer in `src/core/io`.

4. Navigation controls are not industry-standard yet (no MMB orbit profile)
- Confirmation experiment: perform viewport input test; verify orbit is left-drag (non-brush), pan is right-drag, no MMB orbit mode toggle.

5. glTF parity is partial (normals yes, but no UV/colors/materials)
- Confirmation experiment: export glTF and inspect JSON accessors/primitives for `TEXCOORD_0`, `COLOR_0`, and material references.

6. VOX import does not reconstruct hierarchy/transform semantics
- Confirmation experiment: import VOX containing transform/scene chunks and verify warning + flattened behavior.

7. Duplicate source trees still carry maintenance risk
- Confirmation experiment: modify legacy file under `src/voxel_tool`; verify guard test failure and developer friction for intentional changes.

8. Incremental meshing safety currently relies on fallback checks that may impact large-scene performance
- Confirmation experiment: run repeated localized edits on dense scenes and log rebuild timings with fallback frequency.

9. Packaging confidence is still environment-biased
- Confirmation experiment: run packaging + smoke on clean VM and second machine; compare failures and missing runtime deps.

10. Day-scale delivery risk for "Qubicle + better" scope is high without strict task slicing and acceptance gates
- Confirmation experiment: track completion burn-down at task 10/20/30 checkpoints against pass/fail gates.
