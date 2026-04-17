# Workflow assembly upgrade

## Pipeline

1. `assemble_ordered_steps` (existing) produces base `action_steps`.
2. `enrich_action_steps_with_extraction` attaches `workflow_extraction` per `unit_id`.
3. `merge_step_ownership` fills `applies_to_role` when only text hints exist.
4. `augment_decision_plan_with_assembly` adds merged views + assessment.

## New decision_workflow keys

- `workflow_checkpoint_view` — flattened checkpoints / stops / escalation triggers from extraction.
- `workflow_branch_hints` — conditional sentence list.
- `workflow_escalation_lines_merged` — normalized escalations + text signals, deduped by prefix.
- `workflow_extraction_assessment` — sparse-signal detection for guardrails.
