# Review vs promotion interaction

## Ingestion source versions

Human **approval** on `ingestion_source_version` sets `meta_json.human_review.promotion_ready` when outcome is `approved`. The API **`/promotion/ingestion-source-version/{id}`** returns:

- `retrieval_ready_db` — existing column from the control plane.
- `review_head_approved` — whether the artifact head is `approved`.
- `promotion_hint` — advisory string (`approved_for_promotion` vs `needs_review_or_validation`).

## Non-overrides

- Ingestion **validation** and **retrieval_ready** flags from jobs remain authoritative for technical readiness.
- Review cannot mark a broken ingest as production-ready without passing validation elsewhere.

## Website pack entries

Stable string IDs (e.g. `allcare:page:services`) store **events + heads only**; manifest files on disk are unchanged. Optional `meta_json` on the event can carry priority for downstream tooling.
