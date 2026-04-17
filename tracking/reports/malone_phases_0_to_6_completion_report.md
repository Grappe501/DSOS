# Malone — Phases 0–6 Completion Report

**Run date:** 2026-04-16  
**Scope:** Active lane only (`app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/`).

## Executive summary

Phases **0 through 6** are delivered as a **coherent, additive** legal-handbook slice on the existing Malone spine: governance artifacts, stable legal data model alignment, ingestion direction unchanged but documented, retrieval deduplication/scoping improvements, **feature-flagged** legal evidence in the truth packet, **optional** deterministic citation-first lookup, hardening + tests. **Voice remains deferred.**

## Phase deliverables (artifacts)

| Phase | Report | State JSON | Handoff prompt |
|-------|--------|------------|----------------|
| 0 | `malone_phase0_foundation_report.md` | `malone_phase0_foundation_state.json` | `NEXT_THREAD_PROMPT_PHASE0.md` |
| 1 | `malone_phase1_modeling_report.md` | `malone_phase1_modeling_state.json` | `NEXT_THREAD_PROMPT_PHASE1.md` |
| 2 | `malone_phase2_ingestion_report.md` | `malone_phase2_ingestion_state.json` | `NEXT_THREAD_PROMPT_PHASE2.md` |
| 3 | `malone_phase3_retrieval_report.md` | `malone_phase3_retrieval_state.json` | `NEXT_THREAD_PROMPT_PHASE3.md` |
| 4 | `malone_phase4_evidence_report.md` | `malone_phase4_evidence_state.json` | `NEXT_THREAD_PROMPT_PHASE4.md` |
| 5 | `malone_phase5_lookup_report.md` | `malone_phase5_lookup_state.json` | `NEXT_THREAD_PROMPT_PHASE5.md` |
| 6 | `malone_phase6_hardening_report.md` | `malone_phase6_hardening_state.json` | `NEXT_THREAD_PROMPT_PHASE6.md` |

## Code highlights (integration purpose)

- `app/services/legal_evidence_service.py` — evidence bundle + truth-packet enrichment + trace persistence.
- `app/services/malone_service.py` — wires bundle, enrichment, deterministic legal delivery branch.
- `app/services/truth_packet_service.py` — legal handbook web-search off; clarification bypass for legal.
- `app/services/intent_service.py` — env-gated `legal_handbook` intent.
- `app/services/legal_assistant/answer_formatter.py` — citation-first deterministic text.
- `app/services/legal_assistant/guardrails.py` — forbidden-claim extensions.
- `app/services/legal_retrieval/lexical.py`, `citation_lookup.py` — dedupe + ordering.

## Environment flags

- `MALONE_LEGAL_EVIDENCE_ENABLED` — enable legal intent + evidence bundle + traces.
- `MALONE_LEGAL_LOOKUP_ENABLED` — deterministic citation-first delivery (requires evidence flag).

## Verification executed (this run)

- `python -m pytest tests -q` — pass  
- `python -m compileall app -q` — pass  
- `alembic upgrade head` — pass (SQLite)  
- `npm run build` — pass  
- `python tools/self_verify_bootstrap.py` — pass  

## Production-ready (within stated constraints)

- Internal evidence-backed handbook lookup path with audit logging, when flags and data are present.
- Retrieval scoping and deduplication sufficient for SQLite MVP.

## Deferred / next

- Vector retrieval, richer intent classification, LLM prompt consumption of evidence when lookup is off.
- Voice UX — follow `NEXT_THREAD_PROMPT_POST_PHASE6.md`.
