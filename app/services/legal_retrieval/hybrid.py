"""
Integration-aware hybrid stub: lexical-only until embeddings exist.

Role in Malone:
    Single call site to assemble an evidence-shaped bundle for `truth_packet_service`.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.services.legal_retrieval.lexical import search_legal_chunks_lexical


def retrieve_legal_evidence_bundle(
    db: Session,
    query: str,
    *,
    limit: int = 10,
    legal_source_version_id: str | None = None,
) -> dict[str, Any]:
    """
    Returns ranked lexical hits with explicit warning when vector leg is absent.
    """
    hits = search_legal_chunks_lexical(
        db,
        query,
        limit=limit,
        legal_source_version_id=legal_source_version_id,
    )
    return {
        "chunks": hits,
        "warnings": [] if hits else ["no_lexical_hits"],
        "embedding_leg": "disabled",
    }
