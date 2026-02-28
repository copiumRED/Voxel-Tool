# NEXT_WORKDAY

Date Prepared: 2026-02-28  
Prepared By: Codex

## First 10 Minutes Checklist
1. `git checkout stable`
2. `git pull`
3. `python src/app/main.py`
4. Confirm viewport:
   - grid/axes visible
   - status bar shows viewport ready details
5. Quick edit smoke:
   - `Debug -> Create Test Voxels (Cross)`
   - brush paint adds voxel
   - erase removes voxel
6. Export smoke:
   - export OBJ once
   - export VOX once
7. `pytest -q`

## Today's Objective
Today’s objective is to convert the current “feature-complete but uneven” voxel editor into a Phase 1 production-usable baseline with Qubicle-like editing confidence. The focus is not adding mesh-edit complexity yet; it is strengthening voxel workflow speed, predictability, and reliability: robust viewport behavior, intuitive targeting feedback, practical part management, safer operations, and export trust. Success means an indie user can reliably block out, iterate, and export assets without uncertainty or hidden failure modes.

## First 3 Roadmap Tasks to Execute
1. Task 01: Viewport Health Overlay + Startup Diagnostics
- Why: rendering confidence is the first blocker; all other workflow work depends on reliable visual feedback.

2. Task 02: First-Voxel UX Preview (Hover Cell/Face)
- Why: edit targeting must be obvious to reduce “tool not working” perception and improve usability immediately.

3. Task 03: Part Actions v1 (Delete/Duplicate)
- Why: object workflow completeness is core Qubicle parity and is needed for practical scene iteration.
