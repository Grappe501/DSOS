"""
Stable `citation_key` + `anchor_json` builders for `legal_citations`.

Role in Malone:
    Truth-packet and trace layers reference `citation_key`; anchors carry display fields.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


def _slug_fragment(value: str, max_len: int = 96) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").upper()
    return s[:max_len] if len(s) > max_len else s


def stable_citation_key(
    *,
    edition_slug: str,
    family_code: str,
    primary_citation: str | None,
    subsection_path: str,
    ordinal: int,
    legal_unit_id: str | None = None,
) -> str:
    """
    Deterministic key for idempotent re-ingest (same inputs produce the same key).

    ``legal_unit_id`` disambiguates rare cases where two parsed units share the same
    primary citation and chunk ordinal within one family (multi-strategy family spans).
    """
    cite = primary_citation or "UNIT"
    path = subsection_path or ""
    scope = legal_unit_id or ""
    payload = "|".join([edition_slug, family_code, cite, path, str(ordinal), scope])
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:18]
    fam = family_code.upper()
    cite_part = _slug_fragment(cite, 48)
    return f"ARK-ASBP-{edition_slug}-FAM-{fam}-{cite_part}-P{_slug_fragment(path, 32) or 'ROOT'}-O{ordinal:04d}-{digest}"


def build_anchor_json(
    *,
    family_code: str,
    family_title: str | None,
    primary_citation: str | None,
    unit_kind: str,
    subsection_path: str | None,
    heading_raw: str | None,
    page_start: int | None = None,
    page_end: int | None = None,
    toc_path: str | None = None,
) -> dict[str, Any]:
    return {
        "family_code": family_code,
        "family_title": family_title,
        "legal_citation": primary_citation,
        "unit_kind": unit_kind,
        "subsection_path": subsection_path or "",
        "section_title": heading_raw,
        "page_start": page_start,
        "page_end": page_end,
        "toc_path": toc_path,
    }


def dumps_anchor(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def normalize_statute_like_citation(primary: str | None) -> str | None:
    """Collapse whitespace for Ark. Code-style citations (e.g. 17-92-115)."""
    if not primary:
        return None
    return re.sub(r"\s+", "", primary.strip())
