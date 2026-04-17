# Dimensional tagging framework

## Principles

- Tags are **dimensional**: the same string in two dimensions means different things (e.g. `domain=operations` vs `topic=operations`).
- Definitions are **normalized** per `(dimension, slug)` to avoid unbounded duplicate labels.
- Assignments bind tags to **version-scoped** or **segment-scoped** targets for audit and retrieval filters later.

## Dimensions (minimum)

| Dimension | Typical use |
| --- | --- |
| `domain` | Business area (e.g. Pharmacy Operations, HR). |
| `topic` | Subject matter cluster. |
| `document_type` | Policy, SOP, memo, contract excerpt, etc. |
| `role` | Audience (PIC, technician, billing). |
| `action_type` | Obligation vs guidance vs reference. |
| `review_state` | Draft, approved, expired, needs_review. |

Code constants: `app/services/ingestion_control/tagging.py` (`TAG_DIMENSIONS`).

## Storage model

- `ingestion_tag_definitions`: `dimension`, `slug`, `label`, optional `parent_id` for hierarchies later.
- `ingestion_tag_assignments`: `tag_definition_id`, `target_kind` (`source_version` | `segment`), `target_id`.

## API helpers

- `ensure_tag_definition` — idempotent create-by dimension+slug.
- `assign_tag` — idempotent assignment (duplicate assignments skipped).
- `tag_source_version_from_map` — convenience for CLI (`--tags-json`) mapping dimension → label (slug derived).

## Deferred

- Hierarchical browsing UI; graph edges between tags; automated tag suggestions from LLMs (out of scope for this pass).
