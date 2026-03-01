# QUBICLE_FEATURE_CATALOG

Date: 2026-03-01
Scope: Source-based feature catalogue of Qubicle Voxel Editor base + publicly listed DLC/modules.
Method: Public product pages/documentation only; no reverse engineering; unknowns are explicitly marked.

## A) Core Application Features (Base Product)

### 1) Editing Modes
- 3D voxel editing workspace.
- 2D slice/canvas workflow (`Slice Mode`) for per-slice editing.
- Fast toggle between normal 3D interaction and 2D slice-focused editing.

### 2) Toolset (Drawing, Selecting, Transforming)
Publicly listed as 21 tool classes and broad action sets.

Drawing/painting categories (publicly documented):
- Pencil, Eraser, Attach, Paint.
- Freehand, Line, Rectangle.
- Paint Bucket, Magic Wand.
- Primitive-oriented build tools: Cube, Sphere, Pyramid, Cone, Cylinder.

Selection/manipulation categories:
- Move tool.
- Rectangular select.
- Box select.
- Paint/freehand selection.
- Resize.
- Extrude.

Transform/action layer (public claims):
- Tool symmetry/mirroring.
- 40+ actions across selected voxels/objects.
- Additional transform operations are documented in menu-driven docs (for example, flip).

### 3) Symmetry/Mirroring
- Tool-level mirror/symmetry behavior is part of baseline claims.
- Intended for production modeling workflows (rapid bilateral edits and mirrored operations).

### 4) Scene/Parts/Object Management
- Component/object-part editing workflow is a headline capability.
- Large scene/object limits are publicly claimed:
  - Up to 16 million objects per scene.
  - Up to 1024x512x1024 voxels per object.
- Object hierarchies are referenced in Utility Module (Compounds).

### 5) Palette/Material/Color Workflow
- Color map and voxel color workflow are core to Qubicle docs.
- Includes painting/recoloring and color-selection tools (Paint Bucket/Magic Wand).
- Texture-linked workflows are present in relevant modules/features (OBJ+MTL in Voxelizer path).

### 6) Navigation & Viewport
- Camera-driven work area with configurable visual overlays/settings.
- Work area display settings include shading/wireframe/grid/bounding boxes/ghosts/lights.
- UI customization and hotkey customization are explicitly advertised.

### 7) Undo/Redo & Workflow UX
- Workflow messaging emphasizes familiar 2D/3D tool behavior and fast onboarding.
- Copy/paste and object/voxel selection workflows are documented.
- Strong emphasis on predictable transform/selection/action pipelines.

### 8) Import/Export Formats (Publicly Listed)
Voxel formats:
- QB, QEF, QBT, QMO, QBCL, VOX, Minecraft Schematic.

Mesh/export claims:
- Base: unoptimized OBJ/FBX/Collada export.
- Export slices as PNG.
- 3D printing and Sketchfab upload are publicly advertised features.

## B) DLC / Modules

### 1) Voxelizer Module
Publicly stated scope:
- Import OBJ meshes and voxelize them.
- OBJ with MTL and texture support is explicitly mentioned.
- Real-time rotate/scale adjustments after mesh import.
- Voxelized results can be converted to editable matrices.

Unknown specifics (requires hands-on verification):
- Exact quality controls for voxelization resolution and sampling method.
- Full behavior on complex/non-manifold meshes.

### 2) Mesh Module
Publicly stated scope:
- Advanced mesh export options for game workflows.
- Mesh optimization claims (up to 90%).
- Color-encoded STL export for multi-color printing.
- Export voxels as individual cubes.
- Extra export controls (for example filename prefix/output-folder style options).

Unknown specifics (requires hands-on verification):
- Exact optimization algorithm and quality controls.
- Per-format differences and limits across OBJ/FBX/Collada/STL pipelines.

### 3) Utility Module
Publicly stated scope:
- Landscape/terrain generation.
- Height map import (and matching texture-related workflow mentions).
- Compounds/object hierarchy capabilities.

Unknown specifics (requires hands-on verification):
- Practical hierarchy depth/constraints.
- Terrain generator control granularity and deterministic reproducibility.

## C) Workflow Feel Expectations (Qubicle Baseline)
What makes the baseline feel "production-usable":
- Tool behavior is consistent and predictable between drawing/select/transform paths.
- Selection operations are rich (rect/box/freehand/color-driven) and flow quickly.
- Symmetry and transform actions reduce repetitive edits.
- 3D + 2D slice workflows let artists switch between macro shape and pixel-precise edits.
- Scene/part/component workflows support large asset organization.
- High iteration speed via shortcuts/customization and low-friction repetitive actions.

## Sources
- Qubicle base store page (features, formats, editions): https://store.steampowered.com/app/454550/
- Qubicle DLC listing page: https://store.steampowered.com/dlc/454550/Qubicle_Voxel_Editor/
- Voxelizer DLC page: https://store.steampowered.com/app/456110/Qubicle_Voxelizer_Module/
- Mesh DLC page: https://store.steampowered.com/app/456230/Qubicle_Mesh_Module/
- Utility DLC page: https://store.steampowered.com/app/456231/Qubicle_Utility_Module/
- Qubicle docs - Tools overview: https://getqubicle.com/qubicle/documentation/docs/tools.html
- Qubicle docs - Slice Mode: https://getqubicle.com/qubicle/documentation/docs/tools/slice_mode/
- Qubicle docs - Work Area settings: https://getqubicle.com/qubicle/documentation/docs/view/work_area/
- Qubicle docs - Voxelize: https://getqubicle.com/qubicle/documentation/docs/voxelize/
- Qubicle docs - Auxiliary tools: https://getqubicle.com/qubicle/documentation/docs/tools/auxiliary/
- Qubicle docs - Flip transform example: https://getqubicle.com/qubicle/documentation/docs/transform/flip/
