# COMPETITIVE_ANALYSIS

Date: 2026-03-01
Reference Product: Qubicle Voxel Editor baseline workflows.

## Parity Snapshot
| Area | Qubicle Baseline | Current State | Gap | Priority |
|---|---|---|---|---|
| Core voxel tools | paint/erase/line/box/fill + mirror | Implemented | advanced brush macros/falloff missing | P1 |
| Picking + selection | full 3D picking + robust selection flows | Surface/plane lock + selection mode + move/duplicate | lasso/freeform selection missing | P1 |
| Parts workflow | mature multi-part + hierarchy ergonomics | multi-part + grouping + transforms + bulk actions | nested hierarchy/instancing missing | P1 |
| Palette workflow | fast palette operations and iteration | edit/import/export + lock + quick slots | richer palette asset workflows missing | P2 |
| Viewport UX | production-grade controls and presets | classic/MMB/blender-mix + precision + ortho + presets | quad-view and deeper snapping UX missing | P1 |
| File interop | VOX/QB-centric pipelines | OBJ/glTF/VOX + QB feasibility IO | FBX and deeper VOX/QB compatibility gaps | P0 |
| Performance | responsive at practical scene sizes | caching + incremental telemetry + stress tiers | stricter perf budgets + culling strategy needed | P1 |
| Packaging | polished desktop delivery | packaging and portable checklist documented | automated clean-machine confidence pending | P1 |

## Top Remaining Gaps
1. Mesh edit mode (vertex/edge/face edit) not shipped.
2. FBX export not shipped.
3. VOX hierarchy semantics are only partially mapped.
4. QB support is feasibility-level; edge cases remain.
5. Quad-view/advanced viewport ergonomics not shipped.

## Differentiators Already Landed
- Multiple navigation profiles including blender-mix behavior.
- Precision modifier for camera and transform scrub workflows.
- Integrated command palette + hotkey overlay.
- Built-in recovery diagnostics and startup recovery decision flow.
- Strong regression coverage (`183` passing tests) with perf/correctness slices.

## Must-Have Next Focus (if parity push continues)
- Mesh edit MVP vertical slice.
- FBX export slice.
- VOX scene-graph mapping upgrade.
- Clean-machine packaging validation matrix automation.

## Plugins/DLC Roadmap Placeholder
- Phase 1.5 DLC: Voxelizer import assistant (mesh/image-to-voxel helper pipeline).
- Phase 1.5 DLC: Material/Palette pack manager (theme packs + project-scoped libraries).
- Phase 2 DLC: Procedural brush kit (noise/falloff/stamp macro brushes).
- Phase 2 DLC: Advanced scene tools (instancing, nested groups, hierarchy ops).
- Phase 2 DLC: Export bridge pack (FBX-focused interchange and validation presets).
