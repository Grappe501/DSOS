# Malone Legal Handbook Vertical Slice — Pass Report

**Pass date:** 2026-04-16  
**Scope:** One deterministic vertical slice for the Arkansas State Board of Pharmacy “Statutes and Rules” November 2025–style compilation (text-in ingestion path).  
**Active lanes honored:** `app/`, `schemas/`, `alembic/`, `tracking/` only.

---

## 1. WHAT THIS PASS IMPLEMENTED

### Concrete persisted capabilities added

- **Database:** Alembic `0003_legal_handbook_knowledge_foundation` (already present) is the persistence target; companion DDL `schemas/legal_handbook_knowledge_v0.sql` documents the same tables.
- **ORM:** `app/models/legal_handbook.py` mirrors legal-handbook tables so SQLAlchemy can insert/query rows alongside `Base.metadata.create_all` in dev.
- **Document + edition:** `legal_documents` and `legal_source_versions` rows created by `app/services/legal_knowledge/document_registry.py` and `app/services/legal_ingestion/arkansas_pipeline.py`.
- **Source families (A–H style):** `legal_document_families` populated from major `A.` … `H.` headings via `app/services/legal_ingestion/toc_parser.py` (heuristic: long titles to reduce TOC noise).
- **Legal units:** `legal_units` for Ark. Code–style sections (`17-92-115`), Roman “Section VII”, and `PDMP Section VII` via `app/services/legal_ingestion/legal_unit_parser.py`.
- **Subsection-preserving chunks:** `legal_unit_chunks` from `subsection_parser.py` + `chunk_builder.py` (not character-window chunking as the primary boundary).
- **Citation anchors:** `legal_citations` with deterministic `citation_key`, `normalized_citation` for statute-style ids, and JSON `anchor_json` (family, citation, subsection path, heading).
- **Date layers:** `legal_date_layers` for compiled edition and per-family embedded revision labels (e.g. May 2023) via `date_layering.py`.
- **Lexical retrieval:** `app/services/legal_retrieval/lexical.py` (ILIKE across chunk body, headings, family titles, citation fields).
- **Citation / title lookup:** `app/services/legal_retrieval/citation_lookup.py` (exact normalized citation, heading phrase, family + body phrase).
- **Hybrid stub:** `app/services/legal_retrieval/hybrid.py` — lexical-only bundle with explicit `embedding_leg: disabled`.
- **Regulation foundation bridges:** `ingestion/parser.py` (UTF-8 decode + optional Arkansas profile normalization), `ingestion/chunker.py` (`chunk_legal_unit_body_subsections`), `knowledge/source_registry.py` (`draft_legal_handbook_bridge_meta`), `retrieval/lexical.py` (`search_handbook_lexical`), `retrieval/hybrid.py` (`retrieve_legal_handbook_evidence`).
- **Malone future-fit:** `assistant/orchestrator.py` (`outline_truth_packet_legal_evidence_slots`), `assistant/formatter.py` / `guardrails.py` stubs for legal evidence formatting and citation-key gates.
- **Fixture:** `tracking/fixtures/arkansas_handbook_vertical_slice_sample.txt` exercises the pipeline end-to-end.

### What is still scaffold only

- PDF binary parsing (no `pdftotext`/PyMuPDF integration in this pass; bytes must be UTF-8 text or pre-extracted text fed to the pipeline).
- `legal_cross_references` population and resolution.
- Embeddings, FTS5 virtual tables, vector hybrid scoring.
- `truth_packet_service.build_truth_packet` does **not** yet attach legal evidence (contract only).
- `malone_service` / intent routing unchanged — no user-visible regulation Q&A.

---

## 2. HOW THE ARKANSAS LAW BOOK IS NOW MODELED

