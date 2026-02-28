# PROJECT_SPEC.md — Voxel-to-LowPoly Desktop Tool (Windows, Python)

## Project Overview
A Windows-only standalone desktop application that lets solo/small-team game developers create voxel models quickly (Magica/Qubicle-style), then “Solidify” them into a clean, watertight low-poly mesh, and perform **Blender-light** mesh edits (vertex/edge/face editing) to add stylized detail—without needing Blender except for advanced workflows.

This is a **voxel-first workflow** with a **mesh enhancement layer**:
- Build volume with voxels fast
- Convert to optimized surface mesh
- Refine as low-poly (subtle additions, silhouette tweaks)
- Export to game pipelines (OBJ + FBX), with support for **vertex colors and textures**

---

## Goals
- **Fast voxel modeling** up to **128³** grids per part (typical), with predictable performance.
- **One-click Solidify**: generate watertight mesh with greedy meshing + correct normals.
- **Blender-light mesh editing**: vertex/edge/face selections; add vertices on edges; split faces; basic extrude/inset; move/scale/rotate.
- **Game-dev oriented**: analysis/stats tools for triangles/faces/edges/verts per object and whole scene; export settings; predictable outputs.
- **Mirror modes** on **X/Y/Z** in voxel tools and (where feasible) mesh edit mode.
- **Windows packaging** as a standalone app built from VS Code + Python.

---

## Non-Goals
- Full Blender replacement (no modifiers stack, sculpting, simulation, node graphs, advanced retopo).
- Rigging/animation, skinning, advanced UV unwrapping/packing (beyond basic projection + simple editing).
- Photoreal rendering or heavy material systems (keep “mini-engine”, not AAA).
- Networked collaboration.

---

## Target Platform
- **Windows 10/11** (x64)
- GPU: any DX11+ capable GPU (OpenGL 3.3+ equivalent via ModernGL); fallback path optional but not required for MVP.

---

## User Personas
1. **Solo Indie Dev (Primary)**
   - Needs rapid asset creation for prototypes/vertical slices
   - Wants clean, low-poly stylized models with minimal tool friction

2. **Small Team Artist/Tech-Artist**
   - Needs repeatable exports (scale, pivot, naming, batching)
   - Wants consistent poly budgets and quick tweaks without Blender round-trips

3. **Game Jam Creator**
   - Wants speed > perfection, fast iteration, quick exports

---

## Core Features (MVP)
### 1) Project + Scene System
- Create/Open/Save project
- Scene contains multiple **Parts/Objects**
- Each Part has:
  - voxel grid (up to 128³ typical, configurable)
  - palette/material references
  - transform (pos/rot/scale)
  - pivot/origin controls
  - visibility/lock

### 2) Voxel Modeling Tools
- Brush paint / erase
- Box fill / box erase
- Line tool (optional if time allows; otherwise future)
- Flood fill within bounds (optional future if time tight)
- **Mirror modes**: X, Y, Z (independent toggles)
- Palette with:
  - colors (RGBA)
  - optional “material slots” (roughness/metalness fields reserved for future)

### 3) Solidify (Voxel → Mesh)
- Surface extraction (remove internal faces)
- **Greedy meshing** to reduce polygon count on axis-aligned surfaces
- Generate mesh with:
  - vertex positions
  - normals
  - UVs (basic projection)
  - vertex colors (from voxel palette)
- “Rebuild Mesh” on demand (non-destructive relative to voxel data)

### 4) Mesh Edit Mode (Blender-light, Game-Oriented)
Selection modes:
- Vertex select
- Edge select
- Face select

Edit operations (MVP scope):
- Transform: move/rotate/scale selection (gizmo)
- Extrude faces
- Inset faces (simple)
- Delete verts/edges/faces (safe cleanup)
- **Add vertex on edge** (edge split)
- **Add edge on face** (face split via two-point cut, constrained)
- Weld/merge by distance (basic cleanup)
- Recalculate normals (per object)

Mirror in mesh edit (MVP pragmatic scope):
- Symmetry editing along X/Y/Z via mirrored transforms + mirrored edits (best-effort)
- Hard requirement: voxel tools mirror must be solid; mesh symmetry can start with X only if engineering risk is high, but target is XYZ.

### 5) UV + Color Support
- Vertex colors always available (fast, no textures needed)
- Texture workflow:
  - Simple atlas baking from palette (configurable resolution, e.g. 256/512/1024)
  - UVs assigned to atlas tiles (grid-based)
- Basic UV transform tools (move/scale/rotate UV island) may be deferred to v1 if needed

### 6) Analysis / Stats Tool (Game-Dev Intent)
- Per-object stats:
  - triangles, faces, edges, vertices
  - bounds size (meters)
  - material slots used
- Whole-scene stats summary
- “Poly budget warnings” (thresholds configurable)

### 7) Export
- Export selected object(s) or full scene
- Formats:
  - **OBJ** (MVP)
  - **FBX** (see Technical Notes: recommended as v1 due to Python ecosystem constraints; include as optional plugin if feasible)
