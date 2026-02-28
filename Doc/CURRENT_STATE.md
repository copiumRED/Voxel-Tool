# CURRENT_STATE (Start of New Day Cycle)

Date: 2026-02-28  
Branch baseline: `stable`

## Phase Completion Estimates
- Phase 0 (foundation shell + runnable editor + save/load + basic export): **92%**
- Phase 1 (Voxel MVP + qubicle-like usability + robust export/stats): **71%**
- Phase 2 (Blender-like mesh editing layer): **7%**

Reasoning:
- Phase 0 is mostly complete: app shell, viewport initialization, camera controls, scene/part model, persistence, core tools, and packaging scripts/checklists are in place.
- Phase 1 has substantial progress (brush/box/line/fill, mirrors, 3D picking, solidify naive+greedy, OBJ/glTF/VOX export, stats panel), but still lacks important usability/perf/reliability elements needed for Qubicle-competitive day-to-day production.
- Phase 2 is intentionally early and mostly placeholder territory per spec.

## Corrections vs Yesterday
- Correction 1: Yesterday report showed roadmap 1-15 complete, which is true at a feature milestone level, but usability-critical regressions (viewport render compatibility and empty-scene brush bootstrap) were still discovered and fixed afterward.
- Correction 2: Yesterday checklist cited `36 passed`; current baseline is `38 passed`.
- Correction 3: Runtime entry consistency improved (`run.ps1` now points to `src/app/main.py`), reducing launch-path ambiguity.
- Correction 4: Startup diagnostics now report explicit viewport readiness + shader profile in status bar; pipeline-unavailable state now renders clear in-viewport error text.
- Correction 5: Brush hover target preview now renders in viewport, including empty-scene plane fallback targeting.
- Correction 6: Part duplicate/delete actions are now available in Inspector with active-part-safe behavior and last-part delete guard.
- Correction 7: Part visibility/lock controls are now active and persisted; viewport now renders visible parts only and blocks edits on locked active parts.
- Correction 8: Shortcut map v1 is active for core tool/mode switching and camera frame/reset controls.

## Qubicle Parity Scorecard
| Feature | Qubicle Baseline | Our Current State | Gap | Priority |
|---|---|---|---|---|
| Viewport reliability | Consistent visible voxel render on launch | Mostly fixed, modern shader fallback added | Need wider GPU/manual validation matrix + stronger fallback UX | P0 |
| First-voxel workflow | Immediate paint in empty scene | Plane fallback + brush hover preview implemented | Remaining gap is richer ghosting for box/line/fill tools | P0 |
| Brush/erase usability | Fast, predictable | Implemented | Missing stroke smoothing + advanced brush options | P1 |
| Box/line/fill tools | Core productivity tools | Implemented | Needs better preview/selection affordance and edge-case polish | P1 |
| Mirror editing | Easy symmetry toggles | XYZ implemented (origin reflection) | Missing custom mirror planes and visual mirror gizmos | P1 |
| Scene/part workflow | Practical object management | Add/rename/select/duplicate/delete/visibility/lock implemented | Remaining gap: optional reorder polish | P1 |
| Palette workflow | Fast color iteration | Basic palette + active color implemented | Missing richer palette mgmt (save/load/swap/hotkeys) | P1 |
| Picking behavior | Intuitive paint/erase targeting | 3D surface pick added | Needs accuracy tuning and fallback hints | P0 |
| Import/export breadth | Robust interop | OBJ + glTF + VOX export implemented | Missing VOX import and stronger export option set | P0 |
| Keyboard shortcuts | Tooling speed via hotkeys | Core tool + camera shortcut map implemented | Remaining gap: part/workflow shortcuts and discoverability polish | P1 |
| Undo/redo confidence | Stable and predictable | Command stack present | Need grouped transactions and stress tests | P1 |
| Performance at scale | Handles practical production scenes | Unknown at larger voxel counts | Need perf benchmarks and optimization passes | P0 |
| Crash resilience | Stable session behavior | Better logs + error signaling | Need broader exception surfacing and recovery paths | P0 |
| Packaging/run consistency | “Works out of box” | Packaging scripts/spec present | Needs clean-machine validation and installer docs | P0 |
| UX discoverability | Low friction UI | Functional but utilitarian | Missing onboarding hints/tooltips/status guidance polish | P1 |

## Top 10 Risks / Blockers (Ranked) + Mitigations
1. Runtime viewport regressions on specific GPU/driver profiles
- Mitigation: startup diagnostics and in-viewport error surfacing are implemented; next is fallback mode toggle + GPU matrix QA checklist.

2. Tool confidence gap (user cannot tell where edits will land)
- Mitigation: brush hover preview is in place; next is operation ghosting parity for box/line/fill.

3. Part workflow incompleteness (missing delete/duplicate/visibility/lock)
- Mitigation: duplicate/delete/visibility/lock shipped with tests; optional reorder remains non-blocking.

4. Sparse data model may degrade at larger scenes
- Mitigation: add perf tests; profile hot paths; consider chunked/hybrid representation if thresholds fail.

5. Export interoperability expectations not fully met
- Mitigation: validate OBJ/glTF/VOX in target tools; add import smoke tests and option parity tasks.

6. Undo/redo edge-case breakage in compound/mirrored operations
- Mitigation: add transaction grouping and targeted regression tests for multi-cell mirrored commands.

7. Duplicate code tree (`src/app` vs `src/voxel_tool`) remains a confusion hazard
- Mitigation: document canonical runtime path and plan deprecation/removal of placeholder tree.

8. Packaging confidence not proven on clean machine
- Mitigation: execute packaging checklist on fresh environment and track failures as blockers.

9. Documentation drift vs implementation velocity
- Mitigation: daily doc checkpoint policy (CURRENT_STATE + DAILY_REPORT + NEXT_WORKDAY updates each cycle).

10. Phase boundary creep (mesh-edit ambitions entering Phase 1 prematurely)
- Mitigation: enforce Phase 1 roadmap guardrails; defer Blender-like editing tasks to Phase 2 backlog.
