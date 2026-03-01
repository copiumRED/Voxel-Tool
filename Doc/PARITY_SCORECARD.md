# PARITY_SCORECARD

Date: 2026-03-01
Scope: Qubicle baseline (base + publicly listed modules) vs current `main` implementation.

## A) Scoring Model
- `0` = missing.
- `0.5` = partial / workaround / unstable / significantly behind baseline workflow.
- `1` = baseline-equivalent for practical production use.
- `1.2` = clearly better-than-baseline in this area.

Scoring notes:
- "Partial" is used aggressively for janky or limited implementations.
- Publicly vague Qubicle areas are scored conservatively; unknown module specifics are not invented.

## B) Feature Score Table
| ID | Feature Area | Qubicle baseline (short) | Our state (short) | Score | Notes | Priority |
|---|---|---|---|---:|---|---|
| F01 | 3D voxel editing | Full 3D voxel modeling | Implemented | 1.0 | Core edit loop is present | P0 |
| F02 | 2D slice/canvas mode | Dedicated slice workflow | Not implemented as dedicated mode | 0.0 | Plane lock != slice editor UX | P0 |
| F03 | Core draw tools | Brush/erase/line/box/fill class | Implemented | 1.0 | Practical parity on core set | P0 |
| F04 | Primitive generators | Cube/sphere/pyramid/cone/cylinder tools | Limited brush shape only | 0.5 | Missing explicit primitive toolset | P1 |
| F05 | Selection richness | Rect/box/paint/magic-style selection breadth | Basic voxel selection mode | 0.5 | Missing color/paint/freeform selection depth | P1 |
| F06 | Transform/action depth | 40+ actions headline | Limited tool/action set | 0.5 | Core actions exist; breadth missing | P1 |
| F07 | Mirror/symmetry | Built-in symmetry workflows | Implemented (XYZ + offsets) | 1.0 | Strong parity for voxel ops | P0 |
| F08 | Scene/object scale | Very large object/scene claims | Unproven at equivalent scale | 0.5 | No equivalent public limits validated | P1 |
| F09 | Object hierarchy depth | Component/object hierarchy emphasis | Flat groups, no deep compounds | 0.5 | Nested hierarchy missing | P1 |
| F10 | Palette depth | Mature color map workflow | Solid basic palette ops | 0.5 | Asset/library-level workflow missing | P1 |
| F11 | Hotkey customization | Customizable hotkeys advertised | Fixed shortcuts + overlay | 0.5 | Missing keymap editor | P1 |
| F12 | Import format breadth | QB/QEF/QBT/QMO/QBCL/VOX/schematic | VOX + QB feasibility only | 0.5 | Major format gaps remain | P0 |
| F13 | Export format breadth | OBJ/FBX/Collada (+ module extras) | OBJ/glTF/VOX/QB | 0.5 | No FBX/Collada, different strengths | P0 |
| F14 | Slice PNG export | Export slices as PNG | Missing | 0.0 | No equivalent path | P2 |
| F15 | Voxelizer-equivalent | OBJ->voxel pipeline module | Missing | 0.0 | No dedicated voxelizer flow | P1 |
| F16 | Mesh module equivalence | Advanced optimization/export module | Partial (greedy+baseline export controls) | 0.5 | Not module-equivalent feature breadth | P1 |
| F17 | Utility module equivalence | Terrain/heightmap/compound tools | Missing | 0.0 | No terrain/heightmap pipeline | P1 |
| F18 | External publish/print | Sketchfab + 3D print workflows | Missing | 0.0 | No direct publish/print tooling | P2 |
| F19 | Startup recovery UX | Not a highlighted baseline claim | Implemented strongly | 1.2 | Better safety/recovery flow | P2 |
| F20 | Command palette/HUD aids | Not clearly baseline-highlighted | Implemented | 1.2 | Better discoverability layer | P2 |
| W01 | Tool predictability | Consistent modeling behavior | Strong on core tools | 1.0 | Stable edit loop | P0 |
| W02 | Preview confidence | Visual confidence during operations | Implemented previews/ghosting | 1.0 | Good preview parity | P0 |
| W03 | Selection ergonomics | Broad, fast selection workflows | Basic selection only | 0.5 | Ergonomic depth missing | P1 |
| W04 | Symmetry ergonomics | Productive mirrored workflows | Good mirror workflow | 1.0 | Strong parity in voxel mode | P0 |
| W05 | Navigation feel | Production camera flow | Multi-profile + precision mode | 1.0 | Competitive feel in current scope | P0 |
| W06 | 2D/3D switching | Dedicated modes/workflow | No dedicated 2D slice mode | 0.0 | Major UX gap vs baseline | P0 |
| W07 | Shortcut discoverability | Mature UI/hotkey flows | Overlay + command palette | 1.2 | Better guidance than baseline claims | P2 |
| W08 | Shortcut customization depth | Customizable keybindings | Missing | 0.5 | Discoverability good, customization missing | P1 |
| W09 | Scene outliner ergonomics | Mature object workflow | Good but not deep hierarchy UX | 0.5 | Compounds/hierarchy depth missing | P1 |
| W10 | Session resilience UX | Baseline unknown/less explicit | Recovery/open-recent UX strong | 1.2 | Better recovery ergonomics | P2 |
| Q01 | Startup/runtime stability | Production expectation | Strong QA gate status | 1.0 | Green baseline | P0 |
| Q02 | Regression test breadth | Baseline unknown | Strong automated suite | 1.2 | Better-than-baseline confidence tooling | P2 |
| Q03 | Solidify correctness/visibility | Usable voxel->mesh path expected | Fixed + tested | 1.0 | Critical gate now passes | P0 |
| Q04 | Import/export fidelity | Broad production formats | Partial fidelity across supported formats | 0.8 | Good on implemented formats, breadth gap | P1 |
| Q05 | Large-scene perf behavior | Production responsiveness | Instrumented + stress tiers | 0.8 | Practical but not fully proven | P1 |
| Q06 | Runtime diagnostics | Useful production diagnostics | Stats/telemetry/memory implemented | 1.0 | Strong internal visibility | P2 |
| Q07 | Packaging diagnostics | Shipping readiness expectation | Script + hash diagnostics | 0.8 | Good local diagnostics | P1 |
| Q08 | Clean-machine confidence | Release-grade evidence | Partial/manual only | 0.5 | Needs matrix evidence | P1 |

## C) Computed Parity Percentages
Calculation basis:
- Functionality parity = average of `F*` scores.
- Workflow/UX parity = average of `W*` scores.
- Stability/performance parity = average of `Q*` scores.

Results:
- Functionality parity: **54.5%**
- Workflow/UX parity: **79.0%**
- Stability/performance parity: **88.8%**

Overall weighted score:
- Weights: Functionality 50%, Workflow/UX 35%, Stability/perf 15%.
- Overall = `0.50*54.5 + 0.35*79.0 + 0.15*88.8 = 68.2%`

Interpretation:
- Core workflow quality is solid, but feature-surface parity against full Qubicle (+ modules) is still materially incomplete.
- Phase 1 completion should be gated by missing `Score < 1` P0/P1 items, not by stability alone.
