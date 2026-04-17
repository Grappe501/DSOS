# Legal Retrieval Scoping Plan

## Problem

Multiple handbook ingests (re-runs, test fixtures, PDF + text trials) can share one SQLite database. Lexical and citation queries must not return mixed versions unless explicitly requested.

## Mechanism

- **`legal_unit_chunks.legal_source_version_id`** — nullable for legacy rows; set on all new ingests from `arkansas_pipeline`.
- **APIs** accept optional `legal_source_version_id`:
  - `search_legal_chunks_lexical`
  - `find_chunks_by_citation_text`
  - `find_chunks_by_section_title`
  - `find_chunks_by_family_and_phrase`
  - `retrieve_legal_evidence_bundle` / `retrieve_legal_handbook_evidence` (wrapper)

## Behavior

- When `legal_source_version_id` is **provided**, SQL filters `LegalUnitChunk.legal_source_version_id == <id>`.
- When **omitted**, behavior matches pre-scoping (all chunks visible) for backward compatibility.
- Legacy chunks with `NULL` version id **do not match** a specific version filter.

## Caller responsibility

- Future Malone / admin flows should persist the active `legal_source_version_id` alongside proposals or session scope and pass it into retrieval.
