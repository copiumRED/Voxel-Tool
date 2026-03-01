# QUBICLE_GAP_ANALYSIS

Date: 2026-02-28  
Prepared By: Codex  
Scope: Comparative parity analysis between Qubicle baseline workflows and current `main` implementation, aligned to `Doc/PROJECT_SPEC.md`.

## A) Parity Scorecard

| Area | Qubicle Baseline | Our Current State | Gap | Impact (High/Med/Low) | Priority (P0/P1/P2) | Proposed Implementation (1-3 bullets) | Validation (human test) |
|---|---|---|---|---|---|---|---|
| Core tools: paint/erase, line/box/fill, mirror, brush shapes/sizes | Fast paint/erase, line/box/fill, mirror workflows, practical brush sizing presets | Paint/erase + line/box/fill + mirror XYZ + mirror offsets are implemented; continuous brush drag implemented | Missing brush size/shape variants and preview parity for non-brush tools | High | P0 | - Add brush size radius (1/2/3) and shape mode (cube/sphere). - Add live operation ghost for line/box/fill before commit. - Add single-key cycle for brush size. | Paint with each brush mode; verify previews and one-step undo per operation remain correct. |
| Picking: voxel/face picking in full 3D (not just plane), hover preview, selection modes | Confident 3D face targeting with clear hover and selection affordances | 3D picking is in place with brush hover preview and plane fallback | Non-brush hover ghosting, face-normal hinting, and explicit pick mode controls are missing | High | P0 | - Extend hover system to line/box/fill anchor and target previews. - Add face normal indicator and target-cell marker. - Add explicit pick mode toggle (surface/plane lock). | Draw line/box/fill on dense geometry and empty scene; verify predictable target and visible preview before click release. |
| Parts workflow: multi-part management, transform, visibility/lock, duplicate/delete, grouping | Robust object manager with part transforms, grouping, and hierarchy controls | Multi-part add/rename/select/duplicate/delete/visibility/lock exist | Missing per-part transform editing and grouping/reorder workflows | High | P0 | - Add inspector controls for part position/rotation/scale/pivot. - Add part reorder in list with stable save/load order. - Add group container model (v1: name + children + visible/locked). | Create 5+ parts, transform/reorder/group them, save/open, verify state is preserved and editable. |
| Palette: palette editing, import/export, per-voxel color workflow | Direct palette edit tools with import/export and rapid color switching | Palette preset save/load exists; active color handling is stable | Missing add/remove/edit/swap color slots and external palette import formats | Med | P1 | - Add palette cell edit (RGB/A), add/remove, and swap positions. - Add quick numeric hotkeys for first 10 colors. - Add import/export for common palette formats (JSON + GPL v1). | Edit palette entries, repaint voxels, save/load preset and reopen project to verify color continuity. |
| Viewport UX: ortho views, view presets, snapping, grid controls | Fast viewport switching with ortho views, snapping, and grid customization | Orbit/zoom/pan and frame/reset are implemented; mirror guides visible | Missing ortho view presets, camera snapping, and user-facing grid controls | High | P0 | - Add top/front/left/right/back/bottom view actions and shortcuts. - Add camera snap increments and voxel-aligned orbit/pan snap option. - Add grid size/visibility controls in View menu. | Switch across all view presets, toggle grid settings, and verify edit operations still land correctly. |
| File formats: VOX import/export parity, Qubicle formats feasibility note, plus OBJ export quality | Mature voxel file interoperability plus reliable mesh export | VOX import/export is implemented (single + multi-model); OBJ/glTF export present | Qubicle native `.qb` not supported; OBJ color/material parity still incomplete | High | P0 | - Keep VOX as first-class interchange path. - Add explicit `.qb` support guardrail and go/no-go trigger. - Improve OBJ writer for material/color strategy and pivot/scale handling. | Import VOX from Qubicle then re-export VOX/OBJ and verify roundtrip geometry/color fidelity. |
| Mesh generation: surface extraction + greedy meshing + normals (+ UVs only if in spec) | Clean low-poly mesh generation suitable for engine import | Surface extraction + greedy meshing implemented; rebuild mesh action exists | Normals verification and UV/vertex-color outputs are incomplete vs spec targets | High | P0 | - Add explicit normal generation and winding validation tests. - Add basic UV projection and vertex-color export path for OBJ/glTF target. - Add mesh QA diagnostics (non-manifold count, degenerate triangles). | Export sample assets and inspect in engine/DCC for normal direction, UV presence, and color correctness. |
| Performance: large scenes, incremental updates, memory | Interactive editing at practical scene scales | Baseline harness exists for brush/fill/solidify timing | Missing runtime large-scene profiling UI and incremental remesh strategy | High | P0 | - Add chunk-level dirty tracking for mesh rebuild scope reduction. - Add live perf counters (frame ms, voxel count, mesh tris). - Add stress presets (64^3, 96^3, 128^3 scenarios) and guardrails. | Run stress scenes and verify interaction remains responsive and rebuild times stay within defined thresholds. |
| UX: hotkeys, tool shortcuts, undo depth, autosave/crash recovery | Dense shortcut coverage, deep undo confidence, basic crash resilience | Core tool/camera shortcuts exist; undo/redo works with transactions | Missing configurable shortcut map, undo depth settings, autosave, and crash recovery prompt | High | P0 | - Add preferences panel for shortcuts and undo depth. - Add autosave timer + recovery file on unsafe exit. - Add startup recovery prompt and safe restore path. | Perform edits, force-close app, relaunch, and verify recovery options restore expected state safely. |
| Packaging: clean-machine readiness, installer/portable zip, settings persistence | Reliable distribution for non-dev users | Packaging script and packaged launch smoke validated on current machine | Missing independent clean-machine checklist pass, portable zip flow, and persisted user settings package validation | Med | P1 | - Add portable zip build target and artifact checklist. - Add first-run settings path validation + migration checks. - Add operator clean-machine script checklist with pass/fail rubric. | Install/launch on clean Windows VM, verify first-run settings creation, save/open/export, and relaunch persistence. |

