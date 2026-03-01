# PARITY_RECHECK_PROMPT

You are the Programmer team (Codex) in The Trinity Loop.

MISSION:
Recompute parity after completing the current closure roadmap, using the same scoring rubric and categories.

Authoritative inputs:
1. `Doc/PARITY_SCORECARD.md`
2. `Doc/PHASE1_COMPLETION_DEFINITION.md`
3. `Doc/CURRENT_STATE.md`
4. `Doc/COMPETITIVE_ANALYSIS.md`
5. Current codebase on `main`

Rules:
- Docs + analysis only.
- No feature/code changes in this recheck step.
- Use identical rubric:
  - `0` missing
  - `0.5` partial/buggy/unstable
  - `1` baseline-equivalent
  - `1.2` better-than-baseline

Required outputs:
1. Update `Doc/PARITY_SCORECARD.md`
- Re-score all feature rows using the same IDs.
- Recompute:
  - Functionality parity %
  - Workflow/UX parity %
  - Stability/performance parity %
  - Weighted overall parity % (50/35/15 unless spec updates priorities)

2. Update `Doc/CURRENT_STATE.md`
- Update parity snapshot section with new percentages.
- Update top missing items list (only items still below `1.0`).

3. Update `Doc/DAILY_REPORT.md`
- Add parity delta report section including:
  - Features moved `0 -> 0.5`
  - Features moved `0.5 -> 1`
  - Features moved `0 -> 1`
  - Any regressions (`1 -> 0.5` or lower)
  - Remaining blockers for Phase 1 completion

4. Produce a short terminal summary:
- New parity percentages
- Net delta from previous run
- Top remaining 10 missing items

Stop after doc updates only.
