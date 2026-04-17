# Next Thread — Family Map Hardening (Post-Pass)

You are continuing DSOS / Malone after the **family map hardening pass** (2026-04-16).

## Completed

- `family_boundary.py` — statute anchor, TOC line-shape vs body headings, reconciliation + title validation phrases.
- `toc_parser.py` — `FamilySpan` provenance/confidence, reconciled path, improved legacy body-slice start.
- `source_profiler.py` — `estimate_handbook_zones`.
- `arkansas_pipeline.py` — `meta_json.family_map`, version `handbook_zones`.
- `source_families.py` — confidence helpers for retrieval.
- `legal_retrieval/lexical.py` + `citation_lookup.py` + `retrieval/lexical.py` — family filters and confidence guardrails.
- Tests: `tests/test_family_boundary.py`; script: `tracking/scripts/family_map_validate.py`.
- Tracking: main report, state JSON, contracts, validation note, retrieval plan, this prompt.

## Active lanes

`app/`, `schemas/`, `alembic/`, `tracking/`, `tests/` — do **not** edit `backend/`, `frontend/`, `dsos_replacements/`.

## Suggested next pass

1. Run `tracking/scripts/family_map_validate.py --pdf` on the real November 2025 Arkansas PDF; tune TOC dot-leader regex or title length floors if needed.
2. Optional: add `span_confidence` column if JSON filtering becomes a bottleneck.
3. Thread family filters into evidence bundle / hybrid retrieval when truth-packet wiring is ready.
4. Keep embeddings and public legal Q&A out of scope until evidence fidelity gates are satisfied.

## Read first

- `tracking/reports/malone_family_map_hardening_report.md`
- `app/services/legal_ingestion/family_boundary.py`
- `app/services/legal_ingestion/toc_parser.py`

## Hard-fail conditions

No passive-root edits, no wholesale Malone replacement, no speculative user-facing legal Q&A before evidence paths are stable, no skipping tracking updates for the slice you ship.
