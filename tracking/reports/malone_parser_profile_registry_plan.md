# Parser profile registry plan

## Purpose

Parser profiles describe **how** a source class is structured, chunked, enriched, anchored, and validated. They are **code-first** (`parser_profiles.PARSER_PROFILES`) so rules stay reviewable in Git and do not require DB migrations for every tweak.

## Profile record shape

Each `ParserProfile` includes:

- `key` — stable identifier used on `ingestion_source_versions.parser_profile_key` and `ingestion_jobs.parser_profile_key`.
- `default_source_type` — suggested `ingestion_sources.source_type`.
- Narrative fields: structure, chunking, metadata, citation/anchor, validation expectations.
- `extra` — optional map (e.g. executor module hint).

## Implemented vs scaffolded

| Profile key | Execution in this pass |
| --- | --- |
| `legal_handbook` | **Yes** — calls `ingest_arkansas_handbook_pdf`; persists legal rows; business version links via FKs. |
| `policy_manual` | **Yes** — heading-based `ingestion_segments` + checksum validation. |
| `sop_workflow`, `training_module`, `contract_rules`, `meeting_memory`, `general_reference` | **Scaffold** — same segment writer as policy until specialized parsers land; profile text documents intent. |

## Extension process

1. Add or extend a `ParserProfile` in `parser_profiles.py`.
2. If new execution path is needed, branch in `ingest_runner.run_business_ingest` (or a dedicated submodule) without forking the legal pipeline.
3. Add validation rules in `validation.py` and wire from runner.
4. Add tests under `tests/` for deterministic behavior.

## Relationship to Arkansas QA

Lawbook-specific TOC/family validation remains in `run_arkansas_handbook_ingest_validate.py`. Business jobs use `ingestion_validations` for PASS / PASS_WITH_WARNINGS / FAIL at the control-plane layer.
