"""
Purpose:
    Combine lexical and embedding signals into a single ranked evidence bundle when both
    exist.

Role in Malone:
    Primary library hook for building regulation_evidence passed into truth_packet_service.

Expected inputs:
    User query; optional jurisdiction / as_of filters; retrieval limits.

Expected outputs:
    Evidence bundle: chunk ids, scores, citation keys, warnings.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session


def retrieve_evidence_placeholder(query: str) -> dict[str, Any]:
    del query
    return {"chunks": [], "warnings": ["retrieval_not_wired"]}


def retrieve_legal_handbook_evidence(
    db: Session,
    query: str,
    *,
    limit: int = 10,
    legal_source_version_id: str | None = None,
) -> dict[str, Any]:
    """Thin wrapper for Malone-time evidence assembly (lexical-only until embeddings land)."""
    from app.services.legal_retrieval.hybrid import retrieve_legal_evidence_bundle

    return retrieve_legal_evidence_bundle(
        db,
        query,
        limit=limit,
        legal_source_version_id=legal_source_version_id,
    )
