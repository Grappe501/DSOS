# Company Knowledge Review + Promotion — Architecture Note

## Flow

1. **Ingest / normalize** — Unchanged: `IngestionSource` / `IngestionSourceVersion`, segments, `NormalizedKnowledgeUnit`.
2. **Review** — `POST /api/malone/review/feedback` with `artifact_type` + `artifact_id` + `outcome` (+ optional `meta_json`). Writes events and heads; syncs governed fields.
3. **Promotion (activation)** — Separate explicit step: `POST /api/malone/review/company-knowledge/promote-version` calls `promote_source_version` after verifying review head is `approved` (unless `require_prior_approval` is disabled for exceptional ops).
4. **Archive / supersede** — `POST .../archive-version` runs `archive_source_version` then records informational review feedback with lifecycle metadata.

## Components

| Layer | Role |
|-------|------|
| `review_store.submit_review_feedback` | Single write path for human decisions |
| `ingestion_control.promotion` | Mechanical status + `retrieval_ready` |
| `company_knowledge_promotion` | Company-scoped listing and guarded orchestration |
| `governance_hints` | Read-only telemetry for turns using policy/SOP bundles |

## Website pack

Pack lines use `artifact_type=website_pack_entry` with stable string IDs; manifest files on disk are not mutated. Review state is DB-only (heads + events).
