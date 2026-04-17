# Next thread — Business ingestion architecture follow-on

You are continuing **DSOS / Malone** after the **business-wide ingestion control plane** pass (Alembic 0005, `app/services/ingestion_control/`, `tools/run_business_ingest.py`).

## Locked invariants

- **Active lane:** `app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/`.
- **Do not modify:** `backend/`, `frontend/`, `dsos_replacements/` unless a separate thread authorizes it.
- **Legal handbook pipeline** remains authoritative for lawbook rows; business layer **links** via `ingestion_source_versions.legal_*` FKs when `parser_profile_key=legal_handbook`.

## Read first

- `tracking/reports/malone_business_ingestion_architecture_report.md`
- `tracking/reports/malone_business_ingestion_architecture_state.json`
- `app/services/ingestion_control/ingest_runner.py`
- `schemas/business_ingestion_control_v0.sql`

## Suggested next work (pick one stream)

1. **Retrieval QA for segments** — Add optional lexical probes for `ingestion_segments` (scoped by `ingestion_source_version_id`) and fold into `ValidationPayload.retrieval`.
2. **Dedicated SOP parser** — Replace shared heading splitter with step/role extraction; extend validation checklist.
3. **Admin API** — Thin FastAPI routes to list sources/versions/jobs (read-only first) without UI scope creep.
4. **Embedding index** — Only if product priority confirms; keep feature-flagged and separate from control-plane tables.

## Verification commands

```bash
python -m pytest tests -q
python -m compileall app tracking/scripts tools -q
alembic upgrade head
npm run build
```

## Do not regress

- Arkansas `ingest_arkansas_handbook_pdf` behavior and existing legal tables.
- Malone answer loop remains independent of raw ingestion orchestration.
