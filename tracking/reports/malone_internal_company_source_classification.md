# Internal source classification (deterministic)

## Folder → control plane

| Folder | source_type | parser_profile |
|--------|----------------|----------------|
| policy_manual | policy_manual | policy_manual |
| sop_workflow | sop_workflow | sop_workflow |
| training_module | training_module | training_module |
| form_template | form_template | general_reference |
| reference_sheet | general_reference | general_reference |
| billing_reference | contract_rules | contract_rules |
| meeting_memory | meeting_memory | meeting_memory |
| compliance_notice | policy_manual | policy_manual |
| vendor_or_product_reference | general_reference | general_reference |
| company_profile | general_reference | general_reference |

## Unknown folder

Falls back to `general_reference` / `general_reference` with `classification_reason=unknown_folder_default_*`.

## Signals

- **Folder** (primary).
- **Extension** (PDF/office → inactive).
- **Snippet** (optional keywords: “policy”, “sop”, “runbook”) appended to `notes` only—does not override folder mapping.
