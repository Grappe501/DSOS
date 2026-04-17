# Next Thread — Post PDF Grounding

You are continuing DSOS / Malone after the **PDF grounding pass** (2026-04-16).

## Completed

- PDF extraction (`pypdf`), linear corpus + `PageMap`, page fields on families/units/chunks, enriched citation anchors, `legal_source_version_id` scoping, Alembic `0004`, smoke script `tracking/scripts/pdf_grounding_smoke.py`.
- Tracking: `malone_pdf_grounding_pass_report.md`, `malone_pdf_grounding_pass_state.json`, extraction/page/scoping contracts, this prompt.

## Active lanes

`app/`, `schemas/`, `alembic/`, `tracking/` — do **not** edit `backend/`, `frontend/`, `dsos_replacements/`.

## Suggested next pass

1. **TOC tuning** for the real PDF: improve `toc_parser` / family detection so A–H families match the compiled handbook (may require PDF-specific markers or TOC page range hints).
2. **FTS5** or token index for large corpora; keep version scoping in all queries.
3. **Truth-packet hook** (feature-flagged): attach scoped chunk + citation evidence when regulation intent exists.
4. Optional: **cross-reference** extraction using page-grounded spans.

## Hard-fail conditions

No passive-root edits, no wholesale Malone replacement, no speculative user-facing legal Q&A before evidence paths are stable, no skipping tracking updates for the slice you ship.

## Read first

- `tracking/reports/malone_pdf_grounding_pass_report.md`
- `app/services/legal_ingestion/arkansas_pipeline.py`
- `app/services/legal_retrieval/lexical.py`
