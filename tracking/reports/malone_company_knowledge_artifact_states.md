# Company Knowledge — Artifact State Model

## Review outcomes (API)

`approved`, `rejected`, `needs_revision`, `informational`, `risk_flag`, `ready_for_promotion`, `hold_for_review`.

## Lifecycle metadata (`company_knowledge_lifecycle`)

Mapped from outcomes for ingestion versions (human_review patch): e.g. approved → `approved_for_use`, ready_for_promotion → `validated`, hold_for_review / risk_flag / needs_revision → `under_review`, rejected → `rejected`.

## Head display states (representative)

| Artifact | Example head states |
|----------|---------------------|
| `ingestion_source_version` | `approved`, `validated`, `under_review`, `rejected`, `needs_revision`, `reviewed` |
| `normalized_unit` | Uses `NormalizedKnowledgeUnit.review_state` enum space |
| `website_pack_entry` | Includes `ready_for_promotion`, `approved`, `under_review`, … |

## Mechanical ingestion version status

Stored on `IngestionSourceVersion.status`: e.g. `draft`, `validated`, `promoted_active`, `archived`. Not interchangeable with legal handbook versioning.
