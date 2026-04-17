# Normalized retrieval architecture (Malone augmentation)

## Flow

1. **Intent** → `legal_handbook` or `policy_manual` (opt-in via env + message triggers).
2. **Evidence** → `build_legal_evidence_bundle` / `build_policy_evidence_bundle` loads **raw** chunks or segments first.
3. **Normalization** → `attach_normalized_to_legal_bundle` or policy builder queries `normalized_knowledge_units` joined to `normalization_runs` with `PASS` / `PASS_WITH_WARNINGS` only.
4. **Truth packet** → `legal_evidence` / `policy_evidence` include a `normalized` sub-object with serialized units keyed by `legal_unit_chunk_id` or `ingestion_segment_id`.
5. **Answer** → `format_legal_lookup_answer` / `format_policy_lookup_answer` print **citations or excerpts first**, then optional structured normalized lines.

## Non-goals

- No second HTTP API or second Malone entrypoint.
- No replacement of chunk/segment text with summaries only.

## Modules

| Module | Role |
|--------|------|
| `legal_selector.py` | Query units by chunk ids + legal source version |
| `policy_selector.py` | Segment search + units by segment ids |
| `bundle_builder.py` | Attach `normalized` dict to evidence bundles |
| `ranking.py` | Order units by review + confidence |
| `fallback.py` | Block rejected/superseded; caveat flags |
| `serialization.py` | ORM → JSON-safe dict |
