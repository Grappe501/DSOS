"""
Purpose:
    Lexical search (substring, FTS, or SQLite-friendly MVP) over regulation chunk text.

Role in Malone:
    Supplies candidate chunk_ids and snippets for truth_packet evidence assembly.

Expected inputs:
    User query string; result limit; optional filters (future).

Expected outputs:
    Ranked hit list: chunk_id, snippet, scores (as implemented).

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session


def lexical_search_placeholder(query: str, *, limit: int = 8) -> list[dict[str, Any]]:
    del query, limit
    return []


def search_handbook_lexical(
    db: Session,
    query: str,
    *,
    limit: int = 8,
    legal_source_version_id: str | None = None,
    family_code: str | None = None,
    min_family_span_confidence: str | None = None,
) -> list[dict[str, Any]]:
    """
    Legal-handbook corpus (migration 0003). Regulation `regulation_chunks` search remains future work.
    """
    from app.services.legal_retrieval.lexical import search_legal_chunks_lexical

    return search_legal_chunks_lexical(
        db,
        query,
        limit=limit,
        legal_source_version_id=legal_source_version_id,
        family_code=family_code,
        min_family_span_confidence=min_family_span_confidence,
    )
