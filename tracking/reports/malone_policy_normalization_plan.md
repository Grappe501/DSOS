# Policy manual normalization plan

## Input

- `ingestion_source_id` + `ingestion_source_version_id` (both required)
- `source_type` = `policy_manual`

## Source linkage

- Primary: `ingestion_segment_id`
- `ingestion_source_version_id` / `ingestion_source_id` denormalized on each unit for querying
- `anchor_json`: segment id, `anchor_key`, ordinal

## v1 algorithm (`policy_manual_v1`)

1. Load `ingestion_segments` for the version (ordinal order).
2. Run the same **signal extractors** as legal on segment body (+ heading).
3. Classify into `policy_rule`, `definition`, `escalation_rule`, etc.
4. `applies_to_role` when present in segment `meta_json` (`applies_to_role` or `role`).

## Future

- Structured metadata dimensions aligned with `ingestion_tag_assignments`.
- Explicit approval / review fields when stored in segment meta.
- Step graphs for procedures sharing the policy splitter.
