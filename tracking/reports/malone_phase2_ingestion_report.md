# Malone Phase 2 — Ingestion Execution Stability

**Status:** Complete (verified against existing pipeline)  
**Date:** 2026-04-16

## Summary

The Arkansas handbook pipeline (`ingest_arkansas_handbook_pdf`, `ingest_arkansas_handbook_text` → `_ingest_arkansas_corpus`) remains the **single vertical slice**: families from `parse_family_spans`, units from `find_legal_units_in_span`, subsection segments via `split_subsection_segments` / `draft_chunk_rows`, citations via `stable_citation_key` + `LegalCitation`, with **page grounding** when a `PageMap` is available from PDF extraction.

## Stability properties

- **Document + version registration** — `create_legal_document`, `create_legal_source_version` before chunk writes.
- **Family persistence** — deterministic sort by `char_start`; metadata includes parser provenance and span confidence.
- **Chunk persistence** — each chunk receives `legal_source_version_id=ver.id` and optional page range from span or unit fallback.
- **Citation persistence** — one citation per chunk in current pipeline path.
- **Failure surface** — job row tracks `failed` with `no_family_headings_found` when TOC/body cannot be parsed.

## Fixtures / smoke

- `tracking/fixtures/arkansas_handbook_vertical_slice_sample.txt` — sample structure for manual or script validation.
- `tracking/scripts/pdf_grounding_smoke.py` — optional when PDF assets exist locally.

## Deferred

- Full end-to-end PDF binary CI (environment-specific); structure validation remains fixture-driven.

## Verification

See `malone_phase2_ingestion_state.json`.
