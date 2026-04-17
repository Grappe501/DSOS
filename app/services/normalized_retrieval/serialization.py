"""Serialize ORM normalized units for bundles and answer formatting."""

from __future__ import annotations

from typing import Any


def normalized_unit_to_dict(unit: object) -> dict[str, Any]:
    """JSON-safe dict for truth packet / API (no SQLAlchemy objects)."""
    return {
        "id": getattr(unit, "id", None),
        "normalized_unit_type": getattr(unit, "normalized_unit_type", None),
        "source_type": getattr(unit, "source_type", None),
        "title": getattr(unit, "title", None),
        "plain_language_summary": getattr(unit, "plain_language_summary", None),
        "applies_to_role": getattr(unit, "applies_to_role", None),
        "action_type": getattr(unit, "action_type", None),
        "requirement_level": getattr(unit, "requirement_level", None),
        "condition_text": getattr(unit, "condition_text", None),
        "exception_text": _truncate(getattr(unit, "exception_text", None), 800),
        "escalation_text": _truncate(getattr(unit, "escalation_text", None), 800),
        "output_outcome_text": getattr(unit, "output_outcome_text", None),
        "confidence_level": getattr(unit, "confidence_level", None),
        "review_state": getattr(unit, "review_state", None),
        "legal_unit_chunk_id": getattr(unit, "legal_unit_chunk_id", None),
        "ingestion_segment_id": getattr(unit, "ingestion_segment_id", None),
        "citation_keys_json": getattr(unit, "citation_keys_json", None),
        "anchor_json": getattr(unit, "anchor_json", None),
        "retrieval_headline": getattr(unit, "retrieval_headline", None),
    }


def _truncate(s: str | None, n: int) -> str | None:
    if s is None:
        return None
    s = s.strip()
    if len(s) <= n:
        return s
    return s[: n - 3] + "..."
