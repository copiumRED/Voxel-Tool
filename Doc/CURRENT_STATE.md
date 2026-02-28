# CURRENT_STATE (Start of New Day Cycle)

Date: 2026-02-28  
Branch baseline: `stable`

## Phase Completion Estimates
- Phase 0 (foundation shell + runnable editor + save/load + basic export): **92%**
- Phase 1 (Voxel MVP + qubicle-like usability + robust export/stats): **95%**
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
- Correction 9: Command stack now supports explicit transaction grouping; drag-tool undo behavior is covered with mirror-enabled regression tests.
- Correction 10: Mirror plane visual guides are now rendered in viewport and mapped clearly to `Mirror X/Y/Z` controls.
- Correction 11: Custom mirror plane offsets are implemented and mirrored edits now honor per-axis configured planes.
- Correction 12: Export options dialog flow is implemented with session-persisted options and OBJ greedy/triangulate controls.
- Correction 13: VOX exporter validation tests were expanded for deterministic palette/chunk behavior.
- Correction 14: External VOX interoperability was confirmed via Qubicle import (operator test).
- Correction 15: Palette preset save/load flow is implemented with active-color validity protection.
- Correction 16: Continuous brush drag painting is implemented with one-step stroke undo transactions.
- Correction 17: Fill safety threshold is implemented with explicit user feedback for blocked oversized fills.
- Correction 18: Explicit solidify/rebuild action now refreshes active-part mesh cache used by stats/export paths.
- Correction 19: Stats panel now shows unit-aware bounds (voxels + meters) for active part analysis.
- Correction 20: Save/Open now persists and restores core editor tool state with explicit invalid-file error messaging.
- Correction 21: Performance baseline harness is now in tests with tracked baseline values and non-blocking regression thresholds.

## Qubicle Parity Scorecard
| Feature | Qubicle Baseline | Our Current State | Gap | Priority |
|---|---|---|---|---|
| Viewport reliability | Consistent visible voxel render on launch | Mostly fixed, modern shader fallback added | Need wider GPU/manual validation matrix + stronger fallback UX | P0 |
| First-voxel workflow | Immediate paint in empty scene | Plane fallback + brush hover preview implemented | Remaining gap is richer ghosting for box/line/fill tools | P0 |
| Brush/erase usability | Fast, predictable | Continuous brush drag paint implemented with one-step undo | Remaining gap: stroke smoothing + advanced brush options | P1 |
| Box/line/fill tools | Core productivity tools | Fill safety threshold + feedback implemented | Remaining gap: preview/selection affordance and threshold tuning UX | P1 |
| Mirror editing | Easy symmetry toggles | XYZ toggles + visual gizmos + per-axis offsets implemented | Remaining gap: mesh-mode symmetry parity (Phase 2 scope) | P1 |
| Scene/part workflow | Practical object management | Add/rename/select/duplicate/delete/visibility/lock implemented | Remaining gap: optional reorder polish | P1 |
| Palette workflow | Fast color iteration | Save/load presets implemented with active color safety | Remaining gap: palette swap/hotkeys/preset metadata polish | P1 |
| Picking behavior | Intuitive paint/erase targeting | 3D surface pick added | Needs accuracy tuning and fallback hints | P0 |
| Import/export breadth | Robust interop | Export paths consume refreshed mesh cache + options panel v1 + VOX Qubicle validation | Remaining gap: deeper format parity + VOX import | P0 |
| Keyboard shortcuts | Tooling speed via hotkeys | Core tool + camera shortcut map implemented | Remaining gap: part/workflow shortcuts and discoverability polish | P1 |
| Undo/redo confidence | Stable and predictable | Grouped transactions + mirror drag undo tests implemented | Remaining gap: high-volume stress/perf-focused undo tests | P1 |
| Performance at scale | Handles practical production scenes | Perf baseline harness implemented for brush/fill/solidify | Remaining gap: broader scale matrix + targeted optimizations | P0 |
| Crash resilience | Stable session behavior | Improved invalid-file error surfacing in Open flow | Need broader exception recovery paths | P0 |
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
- Mitigation: VOX validation now includes Qubicle manual import confirmation; next is broader external tool smoke matrix.

6. Undo/redo edge-case breakage in compound/mirrored operations
- Mitigation: transaction grouping and mirrored drag regression tests are now in place; next is stress/perf-oriented undo torture coverage.

7. Duplicate code tree (`src/app` vs `src/voxel_tool`) remains a confusion hazard
- Mitigation: document canonical runtime path and plan deprecation/removal of placeholder tree.

8. Packaging confidence not proven on clean machine
- Mitigation: execute packaging checklist on fresh environment and track failures as blockers.

9. Documentation drift vs implementation velocity
- Mitigation: daily doc checkpoint policy (CURRENT_STATE + DAILY_REPORT + NEXT_WORKDAY updates each cycle).

10. Phase boundary creep (mesh-edit ambitions entering Phase 1 prematurely)
- Mitigation: enforce Phase 1 roadmap guardrails; defer Blender-like editing tasks to Phase 2 backlog.
