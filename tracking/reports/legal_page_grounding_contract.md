# Legal Page Grounding Contract

## Coordinate system

- All offsets are indices into the **normalized linear corpus** returned by `build_linear_corpus`.
- Spans follow Python half-open semantics: `[char_start, char_end)`.

## Mapping rules

- **Single position:** `PageMap.global_char_to_page(pos)` returns the 1-based PDF page containing `pos`.
- **Span:** `PageMap.span_to_page_range(start, end)` returns inclusive `(page_start, page_end)` covering all characters in the span.

## Entity grounding

| Entity | Primary span | DB columns |
|--------|----------------|------------|
| Family | `FamilySpan.char_start`–`char_end` | `legal_document_families.toc_page_start`, `toc_page_end` |
| Legal unit | `LegalUnitSpan.char_start`–`char_end` | `legal_units.page_start`, `page_end` |
| Chunk | Subsection segment global offsets, else unit span | `legal_unit_chunks.page_start`, `page_end` |

## Citation anchors

- `anchor_json.page_start` / `page_end` mirror chunk pages when available.
- `anchor_json.display.pages` holds a printable range string (e.g. `163–165`).

## Subsection path

- Unchanged: `subsection_path` remains independent of page numbers; pages annotate location, not hierarchy.
