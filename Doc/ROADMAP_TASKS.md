# ROADMAP_TASKS

Date: 2026-03-01
Branch: `main`
Status: Day-cycle complete (Tasks 01-40 done, merged to `main`).

## Active Board
- Remaining tasks: none.
- Next action: operator validation and bug-fix branches only (`feature/fix-*` -> `main`).

## Completed This Cycle (01-40)
1. 01 - Input State Machine Split (Edit vs Navigate) - `64a6ea4`
2. 02 - MMB Orbit Navigation Profile - `12840b9`
3. 03 - Blender-Mix Navigation Preset - `dbd0bc4`
4. 04 - Navigation Sensitivity Controls - `89843ab`
5. 05 - Drag Transaction Abort Hardening - `381e833`
6. 06 - Recovery Diagnostic Report - `21916d7`
7. 07 - Project Schema Version Handshake - `ffe7c1b`
8. 08 - Save/Open Robustness Sweep - `008bd30`
9. 09 - Scene Outliner Search Filter - `09d34a6`
10. 10 - Multi-select Part Actions - `d5d8b4c`
11. 11 - Voxel Selection Set v1 - `5552389`
12. 12 - Selected Voxel Move Tool - `8df078a`
13. 13 - Selected Voxel Duplicate Tool - `c64a469`
14. 14 - Fill Preview Confidence Layer - `f27010b`
15. 15 - Mirror Visual Plane Overlays - `7d1e828`
16. 16 - Palette Metadata Schema v1 - `2231a82`
17. 17 - Palette Browser and Quick Filter - `dac7964`
18. 18 - glTF UV Export - `0f305bf`
19. 19 - glTF Vertex Color Export - `72fc235`
20. 20 - glTF Material Baseline - `d8bef92`
21. 21 - VOX Transform Chunk Mapping v1 - `9da9a48`
22. 22 - VOX Multi-part Naming and Grouping - `c13180e`
23. 23 - Qubicle QB Import Feasibility Slice - `a32bd8b`
24. 24 - Qubicle QB Export Feasibility Slice - `4c32f65`
25. 25 - Solidify QA Diagnostics - `6ada55d`
26. 26 - Incremental Rebuild Telemetry - `0f4cd4e`
27. 27 - Dense Scene Stress Harness (64/96/128) - `f9266bd`
28. 28 - Frame-Time Hotspot Pass - `d083f64`
29. 29 - Memory Budget Instrumentation - `33b5085`
30. 30 - End-to-End Correctness Sweep - `bbfa6b6`
31. 31 - Interface Polish: Top Toolbar Quick Actions - `f79723a`
32. 32 - Interface Polish: Status HUD Badges - `253bc50`
33. 33 - Interface Polish: Command Palette - `f2938a9`
34. 34 - Interface Polish: Dock Layout Presets - `84752b8`
35. 35 - Interface Polish: Theme and Contrast Pass - `1bdeb04`
36. 36 - Interface Polish: Numeric Field Drag Scrub - `0b9802a`
37. 37 - Interface Polish: Tool Hotkey Overlay - `6434e82`
38. 38 - Interface Polish: Precision Input Mode - `2e5cc92`
39. 39 - Interface Polish: Startup Workspace Recovery UX - `e6e675e`
40. 40 - Interface Polish: Final UX Regression and Operator Pack - `fa7da2e`

## Usage Rules
- One task = one branch = one commit = merge to `main`.
- Do not merge to `stable` during implementation.
- If a gate fails, do not merge; log blocker in `Doc/DAILY_REPORT.md` and `Doc/CURRENT_STATE.md`.
