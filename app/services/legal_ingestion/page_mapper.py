"""
Map global character offsets in the linear corpus to 1-based PDF page numbers.

Purpose:
    Ground families, units, chunks, and citation anchors to printable page ranges.

Role in Malone:
    Evidence displays (e.g. “pp. 12–15”) and audit without re-parsing the PDF at answer time.

Expected inputs:
    ``page_char_starts`` from ``pdf_extractor.build_linear_corpus`` and global ``char_start`` / ``char_end``.

Expected outputs:
    Inclusive 1-based page numbers for spans (``page_end`` >= ``page_start``).
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass


@dataclass(frozen=True)
class PageMap:
    """Maps offsets in ``full_text`` to PDF page numbers (1-based, same order as extraction)."""

    full_text: str
    page_char_starts: list[int]
    page_count: int

    def global_char_to_page(self, char_index: int) -> int:
        """1-based page number containing ``char_index`` (clamped)."""
        if not self.page_char_starts:
            return 1
        idx = bisect.bisect_right(self.page_char_starts, char_index) - 1
        idx = max(0, min(idx, self.page_count - 1))
        return idx + 1

    def span_to_page_range(self, char_start: int | None, char_end: int | None) -> tuple[int | None, int | None]:
        """
        Inclusive page range covering the half-open span ``[char_start, char_end)`` in ``full_text``.

        When offsets are unknown, returns (None, None).
        """
        if char_start is None or char_end is None:
            return None, None
        if char_end <= char_start and char_start == char_end:
            p = self.global_char_to_page(char_start)
            return p, p
        last_pos = char_end - 1 if char_end > char_start else char_start
        p_lo = self.global_char_to_page(char_start)
        p_hi = self.global_char_to_page(last_pos)
        return p_lo, p_hi
