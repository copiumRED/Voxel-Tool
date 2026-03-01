# NEXT_WORKDAY

Date Prepared: 2026-03-01
Prepared By: Codex

## Workday Definition
- Complete `Doc/ROADMAP_TASKS.md` Tasks **01-30** in order.
- One task per branch, merge to `main` only after required self-test gate passes.
- No stable merges during the day.

## 10-Minute Smoke Checklist
1. `git checkout main`
2. `git status` (must be clean)
3. `python src/app/main.py` (launch smoke)
4. In app: `Debug -> Create Test Voxels (Cross)` and `View -> Frame Voxels`
5. Tool smoke:
- Brush paint/erase in both pick modes
- Box and line drag preview/apply once each
- Fill once (small region)
6. IO smoke:
- Save project once
- Open project once
7. Export smoke:
- Export OBJ once
- Export glTF once
- Export VOX once
8. `pytest -q`
9. Packaging prep smoke:
- Run `tools/package_windows.ps1`
- Confirm `ARTIFACT_*` lines print
- Build portable zip and record SHA256

## First 3 Tasks to Execute (and Why)
1. Task 01: Unify Edit Plane Axis Contract
- Why: This removes foundational coordinate ambiguity that causes user-facing placement errors and confusion.

2. Task 02: Non-Brush 3D Target Resolver v1
- Why: This is the highest-impact correctness fix for daily editing productivity and parity.

3. Task 03: Apply Pick Mode to Line/Box/Fill
- Why: Completes targeting consistency across all primary tools and reduces workflow surprises.

## Today Objective
Today focuses on Phase 1 correctness hardening before feature expansion: eliminate targeting inconsistencies, close high-impact export/IO correctness gaps, and then move through Qubicle-parity productivity upgrades with measurable test coverage. Success means the editor behaves predictably across tools, exports truthfully, and is ready for another full operator validation cycle.

## Packaging Prep Objective
Before end-of-day handoff, ensure portable zip packaging steps are operator-ready and installer prerequisites are explicitly documented for the next cycle.

## Operator End-of-Day Validation Checklist
1. Confirm `main` is clean and up to date locally.
2. Launch app: `python src/app/main.py`.
3. In app, run viewport smoke:
- `Debug -> Create Test Voxels (Cross)`
- Orbit/zoom/pan
- `View -> Frame Voxels`
4. Run core workflow smoke:
- Brush paint/erase
- Box and line preview/apply
- Fill small region
5. Run IO/export smoke:
- Save/Open once
- Export OBJ/glTF/VOX once each
6. Run `pytest -q` and verify all tests pass.
7. Run packaging checklist including portable zip/hash verification.
8. Only after all checks pass: approve promotion of `main` to `stable`.
