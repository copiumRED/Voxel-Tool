# FEATURE_ANALYSIS

Date: 2026-03-01
Scope: Feature-state inventory from current `main` implementation and Phase 1 parity targets.

## Feature Inventory (Current)

### Core App + UI
- Docked editor layout with viewport, tools, inspector, palette, stats.
- Menu actions for project lifecycle, exports, view controls, solidify, and debug voxel generation.
- Shortcut baseline: tools (`B/X/L/F`), modes (`P/E`), palette (`1..0`), camera/view presets.

### Project + Scene
- Multi-part scene model with active part selection.
- Part operations: add, rename, duplicate, delete, reorder.
- Part flags: visibility and lock.
- Group model: create/delete/assign/unassign + group visibility/lock propagation.
- Per-part transforms: position/rotation/scale.

### Voxel Tools
- Brush paint/erase with continuous drag strokes.
- Brush profile: size 1-3 and cube/sphere shape.
- Box fill/erase, line paint/erase, bounded flood fill.
- Mirror editing on X/Y/Z with configurable mirror-plane offsets.
- Fill safety threshold to avoid large accidental operations.

### Picking + Preview
- Surface ray-based brush target resolution.
- Plane fallback mode for brush (`Plane Lock` vs `Surface`).
- Hover preview for brush footprint.
- Shape previews for box/line drag and fill hover target.

### Meshing + Analysis
- Surface extraction and greedy meshing.
- Solidify/Rebuild action with per-part mesh cache.
- Dirty-bounds incremental rebuild v1.
- Stats panel for scene/object counts, bounds, and runtime metrics.

### IO + Export
- Project save/open with editor-state persistence.
- Autosave snapshot + crash-recovery prompt.
- VOX import (basic multi-model chunks).
- OBJ export with UV output, vertex-color extension, pivot/scale options, optional triangulation and MTL.
- glTF export baseline (positions/indices).
- VOX export baseline.

### Packaging + Tests
- Windows packaging scripts (PyInstaller spec + PowerShell packaging script).
- Test suite coverage for commands, meshing, IO, exporters, raycast, recovery, and performance baselines.

## Feature Gaps to Reach Qubicle-Competitive Phase 1

### Tools + Picking
- Non-brush tools require true 3D targeting and must respect pick mode.
- Edit-plane selection/locking needs explicit UX (not implicit hard-coded plane).
- Advanced brush workflow (quick size cycle, optional falloff presets) remains missing.

### Parts Workflow
- Group UX needs stronger visibility (part membership display and quick group actions).
- Part ID stability should be globally unique for safer cross-project workflows.
- Part transform gizmo-style interaction is absent (numeric-only today).

### Palette + Materials
- Palette import/export formats beyond JSON are missing.
- Palette-to-material mapping for export is underpowered (single-material OBJ path).
- Color workflow lacks palette metadata, locking, and palette-level validation tools.

### Viewport UX
- Orthographic mode is missing.
- Axis/plane conventions are inconsistent between rendering and editing behavior.
- Large-scene rendering lacks culling/LOD strategy.

### Import/Export
- glTF lacks normals/UV/colors/materials parity.
- VOX import lacks hierarchy/transform chunk interpretation.
- FBX is not present.

### Stability + Performance
- Forward-compatible project schema loading is missing.
- Performance limits are measured but not enforced.
- Recovery path is timer-only; very recent edits can be lost.

### Packaging
- No installer output yet.
- No repeatable clean-machine validation matrix archived in docs.

## Must-Have UX Behaviors (Phase 1)
- Every drawing tool (brush/box/line/fill) must show where it will apply before commit.
- User must be able to choose and see active edit targeting mode (surface/plane lock/axis plane).
- Multi-part scenes must be manageable without leaving inspector (filter/select/reorder/group quickly).
- Palette switching and editing must be keyboard-fast and predictable.
- Undo/redo must remain one-step logical per gesture (drag stroke/group operation).
- Export dialogs must only show options that actually affect that target format.
- Save/open/recover must protect work without surprising schema failures.
- View controls must include orthographic precision workflows for blockout tasks.
- Performance feedback must be visible and interpretable while editing.
- First-use flow must remain discoverable from the app itself (not docs only).
