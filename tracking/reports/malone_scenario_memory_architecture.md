# Scenario memory architecture

## Tables

- **`malone_scenario_memories`**: Prompt (truncated), fingerprint, scenario type label, intent target, JSON lists of source types and version snapshots, memory/review status, delivery metadata, `meta_json` for route payload.
- **`malone_decision_traces`**: Foreign key to scenario memory (unique); JSON payloads for workflow, evidence map, patterns, fallbacks, snapshots.

## Lifecycle

1. Malone builds evidence bundles and decision/workflow as today.
2. Optionally, **prior analogs** attach to the truth packet (`attach_prior_scenario_context`).
3. Delivery runs; answer pattern metadata is written onto `truth_packet`.
4. **`persist_scenario_memory_and_trace`** inserts scenario + trace and **`db.commit()`** so rows survive after `update_proposal_record`’s commit.

## Eligibility

Persistence runs when `MALONE_SCENARIO_MEMORY_ENABLED` (default: follows decision-reasoning enablement) and the interaction is a handbook/policy/SOP path or has at least one evidence item in any bundle; not for `approval_required` delivery.
