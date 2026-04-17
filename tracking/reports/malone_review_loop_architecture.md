# Review loop architecture

## Data flow

1. **Submit feedback** — `POST /api/malone/review/feedback` (owner/admin) calls `submit_review_feedback`.
2. **Event insert** — one row in `malone_review_feedback_events` with `review_state_before` / `after`.
3. **Head upsert** — `malone_review_artifact_heads` stores the latest state for queue queries.
4. **Domain sync** — governed columns (`NormalizedKnowledgeUnit.review_state`, `MaloneScenarioMemory.review_audit_status`, JSON `human_review` on traces/versions) update **without** touching raw source text.

## API surface

| Method | Path | Access |
|--------|------|--------|
| GET | `/api/malone/review/artifact-types` | Authenticated |
| GET | `/api/malone/review/queue` | owner/admin |
| GET | `/api/malone/review/head/{type}/{id}` | Authenticated |
| GET | `/api/malone/review/history/{type}/{id}` | owner/admin |
| POST | `/api/malone/review/feedback` | owner/admin |
| GET | `/api/malone/review/artifact-summary/{type}/{id}` | owner/admin |
| GET | `/api/malone/review/promotion/ingestion-source-version/{id}` | owner/admin |

## Malone

Chat responses include **`malone_governance`**: read-only hints derived from review heads for normalized units present in the truth packet.
