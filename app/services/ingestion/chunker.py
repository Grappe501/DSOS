"""
Purpose:
    Split normalized text into ordered chunks with stable ordinals and optional heading
    paths for citation anchoring.

Role in Malone:
    Chunk boundaries and ordinals feed citation keys and truth_packet evidence refs.

Expected inputs:
    Normalized string; optional structure hints from the parser; chunk size settings.

Expected outputs:
    List of draft dicts (ordinal, body_text, char offsets, etc.) ready for persistence.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any

from app.services.legal_ingestion.chunk_builder import draft_chunk_rows
from app.services.legal_ingestion.subsection_parser import split_subsection_segments


def chunk_normalized_text(
    text: str,
    *,
    max_chars: int = 3500,
    overlap_chars: int = 200,
) -> list[dict[str, Any]]:
    """
    Minimal placeholder splitter by character windows.

    Returns dicts with: ordinal, heading_path, body_text, char_start, char_end.
    """
    del overlap_chars  # reserved for overlap implementation
    if not text.strip():
        return []

    chunks: list[dict[str, Any]] = []
    n = len(text)
    ordinal = 0
    start = 0
    while start < n:
        end = min(start + max_chars, n)
        body = text[start:end]
        chunks.append(
            {
                "ordinal": ordinal,
                "heading_path": None,
                "body_text": body,
                "char_start": start,
                "char_end": end,
            }
        )
        ordinal += 1
        start = end
    return chunks


def chunk_legal_unit_body_subsections(unit_body: str) -> list[dict[str, Any]]:
    """
    Subsection-preserving boundaries for Arkansas-style compiled handbooks (not char-window splits).
    """
    segments = split_subsection_segments(unit_body)
    return draft_chunk_rows(segments)
