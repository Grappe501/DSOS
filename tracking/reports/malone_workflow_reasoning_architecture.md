# Workflow reasoning architecture

## Step ordering

1. Prefer normalized units whose `normalized_unit_type` is workflow-like (`workflow_step`, `procedure_step`, `sop_step`, etc.).
2. If `structured_facets` / `structured_facets_json` exposes `step_order`, `ordinal`, `sequence`, or `order`, use it.
3. Fallback: light heuristic from title digits; stable tie-break by unit id.
4. If **no** workflow-typed units: synthesize up to eight short steps from requirement-like units with summaries — always marked **partial** with reason `no_explicit_workflow_steps_in_units`.

## Partial workflows

- `partial_workflow` true when: non-workflow units coexist with workflow units, fewer than two workflow units, or synthesis path used.
- Answer layer prints explicit partial reason when present.

## Source linkage

- Each step references `unit_id`; `source_evidence_map` maps to chunk or segment anchors for audit.
