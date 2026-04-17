"""
Exact / near-exact citation and title lookup against persisted `legal_citations`.

Role in Malone:
    Deterministic first stage when users supply statute numbers or PDMP section labels.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_handbook import LegalCitation, LegalDocumentFamily, LegalUnit, LegalUnitChunk
from app.services.legal_knowledge.citations import normalize_statute_like_citation


def _normalize_statute_citation(text: str) -> str:
    return normalize_statute_like_citation(text) or ""


def find_chunks_by_citation_text(
    db: Session,
    citation_query: str,
    *,
    legal_source_version_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Match `normalized_citation` (statute id) or substring against citation_key.

    Optional ``legal_source_version_id`` scopes results to one compiled ingest.
    """
    raw = (citation_query or "").strip()
    if not raw:
        return []
    norm = _normalize_statute_citation(raw)
    stmt = db.query(LegalCitation).join(
        LegalUnitChunk,
        LegalCitation.legal_unit_chunk_id == LegalUnitChunk.id,
    ).filter(
        (LegalCitation.normalized_citation == norm)
        | (LegalCitation.normalized_citation == raw)
        | (LegalCitation.citation_key == raw)
    )
    if legal_source_version_id:
        stmt = stmt.filter(LegalUnitChunk.legal_source_version_id == legal_source_version_id)
    rows = stmt.all()
    return _hydrate_citations(db, rows)


def find_chunks_by_section_title(
    db: Session,
    title_phrase: str,
    *,
    limit: int = 8,
    legal_source_version_id: str | None = None,
) -> list[dict[str, Any]]:
    """Case-insensitive match on unit heading (`heading_raw`)."""
    q = (title_phrase or "").strip()
    if not q:
        return []
    like = f"%{q}%"
    units = db.query(LegalUnit).filter(LegalUnit.heading_raw.ilike(like)).limit(limit).all()
    out: list[dict[str, Any]] = []
    for u in units:
        qchunks = db.query(LegalUnitChunk).filter(LegalUnitChunk.legal_unit_id == u.id)
        if legal_source_version_id:
            qchunks = qchunks.filter(LegalUnitChunk.legal_source_version_id == legal_source_version_id)
        chunks = qchunks.all()
        fam = db.get(LegalDocumentFamily, u.legal_document_family_id)
        for ch in chunks:
            cite = (
                db.query(LegalCitation).filter(LegalCitation.legal_unit_chunk_id == ch.id).one_or_none()
            )
            out.append(
                {
                    "legal_unit_chunk_id": ch.id,
                    "legal_source_version_id": ch.legal_source_version_id,
                    "citation_key": cite.citation_key if cite else None,
                    "primary_citation": u.primary_citation,
                    "heading_raw": u.heading_raw,
                    "family_code": fam.family_code if fam else None,
                    "family_title": fam.title if fam else None,
                    "subsection_path": ch.subsection_path,
                    "snippet": (ch.body_text or "")[:400],
                    "page_start": ch.page_start,
                    "page_end": ch.page_end,
                }
            )
    return out


def find_chunks_by_family_and_phrase(
    db: Session,
    *,
    family_title_phrase: str,
    text_phrase: str,
    limit: int = 8,
    legal_source_version_id: str | None = None,
    family_code: str | None = None,
) -> list[dict[str, Any]]:
    """Narrow lexical search: family title contains phrase AND chunk body contains text phrase."""
    ft = (family_title_phrase or "").strip()
    tp = (text_phrase or "").strip()
    if not ft or not tp:
        return []
    fam_like = f"%{ft}%"
    body_like = f"%{tp}%"
    stmt = (
        db.query(LegalUnitChunk)
        .join(LegalUnit, LegalUnitChunk.legal_unit_id == LegalUnit.id)
        .join(LegalDocumentFamily, LegalUnit.legal_document_family_id == LegalDocumentFamily.id)
        .filter(LegalDocumentFamily.title.ilike(fam_like))
        .filter(LegalUnitChunk.body_text.ilike(body_like))
    )
    if family_code:
        fc = family_code.strip().upper()[:1]
        stmt = stmt.filter(LegalDocumentFamily.family_code == fc)
    if legal_source_version_id:
        stmt = stmt.filter(LegalUnitChunk.legal_source_version_id == legal_source_version_id)
    rows = stmt.limit(limit).all()
    hits: list[dict[str, Any]] = []
    for ch in rows:
        unit = db.get(LegalUnit, ch.legal_unit_id)
        fam = db.get(LegalDocumentFamily, unit.legal_document_family_id) if unit else None
        cite = (
            db.query(LegalCitation).filter(LegalCitation.legal_unit_chunk_id == ch.id).one_or_none()
        )
        hits.append(
            {
                "legal_unit_chunk_id": ch.id,
                "legal_source_version_id": ch.legal_source_version_id,
                "citation_key": cite.citation_key if cite else None,
                "family_title": fam.title if fam else None,
                "snippet": (ch.body_text or "")[:400],
                "page_start": ch.page_start,
                "page_end": ch.page_end,
            }
        )
    return hits


def _hydrate_citations(db: Session, cites: list[LegalCitation]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c in cites:
        ch = db.get(LegalUnitChunk, c.legal_unit_chunk_id)
        if not ch:
            continue
        unit = db.get(LegalUnit, ch.legal_unit_id)
        fam = db.get(LegalDocumentFamily, unit.legal_document_family_id) if unit else None
        out.append(
            {
                "legal_unit_chunk_id": ch.id,
                "legal_source_version_id": ch.legal_source_version_id,
                "citation_key": c.citation_key,
                "normalized_citation": c.normalized_citation,
                "primary_citation": unit.primary_citation if unit else None,
                "family_code": fam.family_code if fam else None,
                "family_title": fam.title if fam else None,
                "subsection_path": ch.subsection_path,
                "snippet": (ch.body_text or "")[:400],
                "page_start": ch.page_start,
                "page_end": ch.page_end,
            }
        )
    return out
