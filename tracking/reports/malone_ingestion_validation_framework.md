# Validation framework plan

## Outcomes

Every business ingest job can end with:

- **PASS** — no failures; no warnings (or warnings explicitly empty).
- **PASS_WITH_WARNINGS** — no failures; at least one warning.
- **FAIL** — one or more failures.

Classification uses `decide_overall_status` from `app/services/legal_ingestion/ingest_validate_status.py` (same ordering as Arkansas QA).

## Payload model

`ValidationPayload` holds:

- `failures`, `warnings` — string lists (human-readable, stable prefixes encouraged).
- `precheck` — file exists, DB reachable, schema present, etc.
- `structure` — parser outcomes (segment counts, profile id).
- `db_counts` — row counts (legal: families, units, chunks, citations; business segments TBD).
- `retrieval` — reserved for lexical/citation probes (optional; not required for policy in this pass).

## Persistence

One row per job in `ingestion_validations` (`ingestion_job_id` unique), with JSON columns mirroring payload sections for audit export.

## Legal profile checks

- Precheck: path readable (delegated to runner).
- Ingest: Arkansas result `status == completed`.
- DB: `legal_version_counts` for the `legal_source_version_id` — non-zero families and chunks; zero citations is a **warning**.

## Policy / scaffold profile checks

- Checksum computed from file bytes.
- At least one `ingestion_segment`; single segment only → **warning** (suggest improving headings).

## Combining results

`merge_payloads` exists for future multi-stage runs (precheck + structure + retrieval).

## Deferred

- Full retrieval probes for `ingestion_segments`; parity with `retrieval_is_broad_failure` for business content.
