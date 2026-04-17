"""JSON helpers for runner reports and machine-readable state."""

from __future__ import annotations

import json
from typing import Any


def dumps_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def unit_row_public_dict(row: Any) -> dict[str, Any]:
    """ORM → dict for reports (exclude huge fields optionally)."""
    return {
        "id": row.id,
        "ordinal": row.ordinal,
        "normalized_unit_type": row.normalized_unit_type,
        "title": row.title,
        "source_type": row.source_type,
        "legal_unit_chunk_id": row.legal_unit_chunk_id,
        "ingestion_segment_id": row.ingestion_segment_id,
        "confidence_level": row.confidence_level,
        "review_state": row.review_state,
        "requirement_level": row.requirement_level,
        "retrieval_headline": row.retrieval_headline,
    }
