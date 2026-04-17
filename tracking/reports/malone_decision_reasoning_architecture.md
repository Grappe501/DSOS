# Decision reasoning architecture (Malone augmentation)

## Position in the stack

1. **Evidence** — Legal chunks / policy or SOP segments (raw text) as today.
2. **Normalized attachment** — `normalized` on each bundle (`units_by_chunk_id` / `units_by_segment_id`).
3. **Decision merge** — `merge_units` flattens tuples `(unit_dict, lane, evidence_item)` across bundles.
4. **Action plan** — Roles, grouped conditions/exceptions/escalations, ordered steps, `source_evidence_map` keyed by `normalized_unit_id`.
5. **Truth packet** — `decision_workflow` JSON-safe block + `packet_meta` keys.
6. **Answer** — Citation/segment body first; optional operational appendix from `should_emit_structured_sections`.

## Modules

| Module | Role |
|--------|------|
| `context_builder.py` | Merge units from legal/policy/SOP bundles with lane + evidence pointers |
| `decision_router.py` | Keyword operational intent (`step_by_step`, `escalation_focus`, `lookup`) |
| `workflow_assembler.py` | Order workflow-typed units; partial/synthesized paths when needed |
| `role_mapper.py` | Distinct roles with unit ids |
| `condition_evaluator.py` / `exception_resolver.py` / `escalation_resolver.py` | Group text with provenance |
| `action_plan_builder.py` | Compose plan + anchors |
| `fallback.py` | Env gates, trust aggregation, emit gating |
| `serialization.py` | JSON round-trip + anchor helper |

## Non-goals

- No separate workflow engine process or queue.
- No replacement of raw excerpts by summaries.
