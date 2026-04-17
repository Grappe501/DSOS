# Malone PDF Grounding Pass — Report

**Pass date:** 2026-04-16  
**Scope:** Deterministic PDF-grounded ingestion for the Arkansas State Board of Pharmacy law book (text extraction + page map + persisted page fields + retrieval scoping).  
**Active lanes:** `app/`, `schemas/`, `alembic/`, `tracking/` only.

---

## 1. WHAT THIS PASS IMPLEMENTED

### Real PDF-grounded capabilities added

- **`pypdf`-based extraction:** `app/services/legal_ingestion/pdf_extractor.py` extracts text per PDF page in order, normalizes each page, then builds a linear corpus with stable `page_char_starts`.
- **Page map:** `app/services/legal_ingestion/page_mapper.py` maps global character indices to **1-based PDF page numbers** and inclusive page ranges for spans.
- **PDF ingest entrypoint:** `ingest_arkansas_handbook_pdf` in `arkansas_pipeline.py` (checksum, `file://` storage hint, page-grounded job metadata).
- **Persistence:** `toc_page_start` / `toc_page_end` on families, `page_start` / `page_end` on units and chunks when offsets exist; citation `anchor_json` includes pages plus `display` / `compilation_label` via `anchor_builder.py`.
- **Global body offsets:** `LegalUnitSpan.body_global_char_start` drives subsection segment global offsets for chunk page grounding.
- **Retrieval scoping:** `legal_source_version_id` column on `legal_unit_chunks` (Alembic `0004`) with filters on lexical and citation lookup paths.
- **Regression smoke:** `tracking/scripts/pdf_grounding_smoke.py` validates extraction + map without DB ingest.

### What remained unchanged

- Malone routes, `malone_service`, `truth_packet_service` behavior (no production wiring).
- Embeddings / vector retrieval / public Q&A APIs.
- Passive repository roots (`backend/`, `frontend/`, `dsos_replacements/`).

---

## 2. HOW PAGE GROUNDING NOW WORKS

### Extraction path

- `extract_pdf_pages(path)` → per-page normalized strings.
- `build_linear_corpus(page_texts)` → `full_text` + `page_char_starts[i]` = start offset of PDF page `i+1`.

### Page map

- `PageMap.global_char_to_page(i)` → 1-based page containing character `i`.
- `PageMap.span_to_page_range(start, end)` → inclusive page range for half-open `[start, end)` in `full_text`.

### Family / unit / chunk grounding

- **Families:** `parse_family_spans` char spans → page range via `PageMap`.
- **Units:** unit `char_start`/`char_end` (global) → unit `page_start`/`page_end`.
- **Chunks:** subsection segments use `body_global_char_start` + local offsets; chunk `page_start`/`page_end` from segment span, falling back to the unit’s page range if segment offsets are missing.

### Citation grounding

- `build_anchor_json` receives `page_start`/`page_end`; `enrich_anchor_display` adds `display.pages`, statute/family lines, and `compilation_label`.

---

## 3. DATA MODEL IMPACT

### ORM

- `LegalUnitChunk.legal_source_version_id` added (optional FK in ORM; SQLite migration adds plain `VARCHAR`).

### Migration

- **`0004_legal_unit_chunk_source_version`:** adds column + index (idempotent for dev DBs where `create_all` already added the column).

### Page fields now relied on

- **Families:** `toc_page_start`, `toc_page_end` when PDF path used.
- **Units / chunks:** `page_start`, `page_end` when global offsets resolve; chunks always receive `legal_source_version_id` on new ingests.

---

## 4. RETRIEVAL SAFETY IMPROVEMENTS

- **Scoping:** `search_legal_chunks_lexical`, `find_chunks_by_citation_text`, `find_chunks_by_section_title`, `find_chunks_by_family_and_phrase`, and `retrieve_legal_evidence_bundle` accept optional `legal_source_version_id`.
- **Duplicate bleed:** Multiple compiles in one SQLite file no longer mix when callers pass the version id from the active ingest. Rows **without** a version id (legacy text-only ingests) do not match a strict version filter.

---

## 5. MALONE INTEGRATION BOUNDARY

- **Intentionally not wired:** truth packet assembly, intent routing, user-facing answers, upload UI.
- **Future:** pass `legal_source_version_id` from the selected handbook snapshot when attaching evidence.

---

## 6. IMPLEMENTATION GAPS

- **TOC / family detection:** The `A.` / `H.` long-title heuristic may yield a **single family block** on some PDF extracts until patterns are tuned against real TOC vs body layout (observed: 1 family on the Dec 2025 PDF sample run despite full chunk coverage).
- **OCR:** No scanned-page OCR; extraction quality follows embedded text.
- **Column-level FK on SQLite:** Migration omits DB-level FK for compatibility; integrity is application-level.

---

## 7. HARD-FAIL COMPLIANCE CHECK

| Condition | Status |
|-----------|--------|
| Passive roots modified | **No** |
| Malone replaced wholesale | **No** |
| Code without integration purpose | **No** |
| Versioning + citation direction broken | **No** |
| Required tracking outputs skipped | **No** |
| Speculative user-facing Q&A before source fidelity | **No** |

---

## Verification notes (local)

- Smoke script on `Lawbook-2025-Dec-1.pdf`: 439 pages, non-empty text on all pages.
- Full ingest on same PDF completed with `page_grounded: true` and sample chunk pages populated (e.g. page 163).
- Lexical search with a bogus version id returned zero rows; with the ingest version id returned scoped hits.
