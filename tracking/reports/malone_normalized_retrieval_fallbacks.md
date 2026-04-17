# Normalized retrieval — fallbacks and safety

## When normalized attachment is skipped

| Condition | Behavior |
|-----------|----------|
| `MALONE_NORMALIZED_RETRIEVAL_ENABLED` off (or explicitly false) | `bundle["normalized"]` records disabled reason; raw-only answer. |
| No `legal_source_version_id` / no chunk ids | `fallback_reason: missing_scope` |
| No DB rows for chunks/segments | `fallback_reason: no_matching_normalized_units` |
| Normalization run was `FAIL` | Units excluded by join (not returned) |

## Row-level exclusion

- `review_state == rejected` → not surfaced.
- `superseded == true` → not surfaced.

## Caveats (still shown, flagged)

- `confidence_level == unknown` or `review_state == draft` → unit may appear with `caveat` and a line telling the user to verify against excerpt.

## Answer path

- **Never** removes citation lines or excerpts when normalized data exists.
- If normalized is absent, formatting matches pre-upgrade behavior (plus optional disclaimer only when `normalized.enabled` was true but empty groups).

## Web search

- `policy_manual` and `legal_handbook` both disable external web search in the truth packet (internal evidence only).
