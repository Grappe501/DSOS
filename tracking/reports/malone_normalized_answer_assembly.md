# Normalized answer assembly

## Legal (`format_legal_lookup_answer`)

1. Header: ASBP handbook disclaimer (not legal advice).
2. Optional banner when normalized units exist: structured fields are **heuristic**, not replacements for excerpts.
3. For each evidence item (citation-first):
   - Citation, family, heading, subsection path, pages, **excerpt/snippet**.
   - If `units_by_chunk_id[chunk_id]` exists: append up to **two** normalized blocks with type, requirement level, role, action, summary, condition/exception/escalation (truncated), confidence/review.
4. Footer: verify against official compilation.

## Policy (`format_policy_lookup_answer`)

1. Internal policy disclaimer.
2. Same heuristic banner when normalized segments exist.
3. Per segment: heading, anchor, excerpt, then up to two normalized blocks.
4. Footer: confirm with policy owner.

## Truth packet

- `packet_meta` records counts: `legal_normalized_unit_groups`, `policy_normalized_unit_groups`.
- `allowed_claims` still reference raw evidence ids (chunk / segment).
