# Department Follow-Up Questioning Strategy

## Principles

- **Deterministic**: Same profile state yields the same follow-up list (sorted by priority + target field).
- **Inspectable**: Each item includes `reason`, `target_field`, `question_text`, `priority`.
- **No LLM loop**: Rules live in `followup_generator.py` and `intake_questionnaire.py`.

## Example triggers

| Gap | Reason code | Typical question |
|-----|-------------|------------------|
| Empty mission | `mission_missing` | Primary purpose? |
| No roles | `owner_unknown` | Who owns which responsibilities? |
| No workflows | `workflow_gap` | Major recurring processes? |
| No systems | `no_system_named` | Which tools support workflows? |
| Missing I/O | `io_undefined` | Key inputs and outputs? |
| No dependency info | `dependency_unknown` | Who depends on whom? |
| No handoffs | `no_handoff` | Handoffs to other teams? |
| No escalation | `no_escalation` | When and how to escalate? |
| No blockers | `no_blocker_named` | Common blockers? |
| No SOP names | `no_sop_named` | Written SOP/policy names? |
