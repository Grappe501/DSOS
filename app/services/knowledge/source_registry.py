"""
Purpose:
    Create and list regulation_sources and regulation_source_versions (logical identity
    and immutable version rows) once backed by the database.

Role in Malone:
    Read-only registry queries feed retrieval; Malone consumes chunk evidence, not raw
    registry CRUD from the chat path.

Expected inputs:
    stable_key, title, source_type, jurisdiction, version_label, checksum/storage hints.

Expected outputs:
    Record shapes or IDs for ingestion and retrieval layers.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any


def draft_source_record(
    *,
    stable_key: str,
    title: str,
    source_type: str,
    issuing_authority: str | None = None,
    jurisdiction: str | None = None,
) -> dict[str, Any]:
    """Return a dict shape for persistence; does not touch the database."""
    return {
        "stable_key": stable_key,
        "title": title,
        "source_type": source_type,
        "issuing_authority": issuing_authority,
        "jurisdiction": jurisdiction,
    }


def draft_legal_handbook_bridge_meta(
    *,
    legal_document_id: str,
    legal_source_version_id: str,
) -> dict[str, Any]:
    """
    Optional bridge metadata for `regulation_sources.meta_json` when mirroring the same upload
    in both corpora; keeps the legal-handbook tables as the authoritative decomposition.
    """
    return {
        "legal_document_id": legal_document_id,
        "legal_source_version_id": legal_source_version_id,
        "authoritative_corpus": "legal_handbook_v0",
    }
