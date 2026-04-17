# Review / governance handoff

Each ingested artifact (when not dry-run) includes:

```json
"review_handoff": {
  "governance": "use_malone_review_api",
  "artifact_hint": "ingestion_source_version",
  "version_id": "<uuid>"
}
```

Human reviewers can use **`GET /api/malone/review/promotion/ingestion-source-version/{id}`** and **`POST /api/malone/review/feedback`** (owner/admin) with `artifact_type=ingestion_source_version` to record approval / needs_revision without rewriting source segments.

Manifest fields **`review_recommendation`** and **`ingestion_priority`** support triage before promotion.
