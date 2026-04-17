# Arkansas Law Book — Source Map Plan (PDF Decomposition)

## Goal

Decompose the uploaded **compiled handbook** into addressable **sources of truth** for Malone: families, units, chunks, citations, and anchors—without assuming a single linear narrative.

## Layer 0 — Physical file

- **Artifact:** original PDF bytes.
- **Stored:** `legal_documents.storage_uri`, `content_checksum`, `original_filename`.
- **Signals:** page count, PDF outline (bookmarks) if present.

## Layer 1 — Cover and front matter

- **Extract:** title, board name, **compiled edition month/year** (e.g. November 2025).
- **Persist:** `legal_documents.compiled_edition_label`, `cover_metadata_json`, `legal_date_layers` (`layer_kind`: `compiled_edition`).

## Layer 2 — Table of contents

- **Identify:** labeled blocks **A–H** (major source families).
- **Capture:** family **title**, **start page** (and end page if determinable from TOC).
- **Persist:** `legal_document_families` with `family_code`, `sort_order`, `toc_page_start`/`toc_page_end`.
- **Embedded dates:** when the TOC or family header prints a revision (e.g. “Pharmacy Practice Act — May 2023”), store on **`embedded_source_revision_label`** and mirror into **`legal_date_layers`** (`layer_kind`: `embedded_act_as_of`).

## Layer 3 — Body text by family

- **Segment:** text spans per `toc_page_start`…`toc_page_end` (with overlap guards at boundaries).
- **Detect legal units:**
  - **Statute-centric blocks:** heading + `17-92-xxx` / `5-64-xxx` patterns.
  - **Rule-centric blocks:** “Section I …” and board-specific numbering.
- **Persist:** `legal_units` with `unit_kind`, `primary_citation`, `heading_raw`, `toc_path`.

## Layer 4 — Subsections

- **Walk** lines to detect `(a)`, `(1)`, `(A)`, `(i)` markers.
- **Persist:** `legal_unit_chunks` with `subsection_path` and body text; prefer **one chunk per subsection leaf** when length allows; otherwise split with shared path prefix.

## Layer 5 — Citations and anchors

- For each chunk, emit **`legal_citations`:**
  - `citation_key` (namespaced, unique),
  - `citation_kind` (statute vs rule vs internal),
  - `authority_type`,
  - `anchor_json` with **page** (and char offsets if extracted consistently).

## Layer 6 — Cross-references

- Regex + dictionary of known citation forms → **`legal_cross_references`**.
- Linker pass: resolve `to_citation_key` / `to_legal_unit_id`; leave `unresolved` when ambiguous.

## Failure modes

- **Missing outline:** fall back to TOC text extraction (page-scanned TOC may require OCR).
- **Family boundary drift:** use printed family headers as stronger signals than page ranges alone when both exist.

## Deliverable for next build pass

- A **deterministic fixture** (sample TOC + two families excerpt) to unit-test parsers before full PDF runs.
