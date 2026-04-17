# Malone knowledge normalization — architecture

## Position in the stack

```
ingestion_sources / legal_documents
        ↓
ingestion_source_versions / legal_source_versions  (+ parser_profile_key)
        ↓
ingestion_segments | legal_units / legal_unit_chunks / legal_citations   ← evidence / raw structure
        ↓
normalization_runs  (profile + validation snapshot)
        ↓
normalized_knowledge_units  (+ optional normalized_knowledge_review_events)
```

Normalization **never replaces** chunks or segments; it **references** them via nullable FKs and JSON anchors.

## Components

| Piece | Role |
|-------|------|
| `NormalizationRun` | One execution of a profile against a resolved version; stores PASS / PASS_WITH_WARNINGS / FAIL + JSON failures/warnings. |
| `NormalizedKnowledgeUnit` | One structured knowledge atom: type, roles, requirement level, conditions/exceptions, confidence, review_state, retrieval fields, source text copy. |
| `NormalizedKnowledgeReviewEvent` | Append-only audit when review_state changes (governance). |
| Services | `legal_normalizer` (handbook), `policy_normalizer` (manual), `normalization_runner` (persist + validate), `normalization_validation` (status rules). |

## Determinism

- Classification uses **keyword / regex** rules only (`field_extractors.py`).
- Confidence is **rule-count–based** (`confidence.py`), not ML.
- Unknown fields remain **null**; `confidence_level` may be `unknown`.

## Extension

- Add a profile in `normalizer_registry.py` + a builder module + branch in `normalization_runner.run_normalization`.
- Scaffold source types (`sop_workflow`, …) reuse patterns from policy or legal with different extractors.
