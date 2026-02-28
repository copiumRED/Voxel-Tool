# CURRENT_STATE

## Phase Completion Estimates
- Phase 0 (foundation shell + basic voxel editing + save/load + basic export): **65%**
- Phase 1 (MVP voxel tools + solidify + scene/object workflows + stronger export + analysis): **15%**
- Phase 2 (mesh edit layer, UV/material pipeline, advanced export/packaging polish): **3%**

Reasoning:
- Strong progress on foundational editor shell, project persistence, undo/redo, sparse voxel model, viewport interaction, and OBJ proof export.
- Most spec-critical systems (Scene/Parts, voxel toolset breadth, solidify/greedy meshing, mesh edit, UV pipeline, full analysis/export options) are not implemented.

## Implemented vs Not Implemented

### 1) App Shell / UI
Implemented:
- PySide6 app entry and main window with dock layout.
- Menus: File/Edit/View/Voxels/Debug.
- Actions for New/Open/Save/Save As/Export OBJ, Undo/Redo, debug overlay toggle, camera reset/frame, test scene generation.
- Layout persistence via QSettings (`main_window/geometry`, `main_window/state`) and reset-layout recovery action.
- Status bar feedback for major actions.

Not implemented:
- Dedicated Scene/Part browser UI.
- Inspector properties for transforms/pivot/visibility/lock/material slots.
- Production UX flow for tool modes and shortcuts (placeholder panels remain).

### 2) Project / IO
Implemented:
- `Project` dataclass with metadata + voxel storage.
- JSON save/load with schema validation and legacy tolerance for missing `voxels` key.
- Project-level open/save integrated into UI.

Not implemented:
- Spec serialization format (`*.vxlproj` zip container with `project.json`, compressed voxel bins, meshedits, textures).
- Multi-part scene serialization.
- Version migration framework beyond minimal key checks.

### 3) Commands / Undo
Implemented:
- Generic command interface + undo/redo stack.
- Commands: rename project, add voxel, remove voxel, clear voxels, create deterministic test voxel cross.
- UI wired undo/redo.

Not implemented:
- Domain command grouping/transactions for complex tool operations.
- History labels, stack limits, command serialization.
- Mesh-edit command pipeline.

### 4) Voxels Core
Implemented:
- Sparse `VoxelGrid` (`dict[(x,y,z)] -> color_index`) with CRUD and list roundtrip conversion.
- Palette defaults (8 colors) and active color selection.
- Plane paint/remove interaction (`z=0`) via viewport click and Shift+click erase.

Not implemented:
- Dense 128^3 (spec target) representation or hybrid chunking.
- Box/line/fill/mirror tools.
- 3D picking against voxel surfaces (current pick is plane-only).

### 5) Viewport / Rendering
Implemented:
- QOpenGLWidget rendering pipeline with shader + VBO for voxel points.
- Orbit, zoom, pan camera controls.
- Frame-to-voxels and reset camera.
- Debug overlay: axes, grid, camera/voxel text.
- OpenGL readiness logging and init-error signal handling.

Not implemented:
- Spec target renderer architecture (ModernGL pipeline, render passes, lighting/material preview).
- Robust render diagnostics tooling (GPU capability matrix, runtime toggles for state debug).
- Picking/gizmos/render passes modules as described in spec folder plan.

### 6) Export
Implemented:
- OBJ export from voxel grid with internal face culling (surface-only quads).
- Empty export path writes valid comment-only OBJ.

Not implemented:
- Mesh-based export path (solidified/editable mesh).
- FBX/GLTF export.
- Export options (scale presets, pivot options, triangulate toggle, textures/MTL/vertex color strategy).

### 7) Testing / Infra
Implemented:
- Pytest setup and passing core tests (command stack, voxel grid roundtrip, project IO, palette defaults, OBJ exporter).
- Temp-dir hardening to avoid repo-local ACL issues.

Not implemented:
- Qt/viewport integration tests.
- End-to-end save/open/edit/export workflow tests.
- Performance/stress tests for voxel operations and rendering.

## Known Issues / Blockers
- **Critical operator-facing blocker:** viewport overlay text/grid may appear, but voxels/points are still reported as not visible to human tester.
- Duplicate code trees exist (`src/app/...` and `src/voxel_tool/...`), increasing confusion risk over active runtime path.
- Current click paint works only on fixed plane `z=0`; this is intentionally limited and can be mistaken for rendering failure if camera/plane alignment is unexpected.

## Viewport Visibility Problem: Top 5 Suspected Root Causes (Ranked)

1. **Point-size path still driver/profile fragile**
- Why likely: current pipeline relies on shader `gl_PointSize` and optional fixed-function `glPointSize`; some drivers/profile combos can still produce very small or effectively invisible points.
- Code pointer: `src/app/viewport/gl_widget.py` -> `initializeGL()` shader source (`gl_PointSize`) and `paintGL()` point-size/state handling.
- Fastest experiment:
  1. Temporarily set `gl_PointSize` in vertex shader to `24.0` and switch voxel draw mode to tiny screen-facing quads (or GL_LINES box edges) for one run.
  2. If visible immediately, point primitive sizing/state is the root issue.

2. **Ray-to-plane paint places voxels outside expected visible area**
- Why likely: operator may click expecting surface paint, but current pick is only `z=0` plane; ray math or camera orientation can place points off-screen or far away.
- Code pointer: `src/app/viewport/gl_widget.py` -> `_handle_left_click()` and `_screen_to_world_ray()`.
- Fastest experiment:
  1. Use `Debug -> Create Test Voxels (Cross)` without mouse painting.
  2. Then `View -> Frame Voxels`.
  3. If points appear, paint ray path is primary issue; if not, render path issue remains.

3. **Depth/state interplay hiding points behind overlay/grid**
- Why likely: point pass depth handling toggles each frame; overlay lines can dominate visually if point colors/size contrast is weak.
- Code pointer: `src/app/viewport/gl_widget.py` -> `paintGL()` and `_draw_debug_overlay()`.
- Fastest experiment:
  1. Temporarily disable grid/axes draw call, keep text only.
  2. If points become visible, overlay geometry/state ordering is masking points.

4. **Persisted layout/state still causing central viewport clipping/occlusion in some sessions**
- Why likely: prior bad geometry/state may persist despite improvements, especially across old settings snapshots.
- Code pointer: `src/app/ui/main_window.py` -> `_restore_layout_settings()` and `_on_reset_layout()`.
- Fastest experiment:
  1. Run `View -> Reset Layout`.
  2. Restart app.
  3. If visibility recovers, stale QSettings layout was root cause.

5. **VBO/shader draw silently failing with no hard error path**
- Why likely: current fallback retries VBO rebuild only when computed draw count is zero; it does not inspect GL errors or shader attribute validity per frame.
- Code pointer: `src/app/viewport/gl_widget.py` -> `_draw_colored_vertices()` and fallback branch in `paintGL()`.
- Fastest experiment:
  1. Add temporary per-frame diagnostics: attribute locations, GL error checks after `glDrawArrays`.
  2. If errors/invalid attributes appear, shader/VBO binding path is root cause.

## Additional Notes
- This audit reflects the current workspace state, including existing uncommitted modifications in:
  - `src/app/ui/main_window.py`
  - `src/app/viewport/gl_widget.py`
  - `src/core/commands/demo_commands.py`
  - `tests/test_command_stack.py`
- No code changes were made for this audit beyond generating documentation files.
