# Legal–policy–SOP cross-source reasoning

## Goal

Combine normalized units from **multiple** bundles in one `decision_workflow` block when evidence exists, without a second Malone entrypoint.

## Mechanism

- **Env**: `MALONE_CROSS_SOURCE_DECISION_ENABLED` (default off).
- **Trigger**: `cross_source_legal_policy_triggered(message)` — both legal and policy cues in the message, or explicit `[cross-source]`.
- **Bundles**: `handle_malone_request` may load `legal_bundle` and `policy_bundle` together when cross-source triggers, even if primary intent classification is `legal_handbook` (legal still wins for deterministic delivery unless policy/SOP targets apply).
- **SOP hint**: when cross-source is on, `[sop]` or `runbook` in the message additionally loads `sop_bundle`.

## Merge semantics

- `merge_units` concatenates legal, policy, and SOP normalized groups; `sources_present` lists distinct `source_type` values.
- Ranking within `build_decision_workflow_block` prefers higher `review_state` and `confidence_level` before assembly.

## Future

- Explicit UI or intent for “compare legal vs policy” without keyword overlap.
- Weighted blending when units conflict (currently: display union with ordering, no automated conflict resolution).
