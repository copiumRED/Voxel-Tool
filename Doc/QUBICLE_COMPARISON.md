# QUBICLE_COMPARISON

Date: 2026-03-01
Scope: Practical parity comparison against Qubicle baseline workflows, focused on Phase 1 targets.

## Parity Scorecard

| Category | Qubicle baseline | Our current | Gap | Priority | Notes |
|---|---|---|---|---|---|
| Core paint/erase workflow | Fast, predictable 3D voxel placement with low ambiguity | Brush workflow is strong (surface pick + plane lock + drag + preview) | Non-brush tools still plane-bound and less predictable | P0 | Biggest day-to-day usability blocker |
| Line/Box/Fill productivity | Confident shape operations on intended surfaces | Tools exist with preview and undo | Targeting still tied to fixed plane | P0 | Must unify targeting model across tools |
| Mirror editing | Immediate symmetry toggles with reliable outcomes | XYZ mirror + per-axis offsets implemented | Needs stronger UX around active mirror plane and edge cases | P1 | Functionally close, UX polish still needed |
| Parts management | Strong object workflow for medium scenes | Add/rename/select/duplicate/delete/reorder/visibility/lock/group present | Hierarchy ergonomics and ID robustness need work | P1 | Usable but not yet frictionless |
| Palette workflow | High-speed color iteration, palette confidence | In-app edit/add/remove/swap + presets + numeric hotkeys | Material/export mapping and palette metadata limited | P1 | Internal editing is good; downstream parity lags |
| Picking behavior | Consistent voxel/face picking across tools | Brush has robust pick modes | Non-brush pick parity missing | P0 | Needs shared pick resolver pipeline |
| Viewport precision UX | Includes orthographic precision workflows | Perspective orbit + view presets + grid/snap | Orthographic mode missing; axis plane semantics inconsistent | P0 | Critical for precision modeling parity |
| VOX interoperability | Mature import/export in voxel ecosystem | VOX export + basic VOX import multi-model path | Incomplete VOX chunk handling (transforms/hierarchy) | P1 | Good baseline, not full interoperability |
| OBJ export quality | Reliable geometry + materials/color intent | OBJ supports greedy, pivot/scale, UV, MTL, vertex-color extension | Material strategy and color semantics still basic | P1 | Needs explicit compatibility modes |
| glTF quality | Modern engine-friendly export with richer attributes | glTF geometry-only baseline | No normals/UV/colors/materials; scale option not applied | P0 | High-value export parity gap |
| Performance at scale | Practical responsiveness for larger scenes | Metrics + perf tests + incremental rebuild v1 | No strict budget gates; repeated per-frame work remains | P1 | Needs optimization + CI guardrails |
| Crash resilience | Safe workflows, minimal loss on failure | Autosave + recovery prompt exists | Timer-only autosave can lose latest edits | P1 | Add edit-triggered debounce snapshot |
| Packaging readiness | Reliable install/use on clean machines | Packaging scripts and local smoke pass | Installer and clean-machine matrix still incomplete | P1 | Required before stable production claim |

## Phase 1 Target Emphasis
- P0 first: targeting correctness, axis consistency, glTF correctness, schema robustness.
- P1 second: material/palette/export polish, VOX chunk parity, performance hardening, packaging confidence.
- Defer to Phase 2: mesh-editing engine parity (vertex/edge/face manipulation stack).

## Summary
- The project is functionally ahead of early MVP and already useful for baseline voxel authoring.
- Exact Qubicle-competitive parity for daily production depends on resolving P0 correctness gaps in targeting and export behavior, then tightening P1 workflow polish and packaging confidence.
