# Internal company knowledge — ingestion pack

- **`internal_company_knowledge_manifest.json`** — aggregate manifest produced by `python tools/run_internal_company_ingest.py` (dry-run or ingest). Re-run after adding files under `tracking/data/internal_company_knowledge/`.

Each entry includes `proposed_stable_key`, paths, `source_type`, `parser_profile`, governance fields (`review_recommendation`, `ingestion_priority`, `active_candidate`), and optional `normalization_profile_hint` for policy/SOP paths.
