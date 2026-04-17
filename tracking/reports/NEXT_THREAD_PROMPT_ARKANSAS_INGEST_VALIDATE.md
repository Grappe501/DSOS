# Next thread: Arkansas handbook one-command ingest + validate

## What exists

- Runner: `tracking/scripts/run_arkansas_handbook_ingest_validate.py`
- Status helpers: `app/services/legal_ingestion/ingest_validate_status.py` (`decide_overall_status`, `retrieval_is_broad_failure`)
- Reports (each run overwrites): `tracking/reports/arkansas_handbook_ingest_validate_report.md`, `arkansas_handbook_ingest_validate_state.json`, plus optional `arkansas_handbook_ingest_validate_details.json`, `arkansas_handbook_db_counts.json`, `arkansas_handbook_retrieval_checks.json`

## Command

```bash
python tracking/scripts/run_arkansas_handbook_ingest_validate.py --pdf "C:\path\to\November-2025-Lawbook.pdf"
```

Optional: `--stable-key CUSTOM_KEY` if the default document key already exists; `--no-ingest` for family-map + precheck only.

## Integration points (do not fork)

- Family map: `family_map_validation_report_payload` / `parse_family_spans` (`app/services/legal_ingestion/toc_parser.py`)
- Ingest: `ingest_arkansas_handbook_pdf` (`app/services/legal_ingestion/arkansas_pipeline.py`)
- Retrieval: `find_chunks_by_citation_text`, `search_legal_chunks_lexical` (`app/services/legal_retrieval/`)

## Likely follow-ups

- Wire CI to run against a pinned PDF artifact (path secret / cache) if policy allows.
- If duplicate `stable_key` blocks re-runs, document a safe “replace version” admin path without deleting unrelated rows.
