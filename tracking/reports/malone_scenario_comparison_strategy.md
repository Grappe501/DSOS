# Scenario comparison strategy

## Retrieval

- Scan recent **active** scenario memories (capped scan window in code).
- Score: exact **prompt fingerprint** match → high score; else **Jaccard token overlap** on normalized prompts.
- Penalize differing **intent targets**.
- Attach **source version drift** warnings when flattened version ids differ between current snapshot and prior row.

## Comparison object

`compare_to_prior_row` exposes overlaps, pattern ids, route ids, workflow enabled flags, and `weak_match_warning` when token similarity is below a conservative threshold.

## Non-goals

- No automatic “this is the same case” conclusion.
- No ranking of memories over current chunks or citations.
