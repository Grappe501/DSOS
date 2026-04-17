# Scenario memory safety / precedence

## Rules (implemented)

1. **Current evidence outranks memory** — `current_evidence_outranks_memory()` is always true; documentation + truth-packet `precedence` string.
2. **Priors are review-only** — `prior_analogs` entries include `review_only: true`.
3. **Drift** — Version mismatch flags reduce trust in analogy (warning only).
4. **Weak matches** — High `min_similarity` thresholds can yield zero priors; comparison sets `weak_match_warning`.
5. **Forbidden claims** — When priors attach, extra guardrails block treating memory as governing law.

## Environment

- `MALONE_SCENARIO_MEMORY_ENABLED` — master toggle (inherits decision reasoning when unset).
- `MALONE_SCENARIO_MEMORY_PRIORS_ENABLED` — load priors into truth packet (inherits memory when unset).
- `MALONE_SCENARIO_MEMORY_APPEND` — optional future formatter appendix (default off).