## B) Top 20 Remaining Gaps To Close

1. Brush size and shape variants  
What: Add brush radius and shape modes beyond single-cell brush.  
Why it matters: Major speed multiplier for blockout and detailing.  
Module owner: `app/ui/panels/tools_panel.py`, `app/viewport/gl_widget.py`, `core/commands/demo_commands.py`.  
Success criteria: User can switch radius/shape and paint/erase with accurate preview and one-step undo per stroke.

2. Line/box/fill live previews  
What: Render pre-commit ghost volume/line extents for non-brush tools.  
Why it matters: Prevents misplacement and increases trust in operations.  
Module owner: `app/viewport/gl_widget.py`.  
Success criteria: Before commit, ghost matches final affected cells in at least 10 manual scenarios.

3. Pick mode controls (surface vs plane lock)  
What: Explicit user toggle for pick strategy.  
Why it matters: Removes ambiguity when editing sparse vs dense scenes.  
Module owner: `app/ui/panels/tools_panel.py`, `app/viewport/gl_widget.py`.  
Success criteria: Toggle state is visible and persisted; edits follow selected mode consistently.

4. Part transform editing in inspector  
What: Add per-part transform controls (pos/rot/scale/pivot).  
Why it matters: Required for scene composition parity and export staging.  
Module owner: `app/ui/panels/inspector_panel.py`, `core/part.py`, `core/io/project_io.py`.  
Success criteria: Transform edits reflect in viewport and persist after save/open.

5. Part reorder and stable ordering persistence  
What: Allow moving parts up/down in list and persist order.  
Why it matters: Important for scene organization and export predictability.  
Module owner: `app/ui/panels/inspector_panel.py`, `core/scene.py`, `core/io/project_io.py`.  
Success criteria: Reordered list survives reopen and export order is deterministic.

6. Grouping workflow v1  
What: Add lightweight part groups with group visibility/lock.  
Why it matters: Needed when scenes exceed a few objects.  
Module owner: `core/scene.py`, `app/ui/panels/inspector_panel.py`, `core/io/project_io.py`.  
Success criteria: Create group, add/remove parts, toggle group flags, persist correctly.

7. Palette edit/add/remove/swap  
What: Full palette editing operations in UI.  
Why it matters: Current preset-only flow is too limited for production iteration.  
Module owner: `app/ui/panels/palette_panel.py`, `app/app_context.py`.  
Success criteria: Palette can be edited in-session without crashes; active color remains valid.

8. Palette hotkeys  
What: Direct keyboard selection for common color slots.  
Why it matters: Speeds paint workflow and mirrors industry expectations.  
Module owner: `app/ui/main_window.py`, `app/ui/panels/palette_panel.py`.  
Success criteria: Keys 1-0 switch first 10 colors with clear status update.

9. Ortho views and camera presets  
What: Add top/front/side/bottom/back camera presets.  
Why it matters: Precision edits and familiar modeling UX.  
Module owner: `app/ui/main_window.py`, `app/viewport/gl_widget.py`.  
Success criteria: Preset shortcuts switch viewpoint reliably without breaking controls.

10. Grid and snap controls  
What: Expose grid density/visibility and camera snap options.  
Why it matters: Improves precision and workflow consistency.  
Module owner: `app/ui/main_window.py`, `app/viewport/gl_widget.py`, `app/settings.py`.  
Success criteria: Grid and snap settings are adjustable, persisted, and reflected instantly.

11. VOX import pipeline  
What: Import `.vox` files into project scene and palette.  
Why it matters: Critical interoperability gap with Qubicle/Magica ecosystems.  
Module owner: `core/io`, `core/project.py`, `app/ui/main_window.py`.  
Success criteria: Imported VOX appears correctly with expected palette mapping and no crash.

