# CURRENT_STATE

Date: 2026-03-01
Branch baseline: `main`

## Phase Completion
- Phase 0 (Core Editor Foundations): 100%
- Phase 1 (Qubicle-competitive voxel workflow): 92%
- Phase 2 (Mesh Edit MVP): 10%

## Implemented (Current Build)
- UI: tools/inspector/palette/stats panels, command palette, hotkey overlay, top toolbar, dock presets, theme pass.
- Viewport: perspective + orthographic, classic/MMB/blender-mix navigation, precision modifier, mirror overlays, HUD badges.
- Tools: brush/box/line/fill, paint/erase, selection mode, selected voxel move/duplicate, mirror offsets.
- Scene: multi-part workflow, grouping, multi-select part actions, transform controls.
- IO: project save/load, autosave/recovery with diagnostics, startup recovery/open-recent UX.
- Export/Import: OBJ/glTF/VOX export, VOX import transform mapping v1, QB feasibility import/export.
- Perf/diagnostics: incremental rebuild telemetry, dense stress tiers, memory instrumentation, correctness/perf regression tests.
- Packaging: windows packaging checklist + portable zip workflow documented.

## Not Implemented (Major)
- Mesh edit mode (vertex/edge/face edit workflows).
- FBX export path.
- Full VOX scene hierarchy reconstruction (beyond transform mapping v1).
- Clean-machine packaging matrix evidence automation.

## Top Risks + Fast Confirmation
1. Mesh edit mode gap.
- Confirm: check runtime/UI for vertex/edge/face tools; none available.
2. FBX gap.
- Confirm: no FBX action in export menu and no wired exporter.
3. VOX hierarchy gap.
- Confirm: import complex VOX scene graph and validate flattening/partial mapping.
4. QB support depth is feasibility-level.
- Confirm: test compressed/complex QB files and log unsupported cases.
5. Packaging confidence is machine-biased.
- Confirm: run package + smoke in clean VM and secondary machine.

## Corrections Applied
- Removed stale statements that MMB/blender navigation, QB IO, glTF UV/COLOR/material, and memory instrumentation were missing.

## QA STATUS (Pre-Stable Gate: 2026-03-01)
Checklist results:
- 1) Viewport visibility modes: PASS
- 2) Camera controls + precision + reset/frame: PASS
- 3) Brush paint/erase across XY/YZ/XZ: PASS
- 4) Line/box/fill correctness + previews: PASS
- 5) Mirror/symmetry behavior: PASS
- 6) Parts workflow: PASS
- 7) Palette editing + hotkeys + persistence: PASS
- 8) Project save/open compatibility sanity: PASS
- 9) VOX import + palette fidelity: PASS
- 10) Solidify visibility/exportability: PASS (fixed in this QA branch)
- 11) OBJ + glTF export sanity: PASS
- 12) Undo/redo depth + hotkey overlay: PASS
- 13) Startup recovery UX: PASS
- 14) Packaging diagnostics: PASS

Known blockers (ranked):
1. None at P0/P1 for pre-stable core workflow.
2. P2 backlog remains: mesh edit mode, FBX export, deeper VOX scene hierarchy mapping.

Required BEFORE stable promotion:
1. Keep `main` green (`python src/app/main.py` + `pytest -q`).
2. Operator completes full manual UI pass from `Doc/OPERATIONS.md` checklist.
3. Operator confirms packaged artifact launch/smoke on target machine profile.

## Qubicle Parity Snapshot (Assessment 2026-03-01)
- Functionality parity: **54.5%**
- Workflow/UX parity: **79.0%**
- Stability/performance parity: **88.8%**
- Overall weighted parity (50/35/15): **68.2%**

Scoring source:
- `Doc/PARITY_SCORECARD.md`

Top 15 missing items (Scorecard IDs):
1. `F02` Dedicated 2D slice/canvas mode.
2. `F12` Import format breadth parity (QEF/QBT/QMO/QBCL/schematic class gaps).
3. `F13` Export breadth parity (FBX/Collada-class parity gaps).
4. `F15` Voxelizer-equivalent OBJ->voxel pipeline.
5. `F17` Utility-module-equivalent terrain/heightmap workflows.
6. `F05` Selection mode depth (freehand/color/contiguous workflows).
7. `F09` Hierarchy/compound depth beyond flat grouping.
8. `F11` Hotkey customization UI (user keymap editing).
9. `W06` 2D/3D mode-switch workflow ergonomics.
10. `F16` Mesh-module-equivalent advanced optimization/export controls.
11. `Q05` Production-scale performance proof on large datasets.
12. `Q08` Clean-machine validation matrix evidence.
13. `F10` Advanced palette library workflows.
14. `W09` Scene/outliner ergonomics depth.
15. `Q04` Import/export fidelity confidence across edge-case assets.

## Parity Closure Plan v1

Top 10 board tasks (by impact order):
1. `Task 01 - Slice Mode Core State + Data Contract`
- Why: unlocks dedicated 2D workflow foundation (`F02`, `W06`), currently a P0 gap.
2. `Task 02 - Slice Mode Viewport Rendering + Clip Plane UX`
- Why: makes slice mode usable in practice, not just stateful toggle (`F02`, `W06`).
3. `Task 03 - Slice Paint/Erase Tooling`
- Why: closes essential edit-loop parity for 2D mode (`F02`).
4. `Task 09 - Contiguous/Magic Selection Mode`
- Why: major selection ergonomics gap (`F05`, `W03`).
5. `Task 13 - Hierarchy Model v1 (Nested Groups/Compounds)`
- Why: closes deep scene-organization deficit (`F09`, `W09`).
6. `Task 18 - QEF Importer`
- Why: starts high-priority format breadth closure (`F12`).
7. `Task 22 - Minecraft Schematic Importer v1`
- Why: addresses a publicly expected voxel-format pipeline (`F12`).
8. `Task 23 - FBX Exporter Baseline`
- Why: critical export parity blocker for game pipelines (`F13`).
9. `Task 35 - Keymap Editor UI v1`
- Why: resolves shortcut customization gap (`F11`, `W08`).
10. `Task 38 - Packaging Matrix Automation v1`
- Why: raises release confidence beyond single-machine diagnostics (`Q07`, `Q08`).

Expected parity delta after full board completion (estimate):
- Functionality parity: **54.5% -> 83-90%**
- Workflow/UX parity: **79.0% -> 90-95%**
- Stability/performance parity: **88.8% -> 92-96%**
- Overall weighted parity: **68.2% -> 87-92%**

Assumptions for estimate:
- All P0/P1 board tasks land with score >= `1.0` on recheck.
- Module-equivalent tasks (Voxelizer/Utility/Mesh-module) close most `F15/F16/F17` partials.
- Clean-machine packaging matrix and format fidelity harness are fully executed.
