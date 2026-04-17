# Malone Family Map Hardening Pass — Report

**Pass date:** 2026-04-16  
**Scope:** Deterministic family-map extraction, reconciliation, persistence metadata, and safer family-aware retrieval hooks for the Arkansas State Board of Pharmacy “Statutes and Rules” compilation (November 2025 target).  
**Active lanes:** `app/`, `schemas/`, `alembic/`, `tracking/`, `tests/` only.

---

## 1. WHAT THIS PASS IMPLEMENTED

### Concrete family-map improvements

- **`family_boundary.py`:** Statute-line anchor, TOC-vs-body classification using **line shape** (dot-leaders / page tail vs plain major headings), per-code reconciliation, and validation helpers against the expected A–H title phrases.
- **`toc_parser.py`:** `FamilySpan` now carries `span_provenance`, `span_confidence`, optional `toc_char_start` / `body_anchor_char`, and `reconciliation_notes`. Primary path runs full-corpus reconciliation; **legacy body-slice fallback** uses `min(first statute line, earliest resolved family hit)` so headings that appear **before** the first statute line stay inside the slice (fixes single-family collapse on short fixtures).
- **`source_profiler.py`:** `estimate_handbook_zones()` returns `body_start_char` and optional `body_start_page` for ingest metadata.
- **`arkansas_pipeline.py`:** Persists `parser: arkansas_family_map_v2` and structured `family_map` in `legal_document_families.meta_json`; attaches `handbook_zones` to `LegalSourceVersion.meta`; passes `page_map` into `parse_family_spans`.
- **`source_families.py`:** `parse_family_map_meta`, `family_meets_min_span_confidence` for retrieval guards.
- **`legal_retrieval/lexical.py`:** Optional `family_code`, `min_family_span_confidence`, and `family_span_confidence` on hit dicts; over-fetch when confidence filter is set.
- **`citation_lookup.py`:** Optional `family_code` on `find_chunks_by_family_and_phrase`.
- **`retrieval/lexical.py`:** `search_handbook_lexical` forwards family filters to `search_legal_chunks_lexical`.
- **Tests:** `tests/test_family_boundary.py` (TOC/body zones, reconciliation, eight-family merge, provenance).
- **Script:** `tracking/scripts/family_map_validate.py` (fixture or PDF → JSON summary).

### What remained unchanged

- PDF extraction, `PageMap`, anchor enrichment, chunk page grounding, `legal_source_version_id` scoping column, and Alembic history (no new migration; family metadata lives in existing `meta_json`).
- Malone chat routes, `truth_packet_service`, embeddings, and passive roots (`backend/`, `frontend/`, `dsos_replacements/`).

---

## 2. HOW FAMILY DETECTION NOW WORKS

### TOC extraction

- Lines matching `^[A-H][.)]\s+…` with minimum title length are collected **across the full text**.
- Before the first statute cite line, a hit is classified as **TOC** if the line matches TOC shape (dot leaders + trailing page digits, or “Table of Contents” phrasing); otherwise it is **body** (e.g. a real major heading on an early page without leaders).

### Body confirmation

- After the first statute cite line, hits are **body** zone.
- Per code `A`–`H`, the reconciler prefers a **body** hit; if only a TOC hit exists for a code, that code is still emitted with lower confidence (`toc_only`).

### Reconciliation

- Transparent rules (see `tracking/reports/legal_family_reconciliation_contract.md`):
  - Prefer **body** anchor over **TOC** anchor when both exist for the same letter.
  - If four or more families resolve via reconciliation, spans are merged from reconciled hits; otherwise **legacy body-slice** parsing applies with an adjusted slice start (see above).
  - If still empty, legacy whole-corpus heuristic runs as last resort.

### Confidence / provenance rules

- **`toc_confirmed_by_body`:** Body hit and TOC hit both present for the code (high or medium confidence depending on relative positions).
- **`body_only`:** Body hit, no TOC listing for that code.
- **`toc_only`:** TOC hit only (low confidence).
- **`legacy_*`:** Fallback parsers (explicitly lower trust).

---

## 3. HOW THE ARKANSAS LAW BOOK FAMILY MAP NOW LOOKS

### Expected families (visible TOC / front-matter target)

| Code | Short label (target structure) |
|------|--------------------------------|
| A | Pharmacy Practice Act |
| B | Miscellaneous Statutes Related to Pharmacy |
| C | Uniform Controlled Substances Act |
| D | Insurance Policies – Prescription Drug Benefits |
| E | Food, Drug, and Cosmetic Act |
| F | Controlled Substances and Legend Drugs |
| G | Administrative Procedure Act |
| H | Rules Pertaining to Arkansas Prescription Drug Monitoring Program |

### Detected families (fixture)

On `tracking/fixtures/arkansas_handbook_vertical_slice_sample.txt`, the pipeline detects **A** and **H** only (fixture is an excerpt, not the full compilation). Run `python tracking/scripts/family_map_validate.py --fixture …` or `--pdf …` for machine-readable output.

### Page spans

- When PDF grounding is active, `toc_page_start` / `toc_page_end` on `legal_document_families` remain derived from `FamilySpan` char ranges via `PageMap` (unchanged contract).

### Confidence notes

- Full eight-family fidelity on the **real** November 2025 PDF requires running the validate script locally and comparing to the expected table; title phrase checks are implemented in `validate_against_expected_titles`.

---

## 4. RETRIEVAL SAFETY IMPACT

- Callers can scope lexical search by **`family_code`** and optionally require **`min_family_span_confidence`** so low-confidence `toc_only` bands are not treated like verified body bands.
- Hits include **`family_span_confidence`** when family `meta_json` carries `family_map.span_confidence`.
- **Still guarded:** omitting `legal_source_version_id` retains legacy cross-version visibility; confidence does not imply legal correctness.

---

## 5. MALONE INTEGRATION BOUNDARY

- Not wired: Malone user-facing loop, truth-packet assembly, intent routing, or uploads UI.
- Ingest continues to run from admin/batch paths; evidence rows remain the same tables with richer family metadata.

---

## 6. IMPLEMENTATION GAPS

- **Next pass:** Run `family_map_validate.py` on the production PDF path used in ops; tune TOC line-shape rules if the extract layout adds noise; optional Alembic column for `span_confidence` if JSON filtering proves insufficient at scale.
- **Optional:** Thread `family_code` / confidence into `retrieve_legal_evidence_bundle` and hybrid retrieval once evidence paths consume them.

---

## 7. HARD-FAIL COMPLIANCE CHECK

| Condition | Status |
|-----------|--------|
| Passive roots modified (`backend/`, `frontend/`, `dsos_replacements/`) | **No** |
| Wholesale Malone replacement | **No** |
| Code without integration purpose | **No** (boundary + parser + ingest + retrieval + tests) |
| Versioning / citation / page-grounding direction weakened | **No** |
| Required tracking outputs skipped | **No** |
| Speculative user-facing legal Q&A | **No** |

---

## Artifacts

- State: `tracking/reports/malone_family_map_hardening_state.json`
- Contracts: `legal_family_extraction_contract.md`, `legal_family_reconciliation_contract.md`
- Validation: `arkansas_lawbook_family_validation.md`
- Retrieval note: `legal_family_retrieval_plan.md`
- Next thread: `NEXT_THREAD_PROMPT_FAMILY_MAP_HARDENING.md`
