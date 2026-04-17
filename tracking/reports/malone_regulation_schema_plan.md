# Regulation Knowledge Schema Plan (v0)

**Audience:** implementers adding ORM models and migrations.  
**Live DB today:** SQLite (`sqlite:///./runtime_v5.db` in `app/db/session.py`).  
**Companion DDL:** `schemas/regulation_knowledge_v0.sql`  
**Alembic draft:** `alembic/versions/0002_regulation_knowledge_foundation.py`

## Design principles

1. **Boring tables:** string IDs (UUID strings) consistent with existing `app/models/models.py` style.
2. **No `metadata` column name** in SQLAlchemy models—use `meta_json` if extra JSON is needed (matches project convention in `docs/architecture/WORKING_ARCHITECTURE.md`).
3. **Version is the truth anchor:** users cite **a version** of **a source**; chunks belong to versions.
4. **JSON as TEXT** in SQLite for portability; Postgres migration can switch to JSONB later.

## Entity relationships

```
regulation_sources (1) ──< regulation_source_versions (1) ──< regulation_chunks
                                                      │
                                                      ├──< regulation_ingestion_jobs
regulation_tags (1) ──< regulation_chunk_tags >── (M) regulation_chunks

regulation_chunks (1) ──< regulation_citations

malone_proposals (0..1) <── regulation_answer_traces (optional proposal_id)
```

## Table purposes

### `regulation_sources`

- **Identity:** `stable_key` (e.g. `CA_BOP_HANDBOOK_2024`) for deduplication across uploads.
- **Classifiers:** `source_type` (handbook, statute, memo, board_notice), `issuing_authority`, `jurisdiction` (state code, federal, etc.).
- **meta_json:** free-form (URLs, contact, notes)—not trusted for retrieval.

### `regulation_source_versions`

- **Immutability:** one row per ingestable revision; never overwrite body text in place—add a new version.
- **Temporal:** `effective_date`, `superseded_at`, `status` (`draft`, `active`, `superseded`, `retired`).
- **Integrity:** `content_checksum` or `storage_uri` for provenance (hash preferred for deterministic audits).

### `regulation_chunks`

- **Structure:** `ordinal` for stable ordering; `heading_path` human breadcrumb; `body_text` full chunk text.
- **Semantics:** `rule_type` (definition, requirement, prohibition, procedure); `plain_summary` for UI/snippets.
- **Retrieval:** `retrieval_ready` boolean; optional `embedding_ref` for external/blob embedding storage.
- **meta_json:** parser diagnostics, page ranges, source offsets.

### `regulation_citations`

- **Stable citation_key:** short string suitable for UI and logs (e.g. `CA-BOP-2024-§1730.1#ch-042`).
- **anchor_json:** structured offsets, section numbers, page numbers—whatever the handbook supports.

### `regulation_tags` / `regulation_chunk_tags`

- **Taxonomy:** controlled tags (e.g. `dispensing`, `controlled_substances`, `recordkeeping`).
- Many-to-many only on chunks to avoid tag explosion at version level.

### `regulation_ingestion_jobs`

- **Stages:** `queued` → `parsing` → `chunking` → `indexed` → `completed` / `failed`.
- **Linkage:** optional `source_version_id` once known; errors in `error_message`.

### `regulation_answer_traces`

- **Audit:** optional `proposal_id` → `malone_proposals.id` when the answer went through Malone.
- **Evidence:** `chunk_ids_json` list of chunk primary keys used; `verified` mirrors whether delivery passed verification.
- **meta_json:** model, temperature (if any), rerank scores—keep PII out.

## Retrieval readiness

- **MVP:** lexical search over `body_text` / `plain_summary` (FTS5 in a follow-on migration or separate virtual table).
- **Future:** `regulation_chunk_embeddings` table or external vector store; not required for schema v0.

## Assumptions

- Single-tenant AllCare deployment; no `tenant_id` in v0.
- File storage may remain local disk or S3-compatible later—`storage_uri` is opaque string.
