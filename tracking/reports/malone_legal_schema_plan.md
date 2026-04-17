# Malone Legal Schema Plan (v0)

## Purpose

Define persistent structures for a **compiled pharmacy law handbook** (Arkansas ASBP “Statutes and Rules”) so Malone can cite **Ark. Code sections**, **board rule sections**, **TOC families (A–H)**, **subsection paths**, and **page anchors** without treating the PDF as a flat document.

## Relationship to regulation_knowledge (0002)

- **`regulation_*` tables** (migration `0002_regulation_knowledge_foundation`): generic regulation source, version, chunk, citation, tags, jobs, traces.
- **`legal_*` tables** (migration `0003_legal_handbook_knowledge_foundation`): **handbook decomposition**—families, units, subsection chunks, cross-references, explicit date layers.

Neither replaces the other in v0. A later pass may link rows via stable keys in `meta_json` or a dedicated join table.

## Table inventory (v0)

| Table | Role |
|-------|------|
| `legal_documents` | Uploaded file identity, checksum, compiled edition label, cover metadata. |
| `legal_source_versions` | Ingest snapshots / versions for the same logical document. |
| `legal_document_families` | TOC major sections (A–H), page spans, embedded family revision labels. |
| `legal_units` | Statute blocks, rule sections, nested nodes; `primary_citation`, hierarchy. |
| `legal_unit_chunks` | Retrieval slices with `subsection_path`, text, page/char spans. |
| `legal_citations` | Unique `citation_key`, `authority_type`, `anchor_json`. |
| `legal_cross_references` | Extracted refs; optional resolution to `to_legal_unit_id`. |
| `legal_date_layers` | Edition vs embedded act dates vs printed effective notes (scoped). |
| `legal_tags` / `legal_chunk_tags` | Controlled taxonomy. |
| `legal_ingestion_jobs` | Pipeline tracking. |
| `legal_answer_traces` | Malone proposal linkage + chunk/citation evidence. |

## Citation key strategy (recommended)

- Namespace by kind, e.g. `ark_statute:17-92-115`, `asbp_rule:<family>:<section_label>`, plus disambiguators when collisions occur.
- Store display strings in `normalized_citation` and machine keys in `citation_key`.

## Anchor JSON (flexible)

Suggested keys: `page`, `page_end`, `pdf_object_id` (if available), `char_start`, `char_end`, `family_code`, `subsection_path`, `source_family_title`.

## DDL locations

- Reference SQL: `schemas/legal_handbook_knowledge_v0.sql`
- Alembic: `alembic/versions/0003_legal_handbook_knowledge_foundation.py`

## ORM follow-up

SQLAlchemy models are **not** added in this foundation pass to avoid drift from migrated SQLite; next pass should add models under `app/models/` or a dedicated module and align with `meta_json` naming conventions (`metadata` is reserved).
