# Human feedback schema and governance

## Outcomes

| Outcome | Typical use |
|---------|-------------|
| `approved` | Trust for augmentation / promotion hints |
| `rejected` | Block normalized augmentation where applicable; keep audit row |
| `needs_revision` | Request rework; surfaces caveats |
| `informational` | Acknowledgement without blocking |
| `risk_flag` | Escalate visibility (`under_review`) |

## Event fields

- `review_state_before` / `review_state_after` — string snapshots for diffing.
- `trust_level` — optional `high` / `medium` / `low` (may map to normalized `confidence_level`).
- `notes` — free text (length-capped in sync).
- `meta_json` — structured extras (e.g. website pack priority); **must not** include `source_text` rewrites (`safety.assert_no_source_text_mutation_fields`).

## Reviewer

`reviewer_user_id` references `users.id` for accountability.
