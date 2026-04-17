"""
Purpose:
    Build stable citation_key values and anchor_json payloads for regulation_citations
    rows and UI-safe references.

Role in Malone:
    Truth packet and delivery layers should reference citation_key for provenance display.

Expected inputs:
    Jurisdiction, version_label, ordinal; optional page/section anchor fields.

Expected outputs:
    citation_key string and anchor dict suitable for JSON storage.

Notes:
    This is a foundation scaffold for the regulation engine.
    Arkansas compiled-handbook anchors live in `app.services.legal_knowledge.citations` + `legal_citations`.
"""

from __future__ import annotations

from typing import Any


def build_citation_key(
    *,
    jurisdiction: str | None,
    version_label: str,
    ordinal: int,
) -> str:
    """Deterministic key suitable for logs (not a legal citation string)."""
    j = (jurisdiction or "UNK").upper().replace(" ", "_")
    safe_ver = version_label.replace(" ", "_")
    return f"{j}-{safe_ver}-CHUNK-{ordinal:05d}"


def build_anchor(
    *,
    page_start: int | None = None,
    page_end: int | None = None,
    section: str | None = None,
) -> dict[str, Any]:
    return {
        "page_start": page_start,
        "page_end": page_end,
        "section": section,
    }
