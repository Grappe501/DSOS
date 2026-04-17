"""Validate and build source linkage payloads for normalized units."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session


def validate_legal_chunk_link(
    db: Session,
    *,
    legal_unit_chunk_id: str,
    legal_source_version_id: str,
) -> tuple[bool, str | None]:
    from app.models.legal_handbook import LegalUnitChunk

    ch = db.get(LegalUnitChunk, legal_unit_chunk_id)
    if ch is None:
        return False, "legal_unit_chunk not found"
    if ch.legal_source_version_id and ch.legal_source_version_id != legal_source_version_id:
        return False, "chunk legal_source_version_id mismatch"
    return True, None


def validate_ingestion_segment_link(
    db: Session,
    *,
    ingestion_segment_id: str,
    ingestion_source_version_id: str,
) -> tuple[bool, str | None]:
    from app.models.ingestion_control import IngestionSegment

    seg = db.get(IngestionSegment, ingestion_segment_id)
    if seg is None:
        return False, "ingestion_segment not found"
    if seg.ingestion_source_version_id != ingestion_source_version_id:
        return False, "segment version mismatch"
    return True, None


def anchor_from_legal_chunk(citation_keys: list[str], anchor_json: dict[str, Any]) -> str:
    return json.dumps({"citation_keys": citation_keys, "legal_anchor": anchor_json}, ensure_ascii=False, sort_keys=True)
