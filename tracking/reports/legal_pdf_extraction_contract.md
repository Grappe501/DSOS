# Legal PDF Extraction Contract

## Library

- **`pypdf`** (`PdfReader`) — embedded text layer only; no OCR in this pass.

## Procedure

1. For each page in order, call `page.extract_text()` (empty string if missing).
2. Apply `normalize_extracted_text` **per page** (NFKC, line/space cleanup).
3. Join pages with exactly two newlines (`\n\n`) as the inter-page delimiter.
4. Record `page_char_starts[i]` = character offset in the final string where PDF page `i+1` begins (0-based `i`).

## Invariants

- `len("\n\n".join(pages))` equals the final corpus length tracked by cumulative offsets.
- Page indices are **1-based** in `PageMap` outputs for human-facing “page N”.

## Inputs / outputs

- **Input:** Local filesystem path to one PDF.
- **Output:** `PdfExtractResult.page_texts`, then `build_linear_corpus` → `(full_text, page_char_starts)`.

## Limitations

- Rotated text, columns, and forms may extract out of reading order.
- Scanned bitmap pages may yield empty strings until an OCR pass exists.
