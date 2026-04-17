"""
Helpers for `legal_document_families` (handbook A–H bands and embedded revision labels).

Role in Malone:
    Family title + code scope lexical queries and citation display.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_handbook import LegalDocumentFamily


def list_families_for_document(db: Session, legal_document_id: str) -> list[LegalDocumentFamily]:
    return (
        db.query(LegalDocumentFamily)
        .filter(LegalDocumentFamily.legal_document_id == legal_document_id)
        .order_by(LegalDocumentFamily.sort_order.asc())
        .all()
    )


def parse_family_map_meta(meta_json: str | None) -> dict[str, Any]:
    """Return the ``family_map`` object from ``legal_document_families.meta_json``."""
    if not meta_json:
        return {}
    try:
        m = json.loads(meta_json)
    except json.JSONDecodeError:
        return {}
    return m.get("family_map") or {}


def family_span_confidence_rank(value: str | None) -> int:
    return {"high": 3, "medium": 2, "low": 1}.get((value or "").lower(), 0)


def family_meets_min_span_confidence(meta_json: str | None, min_confidence: str | None) -> bool:
    """If ``min_confidence`` is set, require stored ``span_confidence`` at or above that tier."""
    if not min_confidence:
        return True
    fm = parse_family_map_meta(meta_json)
    need = family_span_confidence_rank(min_confidence)
    got = family_span_confidence_rank(fm.get("span_confidence"))
    return got >= need
