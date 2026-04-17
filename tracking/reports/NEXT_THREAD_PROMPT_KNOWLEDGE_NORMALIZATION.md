# Next thread: knowledge normalization — follow-ups

## Done in v0

- DB tables + ORM for runs, units, review events.
- Deterministic **legal** and **policy** normalizers + runner + CLI.
- PASS / PASS_WITH_WARNINGS / FAIL validation and default `system_generated` review state.

## Recommended next steps

1. **API surface** (in `app/` only): list/query normalized units by `legal_source_version_id` or `ingestion_source_version_id`, filter by `review_state` and `normalized_unit_type`.
2. **Review workflow**: service methods to append `NormalizedKnowledgeReviewEvent` and transition `review_state` with actor + reason.
3. **Legal path QA**: run `tools/run_knowledge_normalization.py --legal-source-version-id <uuid>` against a real ingested Arkansas version; spot-check labels vs. raw chunks.
4. **Malone integration**: optional retrieval that prefers `review_state=approved` units for tooltips or guardrails (without removing citation-backed answers).
5. **SOP profile**: map numbered steps to `workflow_step` with parent/child in `structured_facets_json`.

## CLI reference

```bash
python tools/run_knowledge_normalization.py --legal-source-version-id <UUID>
```

```bash
python tools/run_knowledge_normalization.py \
  --ingestion-source-version-id <UUID> \
  --ingestion-source-id <UUID> \
  --source-type policy_manual
```

## Migrations

```bash
alembic upgrade head
```
