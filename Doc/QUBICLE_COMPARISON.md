# QUBICLE_COMPARISON

Date: 2026-03-01
Scope: parity planning for next day-cycle. Baseline reference is Qubicle full production workflow.

## Parity Table

| Category | Qubicle baseline | Our current state | Gap | Priority |
|---|---|---|---|---|
| Core brush editing | Fast paint/erase with predictable targeting and mirror | Strong brush pipeline with pick modes, mirror, drag, preview | Needs tighter precision overlays and industry-standard nav ergonomics | P0 |
| Line/box/fill tools | High-confidence shape placement in 3D workflows | Implemented with previews and pick/plane support | Needs advanced selection/stamp workflows and stronger UX cues | P1 |
| Picking and hover | Reliable 3D picking with clear visual feedback | Surface and plane-lock behaviors are implemented | Needs richer face-normal/axis hints and hover affordance polish | P1 |
| Multi-part workflow | Mature part management and production-friendly organization | Parts/groups/visibility/lock/reorder implemented | Needs outliner search/filter and bulk workflows | P1 |
| Palette workflow | Rapid color iteration with robust preset organization | Palette editing, slot lock, GPL/JSON import-export are present | Missing metadata browser, tags/folders, and faster preset navigation | P1 |
| Viewport navigation | Familiar DCC-like controls and precision framing | Orbit/pan/zoom + ortho + presets exist | No MMB-orbit profile or Blender-style navigation preset | P0 |
| Orthographic precision | Strong ortho edit workflows and precision views | Ortho projection and presets exist | No quad-view and limited precision HUD cues | P1 |
| VOX interoperability | Mature import/export with broad chunk support | VOX import/export works; unsupported chunks reported | Transform/hierarchy reconstruction still limited | P1 |
| Qubicle format interoperability | Native workflow compatibility | No `.qb` import/export path | Major compatibility gap | P0 |
| OBJ export quality | Stable DCC-friendly OBJ + material behavior | Greedy/UV/material/color policies implemented | Needs stricter external DCC validation presets | P1 |
| glTF export quality | Engine-ready attributes/materials | glTF has geometry + normals + scale | Missing UV/color/material completeness | P0 |
| Solidify quality | Reliable watertight mesh generation | Surface + greedy + incremental rebuild fallback implemented | Needs QA diagnostics and advanced controls | P1 |
| Performance scaling | Practical handling of larger scenes | Baseline perf tests and runtime metrics exist | Needs tighter CI budgets and large-scene stress framework | P1 |
| Packaging/deployment | Production-ready installer workflows | PyInstaller and portable zip checklist are available | Installer pipeline and clean-machine matrix not complete | P1 |
| Mesh edit layer (beyond Qubicle baseline) | Optional in Qubicle-centric workflows | Not integrated yet in runtime | Required by project spec for "better than Qubicle" objective | P0 |

## Summary
- Current editor is a solid voxel authoring baseline but not yet full Qubicle parity.
- The largest remaining parity blockers are: navigation ergonomics, `.qb` compatibility, glTF completeness, and production packaging confidence.
- The largest "better-than-Qubicle" blocker from project spec is missing mesh-edit mode integration.
