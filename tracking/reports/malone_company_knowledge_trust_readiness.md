# Trust / Readiness — Company Knowledge

## Signals

- **Review head** — Latest outcome and state on `malone_review_artifact_heads`.
- **Promotion signal** — `ingestion_source_version_promotion_signal`: combines DB `retrieval_ready`, head state (`approved` vs `validated` staging), and a short `promotion_hint`.
- **Normalized units** — `review_state` + `confidence_level`; `review_rank` prefers approved/reviewed over draft for augmentation tie-breaks.

## What promotion does *not* do

- It does not change citation text, legal chunk selection rules, or handbook determinism.
- It does not inject “approved prose” as a replacement for retrieved segments.

## Operating / trace artifacts

Existing artifact types (`scenario_memory`, `decision_trace`, `operating_copilot_snapshot`) continue to use scenario audit mapping; new outcomes map to reviewed / under_review where applicable.