| Concept | Representation |
|--------|------------------|
| **Document** | `legal_documents` — one compiled handbook upload (`stable_key`, `title`, `compiled_edition_label`, checksum/URI fields). |
| **Source family** | `legal_document_families` — major A–H bands with `family_code`, human `title`, optional `embedded_source_revision_label` (e.g. May 2023). |
| **Legal unit** | `legal_units` — statute sections, board rule sections, or PDMP sections; `primary_citation`, `heading_raw`, `toc_path`, `body_text`. |
| **Chunk** | `legal_unit_chunks` — subsection-preserving slices with `subsection_path` (e.g. `(b)(1)`), `body_text`, ordinals. |
| **Citation anchor** | `legal_citations` — stable `citation_key`, `normalized_citation`, `anchor_json` (family, legal citation, subsection path, section title). |

---

## 3. LEGAL PARSING DECISIONS

- **Statute sections:** Lines matching `^\s*\d{1,3}-\d{1,3}-\d{1,4}\b` start a `statute_section` unit; heading text is taken from the remainder of the first line when present.
- **Rule sections:** Lines matching `^Section\s+([IVXLCDM]+)` become `rule_section` units with primary citation `Section {ROMAN}`.
- **PDMP sections:** Lines matching `PDMP Section {ROMAN}` become `pdmp_section` units.
- **Subsection paths:** Lines whose trimmed text begins with one or more parenthesis tokens `(a)`, `(1)`, `(A)`, `(i)` … define a new chunk; continuation lines append to the current chunk. Paths are concatenated (e.g. `(b)(1)`).
- **Mixed dates:** Compilation date lives on `legal_source_versions` + `legal_date_layers` (`compiled_publication`). Embedded act dates inside a family title are stored on `legal_document_families.embedded_source_revision_label` and duplicated to `legal_date_layers` with `layer_kind=embedded_source_revision`. No automated “which layer wins legally” logic — persistence and disambiguation only.

---

## 4. MALONE INTEGRATION POINTS

- **Unchanged:** `app/api/malone_routes.py`, `handle_malone_request` sequence, proposal/workflow/truth packet/render/verify ordering.
- **Future truth-packet integration:** After intent routing, call `legal_retrieval.hybrid.retrieve_legal_evidence_bundle`, map hits into `outline_truth_packet_legal_evidence_slots()` shape, then extend `build_truth_packet` with an additive `legal_handbook_evidence` field (not done here).
- **Do not touch yet:** Embeddings pipeline, public regulation search API, frontend upload UI, passive roots (`backend/`, `frontend/`, `dsos_replacements/`).

---

## 5. IMPLEMENTATION GAPS

- Wire **optional** legal evidence into `truth_packet_service` behind a feature flag after intent classification supports a regulation scope.
- PDF text extraction with page numbers mapped into `page_start` / `page_end` on units and chunks.
- De-duplicate repeated ingests in dev DB or scope queries by `legal_source_version_id`.
- Populate `legal_cross_references` and resolver pass.
- FTS5 or token index for scale; citation disambiguation UI when multiple chunks share a normalized citation.

---

## 6. HARD-FAIL COMPLIANCE CHECK

| # | Condition | This pass |
|---|-----------|-----------|
| 1 | Modify `backend/`, `frontend/`, `dsos_replacements/` | **No** |
| 2 | Replace existing Malone behavior wholesale | **No** |
| 3 | Code without declared integration purpose | **No** — modules retain Purpose/Role docstrings |
| 4 | Schema direction away from versioning + citations | **No** — versions + citation rows preserved |
| 5 | Skip required tracking outputs | **No** — reports + state + contracts + next-thread prompt |
| 6 | Speculative regulation Q&A before registry + chunks + citations in DB | **No** — ingest persists first; chat path unchanged |

---

## Appendix: Entry points

- Ingest: `app.services.legal_ingestion.arkansas_pipeline.ingest_arkansas_handbook_text`
- Lexical: `app.services.legal_retrieval.lexical.search_legal_chunks_lexical`
- Lookup: `app.services.legal_retrieval.citation_lookup`
