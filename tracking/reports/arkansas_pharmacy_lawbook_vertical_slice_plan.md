# Arkansas Pharmacy Law Book — Vertical Slice Plan

**Source:** Arkansas State Board of Pharmacy “Statutes and Rules” compilation (November 2025 cover; embedded act dates such as May 2023 / August 2025 inside families).

## Objectives (this slice)

1. Register one logical **document** + **source version** per uploaded compilation.
2. Decompose **major families** A–H with titles and optional embedded revision labels.
3. Extract **legal units:** Ark. Code sections (`d-d-d`), board rule Roman sections, PDMP Roman sections.
4. Split **subsection-preserving chunks** for `(a)`, `(1)`, `(A)`, `(i)`, and nested `(b)(1)`-style paths.
5. Persist **citation anchors** with deterministic keys for traces and UI.
6. Support **lexical + citation lookup** without embeddings.
7. Document **truth-packet evidence** mapping only (no chat wiring).

## Operational flow

1. Obtain **plain text** from the PDF (external extractor in a later pass; this slice accepts UTF-8 text).
2. Call `ingest_arkansas_handbook_text` with checksum/storage metadata when available.
3. Validate row counts and spot-check `legal_citations.anchor_json` for a few known citations.
4. Use `search_legal_chunks_lexical` / `find_chunks_by_citation_text` for QA harnesses.

## Out of scope (explicit)

- Multi-tenant uploads, embeddings, vector stores, public HTTP search routes, Malone chat answers.

## Success criteria

- Fixture ingest completes with non-zero families, chunks, and citations.
- Lookup by `17-92-115` returns chunk rows with matching `normalized_citation`.
- No edits under passive repository roots.
