"""
Deterministic PDF text extraction for Arkansas handbook PDFs (page-ordered text).

Purpose:
    Feed `page_mapper` with per-page normalized strings; no OCR or image handling.

Role in Malone:
    Source fidelity for citation pages and retrieval evidence; ingestion-only.

Expected inputs:
    Local filesystem path to a PDF.

Expected outputs:
    Per-page normalized text and a concatenated corpus with stable page boundaries.

Notes:
    Uses `pypdf` (PyPDF2-compatible API). Extraction quality follows the PDF's embedded text layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ingestion.normalizer import normalize_extracted_text


@dataclass(frozen=True)
class PdfExtractResult:
    page_texts: list[str]
    page_count: int


def extract_pdf_pages(path: str) -> PdfExtractResult:
    """Extract one normalized text string per PDF page (1:1 with PDF page index)."""
    from pypdf import PdfReader

    reader = PdfReader(path)
    texts: list[str] = []
    for page in reader.pages:
        raw = page.extract_text()
        if raw is None:
            raw = ""
        texts.append(normalize_extracted_text(raw))
    return PdfExtractResult(page_texts=texts, page_count=len(texts))


def build_linear_corpus(page_texts: list[str]) -> tuple[str, list[int]]:
    """
    Join pages with ``\\n\\n`` and record the character offset where each page begins.

    Returns:
        ``full_text`` — concatenated corpus.
        ``page_char_starts`` — ``page_char_starts[i]`` = start index of PDF page ``i+1`` (0-based ``i``).
    """
    if not page_texts:
        return "", []

    starts: list[int] = []
    pos = 0
    parts: list[str] = []
    for i, t in enumerate(page_texts):
        if i > 0:
            pos += 2
        starts.append(pos)
        parts.append(t)
        pos += len(t)
    full_text = "\n\n".join(parts)
    if len(full_text) != pos:
        raise RuntimeError("corpus length invariant failed")
    return full_text, starts