12. Qubicle `.qb` feasibility and decision note  
What: Document technical feasibility, risks, and go/no-go for `.qb` support.  
Why it matters: Prevents accidental scope drift and clarifies roadmap priority.  
Module owner: `Doc/` analysis + architecture ownership.  
Success criteria: Written decision memo with risk/effort estimate accepted by operator.

13. OBJ export color/material quality pass  
What: Improve OBJ + MTL output to preserve color intent reliably.  
Why it matters: Export trust is a core user value.  
Module owner: `core/export/obj_exporter.py`.  
Success criteria: OBJ imports in DCC/engine with expected color/material mapping.

14. Mesh normals/UV correctness pass  
What: Add normals QA and basic UV assignment output path per spec scope.  
Why it matters: Prevents shading and texturing defects downstream.  
Module owner: `core/meshing/*`, `core/export/*`.  
Success criteria: Reference assets pass manual normals/UV inspection in external viewer.

15. Incremental solidify/mesh rebuild  
What: Rebuild only changed regions instead of full-mesh every time.  
Why it matters: Keeps large-scene editing responsive.  
Module owner: `core/meshing/solidify.py`, edit command paths.  
Success criteria: Rebuild timing drops materially on localized edits (measured baseline delta).

16. Runtime perf diagnostics panel  
What: Show frame time, voxel count, tris, and rebuild time in UI.  
Why it matters: Enables measurable optimization and user confidence.  
Module owner: `app/ui/panels/stats_panel.py`, `app/viewport/gl_widget.py`.  
Success criteria: Metrics update live and remain stable under edit operations.

17. Shortcut map completeness + discoverability  
What: Expand to part/workflow shortcuts and show editable mapping.  
Why it matters: Keyboard-heavy users need efficient, discoverable controls.  
Module owner: `app/ui/main_window.py`, settings layer.  
Success criteria: Core workflows are executable without menu navigation.

18. Undo depth and history reliability controls  
What: Add configurable undo cap and history diagnostics.  
Why it matters: Large scenes can exceed memory or lose expected history depth.  
Module owner: `core/commands/command_stack.py`, settings integration.  
Success criteria: Undo cap respected and visible; no corrupted history under stress tests.

19. Autosave + crash recovery  
What: Add timed autosave and startup restore after abnormal exit.  
Why it matters: Protects user work and reduces catastrophic loss risk.  
Module owner: `app/ui/main_window.py`, `core/io/project_io.py`, settings.  
Success criteria: Recovery prompt appears after forced close; restore works on first attempt.

20. Packaging parity (portable + clean-machine proof)  
What: Complete clean-machine validation and portable artifact checklist.  
Why it matters: Day-to-day adoption depends on predictable installation and launch.  
Module owner: `tools/`, `Doc/PACKAGING_CHECKLIST.md`, operator QA process.  
Success criteria: Clean-machine checklist passes with no manual fixes outside documented steps.

## Qubicle `.qb` Feasibility Decision (Task 13)

- Decision: **Defer `.qb` import/export implementation in current phase (NO-GO for this workday)**.
- Current recommended interchange path: `.vox` for voxel data and `OBJ/glTF` for mesh export.
- Rationale:
  - `.qb` support requires format-specific parsing/encoding with limited test fixtures in-repo.
  - Reverse-engineering or loosely verified community specs adds interoperability regression risk.
  - VOX path is already validated with Qubicle import and now supports multi-model mapping.
- Go criteria (flip to GO in future sprint):
  - At least 10 representative `.qb` fixtures (including multi-part/color edge cases) are collected.
  - Roundtrip acceptance matrix is defined (Qubicle -> Tool -> Qubicle and Tool -> Qubicle -> Tool).
  - Explicit compatibility scope is agreed (supported `.qb` variants, limits, unsupported chunks).
- Guardrail:
  - Do not begin `.qb` parser implementation until the above criteria are met and approved by operator.

## C) Differentiators (How We Beat Qubicle)

- One-click `Solidify/Rebuild Mesh` with optional greedy path and integrated stats feedback.
- Built-in analysis panel with scene/object metrics and unit-aware bounds for budget-driven iteration.
- Mirror offsets per axis, not just on-origin symmetry, for faster asymmetrical production workflows.
- Transaction-grouped undo for drag operations, reducing noisy history and improving edit confidence.
- Integrated export options surface (OBJ/glTF/VOX) with session persistence, reducing repetitive setup.
- Explicit viewport diagnostics at startup with fallback messaging to reduce GPU setup ambiguity.
- Safer fill workflow with bounded-region guardrails to avoid lockups on accidental huge fills.
- In-app quick-help and first-use guidance to reduce onboarding friction for non-technical users.
- Packaging pipeline plus operator checklist oriented for Windows standalone delivery from the same repo.
- Architecture runway for voxel-first authoring plus mesh-enhancement layer as a future upgrade path.
