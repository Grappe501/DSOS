# Legal Ingestion Profile — Arkansas Pharmacy Law Handbook

## Source shape

- **Single PDF** representing a **compiled** publication: Arkansas State Board of Pharmacy “Statutes and Rules” (cover example: **November 2025**).
- **Multiple source families** inside one file: TOC partitions labeled **A through H**, each potentially referencing different underlying acts or rule sets.
- **Mixed authorities:** Arkansas Code sections (numeric **title-section** patterns such as `17-92-101`, `5-64-101`) and **board rules** with headings such as “Section I”, “Section II”.
- **Nested subsections:** `(a)`, `(1)`, `(A)`, `(i)` paths must be preserved on chunks.
- **Cross-references:** Heavy internal references; some point to other families or citation forms.

## Profile parameters (deterministic)

| Parameter | Value |
|-----------|--------|
| `jurisdiction` | US-AR |
| `issuer` | Arkansas State Board of Pharmacy |
| `family_codes` | A, B, C, D, E, F, G, H |
| `statute_citation_regex` | `\b\d+-\d+-\d+\b` (candidate detection; validate with context) |
| `subsection_order` | roman → alpha → num → nested as printed |
| `date_layers` | Always split **compiled edition** vs **embedded act revision lines** |

## Ingestion stages (logical)

1. **Register document** → `legal_documents`, `legal_source_versions`.
2. **Profile cover** → `compiled_edition_label`, `cover_metadata_json`, `legal_date_layers` (document scope).
3. **Parse TOC** → `legal_document_families` with `toc_page_start`/`toc_page_end`.
4. **Per family: extract units** → `legal_units` (statute vs rule via heading templates + citation presence).
5. **Subsection split** → `legal_unit_chunks` with `subsection_path`.
6. **Citations** → `legal_citations` with stable `citation_key` and `authority_type`.
7. **Cross-refs** → `legal_cross_references` (resolve in linker pass).
8. **Tags (optional)** → `legal_tags` / `legal_chunk_tags` for pharmacy topics.

## Quality gates

- **No chunk without resolvable provenance:** at minimum `legal_unit_id`, `family_code` in anchor metadata, and page or char span.
- **No silent date merge:** if the handbook prints “August 2025” inside one family and “May 2023” inside another, both must appear in `legal_date_layers` or family fields.

## Out of scope (this profile)

- OCR vendor selection and layout ML.
- Automatic determination of law outside the uploaded PDF.
