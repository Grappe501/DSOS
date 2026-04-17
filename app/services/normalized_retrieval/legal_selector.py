"""Load normalized knowledge units for legal handbook chunks."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.knowledge_normalization import NormalizationRun, NormalizedKnowledgeUnit
from app.services.normalized_retrieval.fallback import unit_is_blocked
from app.services.normalized_retrieval.ranking import pick_top_per_key, sort_units_for_display


def fetch_normalized_units_for_legal_chunks(
    db: Session,
    *,
    legal_source_version_id: str,
    chunk_ids: list[str],
) -> list[NormalizedKnowledgeUnit]:
    """
    Return normalized units tied to chunks, scoped to version, from successful runs only.
    """
    if not chunk_ids or not legal_source_version_id:
        return []

    q = (
        db.query(NormalizedKnowledgeUnit)
        .join(NormalizationRun, NormalizedKnowledgeUnit.normalization_run_id == NormalizationRun.id)
        .filter(NormalizedKnowledgeUnit.legal_source_version_id == legal_source_version_id)
        .filter(NormalizedKnowledgeUnit.legal_unit_chunk_id.in_(chunk_ids))
        .filter(NormalizedKnowledgeUnit.superseded.is_(False))
        .filter(NormalizationRun.validation_status.in_(("PASS", "PASS_WITH_WARNINGS")))
    )
    rows = q.all()
    usable = [u for u in rows if not unit_is_blocked(u)]
    return sort_units_for_display(usable)


def group_units_by_chunk_id(units: list[Any]) -> dict[str, list[Any]]:
    return pick_top_per_key(
        units,
        key_fn=lambda u: str(getattr(u, "legal_unit_chunk_id", "") or ""),
        max_per_key=2,
    )
