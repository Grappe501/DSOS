# Reviewable artifacts model

Artifacts are addressed by **`(artifact_type, artifact_id)`** — no per-type review tables required.

## States

- **Normalized units**: reuse `review_state` on `normalized_knowledge_units` (`draft`, `system_generated`, `under_review`, `reviewed`, `approved`, `rejected`, `needs_revision`, `superseded`).
- **Scenario memory**: `review_audit_status` (`pending`, `under_review`, `reviewed`, `approved`, `rejected`, `needs_revision`, `superseded`).
- **Traces / versions**: JSON under `meta_json.human_review` for audit overlays.

## Heads vs events

- **Events**: full audit trail (append-only).
- **Heads**: current snapshot for UX and queues; superseded by new events, never deleted when rejecting.
