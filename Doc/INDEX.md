# Documentation Index

Use this folder as the canonical documentation source for daily execution.

## Core Planning
- `PROJECT_SPEC.md`: product specification and architecture intent.
- `ROADMAP_TASKS.md`: task sequence and acceptance criteria.
- `CURRENT_STATE.md`: historical baseline audit/context (snapshot).

## Execution & Handoff
- `DAILY_REPORT.md`: latest execution summary and test status.
- `TEAM_LEAD_REPORT.md`: leadership-facing consolidated report.
- `NEXT_WORKDAY.md`: startup checklist for the next dev session.
- `QUBICLE_COMPETITIVE_NOTES.md`: competitor parity notes and differentiation targets.

## Checklists
- `PACKAGING_CHECKLIST.md`: Windows packaging and smoke verification.
- `MANUAL_CHECKLIST_TASK_01_VIEWPORT_VISIBILITY.md`: viewport reproducibility checklist.

## Canonical Commands
- Run app: `python src/app/main.py`
- Run tests: `pytest -q`
- Convenience run script: `.\run.ps1`
- Packaging: `powershell -ExecutionPolicy Bypass -File .\tools\package_windows.ps1`

## Canonical Source Paths
- Canonical runtime/edit paths: `src/app`, `src/core`, `src/util`.
- Legacy reference path: `src/voxel_tool` (guarded by `tests/test_source_tree_guard.py`).
- If legacy files must change intentionally, update `tests/fixtures/legacy_tree_manifest.txt` in the same task.
