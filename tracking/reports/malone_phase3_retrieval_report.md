# Malone Phase 3 — Retrieval Hardening

**Status:** Complete  
**Date:** 2026-04-16

## Summary

Retrieval modules now reduce **duplicate/version bleed** and improve **determinism** for evidence bundling.

## Changes

1. **`lexical.search_legal_chunks_lexical`** — `order_by(LegalUnitChunk.id)`; dedupe by `legal_unit_chunk.id` when SQL joins multiply rows.
2. **`citation_lookup`** — dedupe hydrated chunks by chunk id; same for family+phrase and title search loops.
3. **`hybrid.retrieve_legal_evidence_bundle`** — unchanged contract; continues to wrap lexical for a single call site.

## Scoping

- `legal_source_version_id` filter remains mandatory for version-safe callers.
- Family span confidence filtering remains available via `min_family_span_confidence` on lexical search.

## Deferred

- FTS / pgvector — not required for current SQLite MVP; hybrid stub documents `embedding_leg: disabled`.

## Verification

See `malone_phase3_retrieval_state.json`.
