# Next Thread Prompt — After Phase 0 (Foundation)

You are continuing the **Malone** build (DSOS). Phases **0–6** are defined in the production plan; **phase 0** locks governance and migration continuity.

## Locked Rules

- **Active lane only:** `app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/`.
- **Do not modify:** `backend/`, `frontend/`, `dsos_replacements/`.
- **Hard-fail:** See `tracking/reports/malone_phase0_foundation_state.json` → `hard_fail_conditions`.
- **Migrations:** Order is `0001` → `0002` → `0003` → `0004` (legal handbook + chunk version scoping).

## What Phase 0 Established

- Explicit phase list (0–6) and artifact naming under `tracking/reports/`.
- Regulation layer (`0002`) precedes legal handbook layer (`0003`–`0004`).
- Voice is **out of scope** until after phase 6.

## Next: Phase 1 — Legal Source Modeling Foundation

1. Confirm ORM (`app/models/legal_handbook.py`) matches Alembic `0003`/`0004` and ingestion writers.
2. Document any gaps in `malone_phase1_modeling_report.md` + `_state.json`.
3. Add or tighten tests for core assumptions (imports, keys, scoping fields).
4. Run tests and fix failures before phase 2.

## Boot Files

- `tracking/reports/malone_phase0_foundation_report.md`
- `tracking/current_state.json` (update when changing global thread state)
