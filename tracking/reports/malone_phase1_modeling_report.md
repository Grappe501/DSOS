# Malone Phase 1 — Legal Source Modeling Foundation

**Status:** Complete  
**Date:** 2026-04-16

## Summary

The legal handbook persistence model remains **coherent and production-directed**: document → source version → family → unit → chunk → citation, with optional cross-refs and date layers. ORM definitions in `app/models/legal_handbook.py` align with Alembic `0003_legal_handbook_knowledge_foundation` plus `0004_legal_unit_chunk_source_version` (`legal_unit_chunks.legal_source_version_id`).

## Alignment

| Layer | Schema reference | Migration |
|-------|-------------------|-----------|
| Core tables | `schemas/legal_handbook_knowledge_v0.sql` (reference) | `0003` |
| Version scoping on chunks | ORM + migration | `0004` |

Ingestion (`app/services/legal_ingestion/arkansas_pipeline.py`) sets `legal_source_version_id` on each `LegalUnitChunk` at write time.

## Versioning / citations / dates

- **Citation keys** — `stable_citation_key` + `LegalCitation.citation_key` (unique).
- **Page grounding** — `page_start` / `page_end` on units and chunks when PDF map present.
- **Date layering** — `LegalDateLayer` + ingestion helpers (`date_layering.py`) for compilation and embedded revisions.

## Tests

- `tests/test_legal_malone_integration.py` — in-memory DB proves FK chain and retrieval scoping.
- Existing `tests/test_family_boundary.py`, `test_page_mapping.py` — parsing invariants.

## Deferred

- Broader ORM relationship() graph for navigation (optional; queries use explicit joins today).

## Verification

See `malone_phase1_modeling_state.json`.
