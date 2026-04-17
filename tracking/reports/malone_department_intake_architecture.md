# Department Intake — Architecture

## Layers

1. **Session lifecycle** — `start_intake_session` creates `OperationsDepartment`, `MaloneProposal`, `MaloneScenarioMemory`, `MaloneDecisionTrace` (stub), and `DepartmentIntakeSession` with default `state_json`.
2. **Answers** — Append-only `DepartmentIntakeAnswer` rows; `state_json.profile` merged from `parse_intake_answer` patches.
3. **Follow-ups** — Derived on read from `compute_followup_questions(state)` (no hidden state).
4. **Materialize** — `materialize_operations_map` deletes prior child rows for the department and rebuilds from profile (explicit tradeoff for clarity).

## Same Malone path

All HTTP calls use existing JWT + `/api/malone` prefix family; chat router is unchanged. Intake does not register a second WebSocket or agent runtime.
