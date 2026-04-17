# Internal company knowledge intake (deterministic layout)

Place internal documents under the subfolders below. The intake runner (`tools/run_internal_company_ingest.py`) maps each **first-level folder** to a `source_type` and parser profile in the business ingestion control plane.

**Preferred formats:** `.md`, `.txt` (UTF-8). PDF/DOCX are skipped for generic text ingest until converted.

Default folder names:

- `policy_manual/` — policies and handbooks  
- `sop_workflow/` — procedures and runbooks  
- `training_module/` — training outlines  
- `form_template/` — form instructions (ingested as structured text)  
- `reference_sheet/` — quick reference  
- `billing_reference/` — payer/billing notes  
- `meeting_memory/` — decision logs  
- `compliance_notice/` — notices (policy-style ingest)  
- `vendor_or_product_reference/` — vendor notes  
- `company_profile/` — background / org context  

Unknown folders default to `general_reference` with a warning.
