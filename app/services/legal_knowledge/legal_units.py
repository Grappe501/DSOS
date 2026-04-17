"""
Helpers for `legal_units` trees: statute blocks, rule sections, nested nodes.

Role in Malone:
    Resolves “what is 17-92-115” to a unit id and chunk ids for retrieval.

Expected inputs:
    Family id, citation keys, parent ids.

Expected outputs:
    Unit rows and paths (`toc_path`, `subsection_path`).

TODO boundary:
    Full-text search lives in `legal_retrieval`; this module is identity and structure only.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.legal_handbook import LegalUnit
from app.services.legal_knowledge.citations import normalize_statute_like_citation


def list_units_by_primary_citation(db: Session, primary_citation: str) -> list[LegalUnit]:
    norm = normalize_statute_like_citation(primary_citation) or primary_citation.strip()
    return db.query(LegalUnit).filter(LegalUnit.primary_citation == norm).all()
