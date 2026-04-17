# Role and escalation reasoning

## Roles

- Derived only from `applies_to_role` on normalized units (no LLM-inferred job titles).
- Output: list of `{ "role": str, "unit_ids": [...] }` for traceability.

## Escalation and reporting

- **Escalation**: strings from `escalation_text`.
- **Reporting / outcomes**: strings from `output_outcome_text` labeled as `reporting_or_outcome`.
- De-duplicated by `(kind, text)` to reduce noise when multiple units repeat guidance.

## Operational intent

- `decision_router.classify_operational_intent` emphasizes escalation-focused phrasing when user message contains supervisor/notify/escalation cues — affects labeling only, not retrieval.
