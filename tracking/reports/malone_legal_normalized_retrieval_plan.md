# Legal handbook — normalized retrieval plan

## Scope

- `legal_source_version_id` from the legal evidence bundle (default: latest ingested version).
- Chunk ids from lexical/citation retrieval hits.

## Query rules

- Join `normalized_knowledge_units` → `normalization_runs` where `validation_status ∈ {PASS, PASS_WITH_WARNINGS}`.
- Exclude `superseded` and `review_state == rejected`.
- Sort by review rank, then confidence, then id; keep up to **two** units per chunk.

## Orphans

- If no normalized rows exist for chunk ids, `normalized.fallback_reason` documents `no_matching_normalized_units`.
- Raw items are unchanged; answer still citation-first.

## Family / page context

- Preserved on raw items; normalized `anchor_json` on units may duplicate citation metadata for audit.
