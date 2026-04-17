"""
Purpose:
    Inspect an uploaded handbook (metadata, page signals, cover block) to classify edition
    and provisional family boundaries before deep parsing.

Role in Malone:
    First deterministic stage of an ingestion job; feeds TOC/body zone hints for family mapping.

Expected inputs:
    Normalized linear corpus text, optional ``PageMap`` from PDF extraction.

Expected outputs:
    Structured profile: body anchor offset, optional 1-based body start page, zone diagnostics.

TODO boundary:
    No full-text OCR here unless a separate deterministic OCR stage is invoked by jobs.
"""

from __future__ import annotations

from typing import Any

from app.services.legal_ingestion.family_boundary import find_statute_body_start
from app.services.legal_ingestion.page_mapper import PageMap


def estimate_handbook_zones(text: str, page_map: PageMap | None = None) -> dict[str, Any]:
    """
    Deterministic TOC vs body split hints for Arkansas-style compilations.

    Integration: ``arkansas_pipeline`` may attach this under ``LegalSourceVersion.meta`` or job meta.
    """
    body_char = find_statute_body_start(text)
    out: dict[str, Any] = {
        "body_start_char": body_char,
        "body_start_page": None,
        "toc_zone_char_end": body_char,
    }
    if page_map is not None and body_char is not None:
        out["body_start_page"] = page_map.global_char_to_page(body_char)
    return out
