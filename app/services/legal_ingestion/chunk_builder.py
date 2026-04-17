"""
Map parsed subsection segments to `legal_unit_chunks` row dicts.

Role in Malone:
    Supplies retrieval rows with subsection_path + body_text + ordinals.
"""

from __future__ import annotations

from typing import Any

from app.services.legal_ingestion.subsection_parser import SubsectionSegment


def draft_chunk_rows(
    segments: list[SubsectionSegment],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ordinal, seg in enumerate(segments):
        rows.append(
            {
                "ordinal": ordinal,
                "subsection_path": seg.subsection_path or None,
                "body_text": seg.body_text,
                "char_start": seg.char_start,
                "char_end": seg.char_end,
                "retrieval_ready": bool(seg.body_text and seg.body_text.strip()),
            }
        )
    return rows