- Export options:
  - apply transforms / keep transforms
  - scale (Unity=1m, Unreal=1cm presets)
  - pivot mode (center/bottom/custom)
  - triangulate (on/off)
  - include vertex colors (OBJ via extension strategy or bake to texture)
  - include textures + MTL for OBJ

---

## Future Features
- LOD generation presets (voxel-level + mesh decimation)
- Per-face smoothing groups / hard edges marking
- Better UV tools (seams, packing)
- GLTF/GLB export (highly recommended)
- Import (OBJ/GLTF) for kitbashing (optional)
- Render preview modes (toon shading, outlines)

---

## UX Flow
### Primary Workflow
1) **New Project**
2) **Create Part**
3) **Voxel Mode**
   - sculpt + paint with mirror toggles
4) **Solidify**
   - generate watertight greedy mesh
5) **Mesh Mode**
   - silhouette tweaks, extrude details, edge/face splits
6) **Analyze**
   - check triangles/verts budget
7) **Export**
   - OBJ (MVP), FBX (v1/optional plugin)

### UI Layout (Mini-Engine Editor)
- Center: 3D viewport (orbit camera, grid, lighting)
- Left dock: tool palette (Voxel / Mesh / Transform / Mirror)
- Right dock: inspector (selected object properties, export, stats)
- Bottom: action log / status / hints (optional)

---

## Technical Stack
### Language / Runtime
- Python 3.11+ (Windows)
- VS Code development workflow

### UI Framework
- **PySide6 (Qt)** for professional docking panels, menus, shortcuts, property inspectors.

### Rendering (Mini-Engine Viewport)
- **ModernGL** embedded into a Qt OpenGL widget
- Simple forward renderer:
  - grid + axis gizmos
  - basic directional light + ambient
  - optional toon ramp (future)

### Math + Data
- numpy for voxel arrays and mesh buffers
- PyGLM (or small math utilities)

### Geometry Core
- Voxel grid represented as dense numpy array for 128³ (fast & simple)
- Mesh represented as:
  - **Half-edge** structure for mesh edit mode
  - Export mesh buffer (indexed triangles) generated from editable mesh

### Serialization
- Project file format: `*.vxlproj` (zip container)
  - `project.json` (metadata, parts, transforms, version)
  - `voxels/<part_id>.bin` (compressed voxel data, e.g., zstd)
  - `meshedits/<part_id>.json` (edit operations or stored mesh deltas)
  - `textures/atlas.png` (optional baked texture)

### Packaging
- **PyInstaller** producing a standalone `.exe`
- Installer (future): Inno Setup

---

## Architecture Overview
### High-Level Components
1. **UI Layer (Qt)**: commands, tool state, panels, menus
2. **Viewport Layer (Renderer)**: camera, draw calls, picking, gizmos
3. **Core Data Model**: Project/Scene/Part/Palette/VoxelGrid
4. **Voxel Ops**: paint/fill/mirror/selection
5. **Meshing Pipeline**: surface extraction + greedy meshing + UV assignment
6. **Mesh Editing Engine**: half-edge mesh, selection sets, edit ops, undo/redo
7. **Exporters**: OBJ/MTL + texture outputs; FBX plugin/v1

### Key Design Principle
- **Voxel data is authoritative** for base shape.
- Mesh edits are an enhancement layer stored as operations (preferred) or snapshot.
- “Rebuild mesh from voxels” does not destroy mesh edits unless explicitly reset.

---

## Folder Structure
```text
voxel_tool/
  README.md
  PROJECT_SPEC.md
  pyproject.toml
  requirements.txt
  assets/
    shaders/
    icons/
    default_palettes/
  src/
    app/
      main.py
      app_context.py
    ui/
      main_window.py
      panels/
        tools_panel.py
        inspector_panel.py
        palette_panel.py
        stats_panel.py
      dialogs/
      shortcuts.py
    viewport/
      gl_widget.py
      camera.py
      gizmos.py
      picking.py
      render_passes.py
    core/
      models.py
      voxel_grid.py
      serialization/
        project_io.py
        versioning.py
        compression.py
    ops_voxel/
      tools.py
      mirror.py
      selection.py
      undo_ops.py
    meshing/
      surface_extract.py
      greedy_mesher.py
      mesh_build.py
      uv_project.py
    mesh_edit/
      halfedge.py
      selection.py
      ops/
        extrude.py
        inset.py
        split_edge.py
        split_face.py
        delete.py
        weld.py
      undo_ops.py
    analysis/
      stats.py
      budgets.py
    export/
      obj_exporter.py
      mtl_writer.py
      texture_bake.py
      fbx_exporter.py
    util/
      log.py
      math3d.py
      profiling.py
  tests/
    test_meshing.py
    test_serialization.py
    test_mesh_edit_ops.py
  tools/
    build_pyinstaller.spec
```

---

## Coding Standards
- Black formatting, Ruff linting, mypy type hints (core + geometry)
- UI must not directly mutate geometry; use command pattern/services
- Prefer deterministic geometry operations; keep ops testable

