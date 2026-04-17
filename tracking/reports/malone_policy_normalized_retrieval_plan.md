# Policy manual — normalized retrieval plan

## Scope

- Default `ingestion_source_version_id`: latest `policy_manual` `IngestionSourceVersion` by `updated_at`.
- Segment search: token overlap scoring over heading + body (deterministic, no embeddings).

## Normalized attachment

- Load units where `ingestion_segment_id` matches hit segments and version matches, same run validation filter as legal.
- Group up to two units per segment id.

## Intent trigger

- Message contains phrases such as `[policy]`, `policy manual`, `company policy`, `internal policy` (see `intent_service`).
- Requires `MALONE_POLICY_EVIDENCE_ENABLED` or defaults to following `MALONE_LEGAL_EVIDENCE_ENABLED` when unset.

## Delivery

- Deterministic path when `MALONE_POLICY_LOOKUP_ENABLED` (defaults aligned with policy evidence flag).
