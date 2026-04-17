# Operating copilot architecture (single Malone path)

## Placement

The business operating copilot runs **after** retrieval-backed bundles are built and **after** `build_decision_workflow_block`. It consumes the same `legal_bundle`, `policy_bundle`, `sop_bundle`, and `decision_workflow` dict that the rest of Malone already uses.

## Data flow

1. **Evidence scope** (`evidence_scope_summary`): counts items per source type and sets `cross_source` when more than one type has items.
2. **Merge** (`merge_units`): normalized units from all lanes (same as decision reasoning).
3. **Scenario route** (`route_scenario`): primary scenario + scores + reasons.
4. **Uncertainty** (`assess_uncertainty`): merged unit count, partial workflow, trust, source-type breadth.
5. **Guidance assembly**: next steps, roles, conditions, exceptions, escalations, summary bullets, distinction object, supporting source mix.
6. **Serialization**: JSON-safe copy via `serialize_copilot_block`.
7. **Truth packet**: `enrich_truth_packet_with_operating_copilot` stores `operating_copilot` and meta; may extend `forbidden_claims`.

## Rendering

- Smart-pattern paths: `render_*_smart_answer` → `_append_decision` → `_append_copilot`.
- Legacy paths without message: `format_*_lookup_answer` appends copilot when `truth_packet` is passed.

## Environment

- `MALONE_OPERATING_COPILOT_ENABLED`: explicit on/off; when unset, defaults to `malone_decision_reasoning_enabled()`.