---

## Naming Conventions
- Classes: `PascalCase`
- Functions/vars/files: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Stable IDs: UUID strings for parts

---

## Data Models
### Project
- `project_id: str`
- `version: str`
- `units: str` (“meters”)
- `palette: Palette`
- `parts: dict[str, Part]`

### Part
- `part_id: str`
- `name: str`
- `voxel_grid_ref: str`
- `transform: Transform`
- `pivot: Pivot`
- `mesh_cache: MeshCache`
- `mesh_edits: MeshEdits`
- `flags: {visible, locked}`

### VoxelGrid
- `dims: (int,int,int)`
- `data: np.ndarray[uint16]` (palette index; 0 = empty)

### EditableMesh (Half-Edge)
- `vertices`, `edges`, `faces`
- `attributes: normals, uvs, colors`
- `selection: {verts, edges, faces}`

### Stats
- `triangles, faces, edges, vertices`
- `bounds, surface_area` (future)
- `materials_used`

---

## State Management
- Tool mode state (Voxel/Mesh/Transform), mirror toggles, active part
- **Command + Undo/Redo**:
  - `execute()` / `undo()`
- Cache invalidation rules:
  - voxel edits invalidate derived mesh
  - mesh edits invalidate export buffers

---

## Error Handling Strategy
- User-facing errors: non-blocking toast + details panel
- Internal exceptions: logged with stack traces
- File IO: validate paths inside project zip (no zip-slip)

---

## Logging Strategy
- Rotating file logs + console logs in dev
- Categories: `ui`, `viewport`, `voxel`, `meshing`, `mesh_edit`, `export`, `io`
- Perf timing logs for meshing/baking/export

---

## Security Considerations
- Local-only app
- Defensive parsing for project zip contents
- No remote plugin execution in MVP

---

## Performance Requirements
- 60 FPS viewport for typical scenes
- Voxel ops must feel instant on 128³
- Solidify target: ~< 2 seconds typical 128³ part (mid-range CPU)
- Mesh edit interactive up to ~100k tris (stretch goal)

---

## Testing Strategy
- Unit tests for:
  - greedy meshing correctness/manifold checks
  - serialization round-trip
  - mesh edit ops (split edge/face, extrude)
- Golden tests: known voxel inputs -> expected mesh stats hashes
- Manual QA: save/load, undo/redo, export import tests (Unity/Unreal)

---

## Build & Run Instructions
### Dev Setup (VS Code)
1. Install Python 3.11+
2. Create venv:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
3. Install deps:
   - `pip install -r requirements.txt`
4. Run:
   - `python src/app/main.py`

### Packaging (Windows)
- `pyinstaller tools/build_pyinstaller.spec`
- Output in `dist/VoxelTool/`

---

## Git Workflow Expectations
- `main` always stable
- `feature/<name>` branches for chunks
- Small commits, clear messages
- Pre-merge checklist: run tests + smoke run

---

## Development Phases
### Phase 0 — Foundations (Week 1)
- Qt shell app + dock layout
- viewport (grid, orbit camera, picking stub)
- project/part models + save/load

### Phase 1 — Voxel MVP (Week 2–3)
- voxel tools + mirror XYZ
- palette system
- undo/redo (voxel)

### Phase 2 — Solidify Pipeline (Week 3–4)
- surface extraction + greedy meshing
- mesh preview
- OBJ export validated in Unity/Unreal

### Phase 3 — Mesh Edit MVP (Week 5–6)
- half-edge mesh
- selection (V/E/F)
- gizmos + transforms
- split edge, split face, extrude/inset
- weld + normals recalc

### Phase 4 — Texture + Analysis (Week 6–7)
- atlas bake + UV assignment
- stats panel + budget warnings

### Phase 5 — FBX Export (Week 7+)
**Risk Note:** FBX export in Python packaging is often fragile.
Plan:
- Ship OBJ as stable baseline.
- Add FBX via:
  1) optional Autodesk FBX SDK integration, or
  2) Assimp if verified stable, or
  3) optional headless Blender conversion bridge (if installed).

---

## First Milestone
**M1: Voxel -> Solidify -> OBJ Export**
- voxel edit with mirror XYZ
- solidify produces watertight greedy mesh
- export OBJ + MTL (+ optional atlas)
- import test in Unity/Unreal: scale/pivot/normals correct

---

## Success Criteria
- Solo dev can create an asset in < 10 minutes:
  voxel blockout -> solidify -> minor mesh edits -> export
- Mesh output is predictable and engine-friendly
- Stats tool reliably reports per-object and scene totals

---

## Handoff Notes
Top risks:
1) Half-edge mesh editing + undo/redo correctness
2) FBX export reliability in a packaged exe
3) Performance for interactive mesh ops in Python

Risk strategy:
- lock M1 (OBJ) first
- keep mesh ops minimal but rock-solid
- treat FBX as plugin/bridge until proven stable
