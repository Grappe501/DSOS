# Next thread — internal company knowledge ingest (follow-on)

## Completed

- Deterministic intake tree, classification, batch orchestration, CLI, manifests, tests, tracking reports.
- Normalization hook for policy + SOP paths via existing `policy_manual_v1` profile.

## Recommended next steps

1. **PDF/DOCX path** — optional pluggable text extraction → temp `.md` then ingest (still through control plane).
2. **Form template profile** — dedicated parser profile if forms need field schemas beyond general reference.
3. **Workflow extraction** — selective `workflow_extraction` pass on `sop_workflow` versions after validation PASS.
4. **CI job** — run `python tools/run_internal_company_ingest.py --dry-run` on PRs touching `tracking/data/internal_company_knowledge/`.

## Constraints

- Keep a **single** ingestion control plane and Malone path.
- No silent injection into scenario memory or chat without registered sources.

## Active lane

`app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/` only.
