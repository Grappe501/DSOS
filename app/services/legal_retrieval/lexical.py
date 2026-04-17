"""
Lexical search over `legal_unit_chunks` (substring / LIKE) for SQLite MVP.

Role in Malone:
    Baseline retrieval before embeddings; feeds hybrid + truth-packet evidence planning.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.legal_handbook import (
    LegalCitation,
    LegalDocumentFamily,
    LegalUnit,
    LegalUnitChunk,
)
from app.services.legal_knowledge.source_families import (
    family_meets_min_span_confidence,
    parse_family_map_meta,
)


def search_legal_chunks_lexical(
    db: Session,
    query: str,
    *,
    limit: int = 12,
    legal_source_version_id: str | None = None,
    family_code: str | None = None,
    min_family_span_confidence: str | None = None,
) -> list[dict[str, Any]]:
    """
    Case-insensitive substring search across chunk body and citation strings.

    When ``legal_source_version_id`` is set, only chunks tied to that ingest version are returned
    (prevents cross-version bleed when multiple compiles exist in one dev database).

    ``family_code`` optionally restricts hits to one major handbook family (A–H).

    ``min_family_span_confidence`` (``high`` / ``medium`` / ``low``) filters on persisted
    ``family_map.span_confidence`` so callers can avoid over-trusting low-confidence boundaries.
    When set, results are filtered in Python after an over-fetch (deterministic ordering preserved).
    """
    q = (query or "").strip()
    if not q:
        return []
    like = f"%{q}%"
    stmt = (
        db.query(LegalUnitChunk)
        .join(LegalUnit, LegalUnitChunk.legal_unit_id == LegalUnit.id)
        .join(LegalDocumentFamily, LegalUnit.legal_document_family_id == LegalDocumentFamily.id)
        .outerjoin(LegalCitation, LegalCitation.legal_unit_chunk_id == LegalUnitChunk.id)
        .filter(
            or_(
                LegalUnitChunk.body_text.ilike(like),
                LegalCitation.citation_key.ilike(like),
                LegalCitation.normalized_citation.ilike(like),
                LegalUnit.heading_raw.ilike(like),
                LegalDocumentFamily.title.ilike(like),
            )
        )
    )
    if legal_source_version_id:
        stmt = stmt.filter(LegalUnitChunk.legal_source_version_id == legal_source_version_id)
    if family_code:
        fc = family_code.strip().upper()[:1]
        stmt = stmt.filter(LegalDocumentFamily.family_code == fc)
    fetch = limit * 4 if min_family_span_confidence else limit
    rows = stmt.limit(fetch).all()

    hits: list[dict[str, Any]] = []
    for ch in rows:
        unit = db.get(LegalUnit, ch.legal_unit_id)
        fam = db.get(LegalDocumentFamily, unit.legal_document_family_id) if unit else None
        if fam and not family_meets_min_span_confidence(fam.meta_json, min_family_span_confidence):
            continue
        cite = (
            db.query(LegalCitation)
            .filter(LegalCitation.legal_unit_chunk_id == ch.id)
            .one_or_none()
        )
        hits.append(
            {
                "legal_unit_chunk_id": ch.id,
                "legal_source_version_id": ch.legal_source_version_id,
                "citation_key": cite.citation_key if cite else None,
                "snippet": (ch.body_text or "")[:400],
                "family_code": fam.family_code if fam else None,
                "family_title": fam.title if fam else None,
                "family_span_confidence": _family_span_confidence_value(fam.meta_json if fam else None),
                "subsection_path": ch.subsection_path,
                "primary_citation": unit.primary_citation if unit else None,
                "page_start": ch.page_start,
                "page_end": ch.page_end,
            }
        )
        if len(hits) >= limit:
            break
    return hits


def _family_span_confidence_value(meta_json: str | None) -> str | None:
    fm = parse_family_map_meta(meta_json)
    v = fm.get("span_confidence")
    return str(v) if v else None
