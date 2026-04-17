# Malone Phase 5 — Guarded Legal Lookup Experience

**Status:** Complete  
**Date:** 2026-04-16

## Summary

A **narrow, citation-first** handbook response path runs **inside Malone** when both flags are enabled: evidence is retrieved from the database, formatted deterministically, and returned without invoking the conversational LLM for that branch.

## Flags

| Variable | Effect |
|----------|--------|
| `MALONE_LEGAL_EVIDENCE_ENABLED=1` | Legal intent + evidence bundle + trace flush. |
| `MALONE_LEGAL_LOOKUP_ENABLED=1` | Deterministic delivery (`delivery_mode: legal_grounded_deterministic`). |

## UX constraints

- `legal_assistant/answer_formatter.format_legal_lookup_answer` — ordered citations, family/title/path/pages, excerpts, explicit **not legal advice** footer.
- `legal_assistant/guardrails.legal_handbook_forbidden_claims` — merged into truth packet forbidden claims.

## API

- Same `/api/malone/chat` surface; behavior is gated by env + message content (no broad public legal Q&A endpoint added).

## Audit

- `malone.delivery.legal_handbook` action logged; `legal_answer_traces` rows store chunk + citation key JSON.

## Verification

See `malone_phase5_lookup_state.json`.
