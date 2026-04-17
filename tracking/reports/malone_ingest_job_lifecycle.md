# Ingest job lifecycle

## Entities

- **`ingestion_jobs`** — Business-layer job: ties `ingestion_source_id`, optional `ingestion_source_version_id`, `parser_profile_key`, `status`, `stage`, `overall_validation_status`, optional `linked_legal_ingestion_job_id`, `counts_json`, timestamps.
- **`ingestion_job_events`** — Append-only audit trail (`event_type`, `payload_json`).

## Typical flow

1. **Create** — Job inserted with `status=running`, `stage=start`, `started_at` set; event `job_created`.
2. **Execute** — Profile-specific work (Arkansas pipeline commits its own `legal_ingestion_jobs` row; runner links via `linked_legal_ingestion_job_id` on success).
3. **Complete or fail** — `status` → `completed` or `failed`; `finished_at` set; event `job_completed` or `job_failed`.
4. **Validate** — `ingestion_validations` row written; `overall_validation_status` on the job mirrors validation outcome string.
5. **Promote (optional)** — See promotion plan; may update version/source status.

## Status strings (business job)

Suggested values: `pending`, `running`, `completed`, `failed`, `cancelled` (cancelled reserved for future use).

## Relationship to legal jobs

`legal_handbook` profile: business job is the **control-plane envelope**; `legal_ingestion_jobs` remains the **handbook pipeline** record. Both IDs appear in reports and JSON exports for traceability.

## Reporting

CLI `tools/run_business_ingest.py` writes `tracking/reports/business_ingest_last_run.json` with args + result payload for operators.
