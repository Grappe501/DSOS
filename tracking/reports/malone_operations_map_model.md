# Operations Map — Data Model

## Core

- **operations_departments** — `stable_key`, `name`, `description`, `meta_json`.
- **department_intake_sessions** — FK to department, actor user, status (`open`/`closed`), optional `proposal_id`, `scenario_memory_id`, `state_json`, `meta_json`.
- **department_intake_answers** — FK session, optional `question_key`, `answer_text`, `entry_mode`, `transcript_ref`, `parser_output_json`.

## Map entities (materialized)

- **operations_roles** — `title`, `description`.
- **operations_workflows** — `name`, `inputs_summary`/`outputs_summary` (first workflow may inherit I/O from profile), `ordinal`, optional `owner_role_id`.
- **operations_system_tools** — `name`, optional FK to workflow.
- **operations_dependencies** — `from_ref`, `to_ref`, `dependency_type`.
- **operations_handoffs** — `to_counterparty`, optional workflow FK.
- **operations_escalations** — `trigger_summary`, `path_summary`.
- **operations_blockers** — `description`.
- **operations_artifact_refs** — SOP/policy **labels** only (no blob storage here).
