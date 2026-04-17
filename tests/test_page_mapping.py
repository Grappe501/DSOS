"""Unit tests for PDF linear corpus + PageMap (no PDF binary required)."""

from app.services.legal_ingestion.page_mapper import PageMap
from app.services.legal_ingestion.pdf_extractor import build_linear_corpus


def test_build_linear_corpus_invariants():
    pages = ["aa", "bb", "cc"]
    full, starts = build_linear_corpus(pages)
    assert full == "aa\n\nbb\n\ncc"
    assert starts == [0, 4, 8]
    assert len(full) == 10


def test_page_map_span():
    pages = ["x" * 10, "y" * 10]
    full, starts = build_linear_corpus(pages)
    pm = PageMap(full_text=full, page_char_starts=starts, page_count=2)
    assert pm.global_char_to_page(0) == 1
    assert pm.global_char_to_page(9) == 1
    assert pm.global_char_to_page(12) == 2
    lo, hi = pm.span_to_page_range(5, 15)
    assert lo == 1 and hi == 2
