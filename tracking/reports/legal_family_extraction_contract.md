# Legal Family Extraction Contract (Arkansas ASBP Handbook)

## Inputs

- **Linear corpus:** Normalized text from `build_linear_corpus` (PDF) or `normalize_extracted_text` (text ingest).
- **Optional `PageMap`:** Accepted by `parse_family_spans` for API compatibility; zone logic is primarily character-based.

## Major-family pattern

- Regex (multiline): line start, optional whitespace, letter `A`–`H`, `.` or `)`, whitespace, remainder of line = title.
- **TOC-style line:** Same pattern, plus line matches TOC shape: dot leaders (`...`) with trailing page digits, or a “Table of Contents” line (case-insensitive).
- **Non-TOC line before first statute:** Treated as a **body** major heading (not TOC noise).

## Statute anchor

- First line matching `(?m)^\s*\d{1,3}-\d{1,3}-\d{1,4}\b` defines the **statute split point** for TOC vs body classification.
- **Profiler** `find_statute_body_start` may still use a long-corpus fallback when no statute line exists (dev fixtures).

## Outputs

- Ordered list of `FamilySpan` values with:
  - `char_start` / `char_end` (half-open semantics for downstream slicing match existing pipeline: `[start, end)` in callers that slice text)
  - `family_code`, `title`, optional `embedded_revision`
  - `span_provenance`, `span_confidence`, optional TOC/body anchor offsets, reconciliation notes

## Invariants

- Family codes are single letters `A`–`H` for this compilation profile.
- Span ends align with the next family’s start or EOF.
- Page columns on `legal_document_families` remain derived from the same char spans via `PageMap` when PDF grounding is enabled.

## Limitations

- OCR and non-linear PDF layouts can still break line-based patterns.
- Short synthetic excerpts may not contain all eight families; extraction degrades via documented fallbacks.
