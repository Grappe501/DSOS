# SOP extraction architecture

## Inputs

- **Unit text:** `title` + `plain_language_summary` (`combined_unit_text`).
- **No synthetic content:** Extractors return empty lists when patterns do not match.

## Modules

| Module | Role |
|--------|------|
| `sop_parser` | Line splitting, whitespace normalization |
| `step_extractor` | Numbered `1.` / `1)` lines; bullet lists |
| `prerequisite_extractor` | Block after `Prerequisites:` / `Before you begin` |
| `checkpoint_extractor` | Verify / confirm / checkpoint verbs |
| `stop_condition_extractor` | Stop if / do not proceed / halt |
| `escalation_trigger_extractor` | Escalate / notify / compliance handoff |
| `role_owner_extractor` | Pharmacist, technician, PIC, nurse, compliance |
| `branch_extractor` | If / unless / when sentences |
| `serialization` | JSON-safe round-trip |

## Output shape

`extract_workflow_fields_from_text` returns a single dict with nested lists and `extraction_confidence`.
