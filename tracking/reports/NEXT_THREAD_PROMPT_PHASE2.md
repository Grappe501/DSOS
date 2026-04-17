# Next Thread — After Phase 2 (Ingestion)

## Completed

- Arkansas ingest path documented; version + chunk linkage verified in code review.

## Next: Phase 3 — Retrieval Hardening

- Focus on `app/services/legal_retrieval/` — citation lookup, lexical scoping, deduplication, deterministic ordering.
- Add/adjust tests for retrieval edge cases (empty DB, duplicate rows).

## Constraints

- Active lane only; no parallel agent; voice deferred.
