# Malone Phase 0 — Foundation / Governance Stability

**Status:** Complete (this pass)  
**Date:** 2026-04-16  
**Scope:** Active lane only (`app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/`).

## Goals Met

1. **Governance** — Malone continues to use the existing proposal → validation → workflow → truth packet → render path. Legal work is additive (evidence bundle + optional deterministic legal delivery), not a second agent.
2. **Active-lane discipline** — Do not modify `backend/`, `frontend/`, or `dsos_replacements/`. Parallel roots remain passive; authoritative application code for this workstream is under `app/` and UI under `src/` per repo conventions.
3. **Phase plan (0–6)** — Phases are sequential: foundation → legal model coherence → ingestion stability → retrieval hardening → evidence in Malone → guarded lookup → production hardening. Voice remains deferred until after phase 6.
4. **Hard-fail rules** — Recorded in this report, in `malone_phase0_foundation_state.json`, and in execution prompts. Any run that violates them is invalid.

## Hard-Fail Conditions (must not violate)

- Modify `backend/`, `frontend/`, or `dsos_replacements/` for this workstream.
- Replace Malone’s existing request path or add a parallel “second agent” orchestrator.
- Ship speculative public legal Q&A before internal evidence retrieval is wired.
- Break versioning, citation keys, or page-grounding direction for handbook rows.
- Skip required tracking outputs for the phase.
- Begin voice implementation before phases 0–6 are complete.

## Migration Continuity (regulation + legal handbook)

Alembic chain (linear):

| Revision | Purpose |
|----------|---------|
| `0001_v070_department_workflow` | Core workflow / Malone tables |
| `0002_regulation_knowledge_foundation` | Regulation knowledge (regulation_* tables) |
| `0003_legal_handbook_knowledge_foundation` | Legal handbook: documents, versions, families, units, chunks, citations, traces, etc. |
| `0004_legal_unit_chunk_source_version` | Adds `legal_source_version_id` to `legal_unit_chunks` for ingest/version scoping |

**Direction:** New legal rows must remain tied to `legal_source_versions` where applicable; retrieval filters on `legal_source_version_id` to prevent cross-version bleed.

## Consolidated Phase Tracking

- Phase reports and machine-readable state: `tracking/reports/malone_phase{N}_*_report.md` and `*_state.json`.
- Handoffs: `tracking/reports/NEXT_THREAD_PROMPT_PHASE{N}.md`.
- Post–phase 6: `malone_phases_0_to_6_completion_report.md`, `malone_phases_0_to_6_completion_state.json`, `NEXT_THREAD_PROMPT_POST_PHASE6.md`.

## Ambiguity Resolved

- **“Internal evidence path”** means persisted `legal_unit_chunks` + `legal_citations` (and related tables), retrieved via `app/services/legal_retrieval/`, not web search, for handbook-grounded answers.
- **“Guarded legal lookup”** means feature-flagged, citation-first, non-advice framing; not broad legal counseling.

## Deferred

- Embeddings / vector hybrid leg (still optional; lexical path is production-directed MVP).
- Voice UX (explicitly after phase 6).

## Verification (phase exit)

- Repository checks run after this phase: see `malone_phase0_foundation_state.json` → `verification.commands`.
