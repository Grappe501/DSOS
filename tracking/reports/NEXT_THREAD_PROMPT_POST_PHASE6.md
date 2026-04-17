# Next Thread — Post Phase 6 (Voice-Ready Handoff)

You are continuing **DSOS / Malone** after completion of **Malone legal phases 0–6**.

## Locked invariants

- **Active lane:** `app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/`.
- **Do not modify:** `backend/`, `frontend/`, `dsos_replacements/` unless a separate reconciliation thread explicitly authorizes it.
- **Handbook evidence** remains on the shared Malone spine (`handle_malone_request`); no parallel agent.

## Legal slice state

- Feature flags: `MALONE_LEGAL_EVIDENCE_ENABLED`, `MALONE_LEGAL_LOOKUP_ENABLED` (see `tracking/current_state.json` → `malone_legal_phases_0_to_6`).
- Evidence bundle: `truth_packet.legal_evidence`
- Deterministic lookup delivery mode: `legal_grounded_deterministic`
- Audit: `legal_answer_traces` + `malone.delivery.legal_handbook` audit action

## Voice workstream (next)

- Start from design docs under `tracking/` (voice planning is **docs-only** until this point).
- Preserve text-first behavior; voice is additive and must not bypass handbook grounding rules.

## Boot checklist

1. Read `tracking/reports/malone_phases_0_to_6_completion_report.md`
2. Read `tracking/reports/malone_phases_0_to_6_completion_state.json`
3. Run `python -m pytest tests -q` and `python tools/self_verify_bootstrap.py`

## Do not regress

- Citation keys, `legal_source_version_id` scoping, page-grounding fields on chunks/units.
