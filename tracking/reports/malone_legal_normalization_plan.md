# Legal handbook normalization plan

## Input

- `legal_source_version_id` (required)
- Optional `legal_document_id` (resolved from version if omitted)

## Source linkage

- Primary: `legal_unit_chunk_id` (+ `legal_unit_id`, `legal_document_id`, `legal_source_version_id`)
- `citation_keys_json`: from `legal_citations` rows for the chunk
- `anchor_json`: unit id, chunk id, primary citation, page range

## v1 algorithm (`legal_handbook_v1`)

1. Load all `legal_unit_chunks` for the version (ordered by unit + chunk ordinal).
2. For each non-empty chunk body, run **keyword signals** (definitions, shall/must, prohibitions, exceptions, reporting, escalation).
3. Map signals → `normalized_unit_type` + `action_type` + `requirement_level` (deterministic precedence in `legal_normalizer._classify_unit`).
4. Set `plain_language_summary` to first sentence heuristic.
5. Set `confidence_level` from match count + text length.
6. Default `review_state` = `system_generated`.

## Future

- Subsection-aware splitting inside very large chunks.
- Cross-reference–aware exception linking.
- Tighter coupling to family_code from `legal_units` / anchors for role scoping.
