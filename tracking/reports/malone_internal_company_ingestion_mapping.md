# Ingestion mapping (internal → existing pipelines)

- **Registry** — `get_or_create_source` with `stable_key`, `source_type`, `business_domain`, `authority_tier`.
- **Jobs** — `ingest_jobs.create_job` as today.
- **Execution** — `ingest_generic_text_profile` for all non-legal profiles in this pass (policy, SOP, training, contract, meeting, general, form_template uses general executor).
- **Legal handbook** — not used by internal company runner (no PDF lawbook path in default intake).
- **Normalization** — after successful ingest for `policy_manual` and `sop_workflow`, `run_normalization` with `PROFILE_POLICY_MANUAL_NORM` (segment-based policy normalizer); persisted units use existing review defaults (`system_generated`).
- **Workflow extraction** — not auto-invoked; SOP content is ingested as segments for future `workflow_extraction` hooks.
