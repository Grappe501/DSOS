# Next Thread — Legal Vertical Slice Continuation

You are continuing the DSOS / Malone build after the **Malone Legal Handbook Vertical Slice** pass (2026-04-16).

## What was completed

- ORM: `app/models/legal_handbook.py` (imported from `app/main.py` for metadata registration).
- Ingest pipeline: `app/services/legal_ingestion/arkansas_pipeline.py` → families, units, subsection chunks, citations, date layers.
- Retrieval: `app/services/legal_retrieval/lexical.py`, `citation_lookup.py`, `hybrid.py` (lexical-only).
- Regulation foundation bridges: `app/services/ingestion/parser.py`, `chunker.py`, `knowledge/source_registry.py`, `retrieval/lexical.py`, `retrieval/hybrid.py`, `assistant/*` stubs.
- Tracking: `malone_legal_vertical_slice_report.md`, `malone_legal_vertical_slice_state.json`, Arkansas plan, parsing/persistence/lexical contracts, this prompt.
- Fixture: `tracking/fixtures/arkansas_handbook_vertical_slice_sample.txt`.

## Active vs passive roots

- **Active:** `app/`, `schemas/`, `alembic/`, `tracking/`.
- **Do not modify:** `backend/`, `frontend/`, `dsos_replacements/`.

## Immediate next work

1. Integrate **PDF text extraction** with **page numbers** mapped into `page_start` / `page_end`.
2. Add **version-scoped queries** (filter by `legal_source_version_id`) for retrieval to avoid duplicate dev data noise.
3. Optional: extend `truth_packet_service.build_truth_packet` with **`legal_handbook_evidence`** populated only when a regulation/legal intent branch is added to `intent_service` (feature-flagged).
4. **FTS5** (or equivalent) when LIKE performance is insufficient.
5. Populate **`legal_cross_references`** with resolver pass.

## Hard-fail conditions (unchanged)

- Modify passive roots; replace Malone wholesale; code without integration purpose; abandon versioning + citations; skip tracking; ship speculative Q&A before persisted evidence.

## Read first

- `tracking/reports/malone_legal_vertical_slice_report.md`
- `app/services/legal_ingestion/arkansas_pipeline.py`
- `app/services/truth_packet_service.py`
- `schemas/legal_handbook_knowledge_v0.sql`

Begin by wiring PDF extraction behind the same ingest entrypoint while preserving deterministic citation keys.
