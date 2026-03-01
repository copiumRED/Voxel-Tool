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
