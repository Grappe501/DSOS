# Legal Handbook Persistence Contract (SQLite / SQLAlchemy)

## Required tables (v0)

Aligned with `schemas/legal_handbook_knowledge_v0.sql` and migration `0003`.

### Identity and edition

- **`legal_documents`:** one row per stable handbook identity (`stable_key` UNIQUE).
- **`legal_source_versions`:** immutable-ish snapshot per ingest (`version_label`, `compiled_publication_date`, `status`, checksum).

### Structure

- **`legal_document_families`:** `(legal_document_id, family_code)` UNIQUE; `embedded_source_revision_label` optional.
- **`legal_units`:** belong to a family; may reference `parent_legal_unit_id` (unused in slice; reserved for nested outlines).
- **`legal_unit_chunks`:** `ordinal` unique per `legal_unit_id`; `subsection_path` nullable for pre-subsection lead text.
- **`legal_citations`:** `citation_key` UNIQUE globally; FK to chunk.

### Provenance layers

- **`legal_date_layers`:** `scope_type` + `scope_id` + `layer_kind` (`compiled_publication` | `embedded_source_revision`).

### Jobs and traces

- **`legal_ingestion_jobs`:** status + stage for batch ingest.
- **`legal_answer_traces`:** optional `proposal_id` — future Malone audit (not written in this pass).

## Invariants

1. Every persisted chunk intended for retrieval has ≥1 `legal_citations` row in normal operation.
2. `normalized_citation` for statute-style units uses whitespace-stripped Ark. Code form (e.g. `17-92-115`).
3. Re-ingest with the same text should use a new `legal_documents.stable_key` or a versioning policy to avoid UNIQUE collisions.
