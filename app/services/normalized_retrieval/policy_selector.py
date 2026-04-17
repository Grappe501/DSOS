"""Policy manual: segment search + normalized unit lookup."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionSegment, IngestionSource, IngestionSourceVersion
from app.models.knowledge_normalization import NormalizationRun, NormalizedKnowledgeUnit
from app.services.ingestion_control.source_types import POLICY_MANUAL
from app.services.normalized_retrieval.fallback import unit_is_blocked
from app.services.normalized_retrieval.ranking import pick_top_per_key, sort_units_for_display


def resolve_default_policy_source_version_id(db: Session) -> str | None:
    """Latest policy_manual version by ``updated_at`` (any ingest status)."""
    hit = (
        db.query(IngestionSourceVersion)
        .join(IngestionSource, IngestionSourceVersion.ingestion_source_id == IngestionSource.id)
        .filter(IngestionSource.source_type == POLICY_MANUAL)
        .order_by(IngestionSourceVersion.updated_at.desc())
        .first()
    )
    return str(hit.id) if hit else None


_TOKEN = re.compile(r"\w{3,}")


def _tokens(q: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(q)][:12]


def search_policy_segments(
    db: Session,
    message: str,
    *,
    ingestion_source_version_id: str,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Lightweight lexical-ish match on segment body + heading."""
    raw = (message or "").strip()
    if not raw:
        return []
    toks = _tokens(raw)
    if not toks:
        return []

    segs = (
        db.query(IngestionSegment)
        .filter(IngestionSegment.ingestion_source_version_id == ingestion_source_version_id)
        .order_by(IngestionSegment.ordinal)
        .all()
    )
    scored: list[tuple[int, IngestionSegment]] = []
    blob_l = raw.lower()
    for seg in segs:
        hay = f"{seg.heading or ''}\n{seg.body_text or ''}".lower()
        score = sum(1 for t in toks if t in hay)
        if blob_l[:80] in hay or any(t in hay for t in toks[:3]):
            score += 2
        if score > 0:
            scored.append((score, seg))
    scored.sort(key=lambda x: (-x[0], x[1].ordinal))
    out: list[dict[str, Any]] = []
    for _, seg in scored[:limit]:
        out.append(
            {
                "ingestion_segment_id": seg.id,
                "ingestion_source_version_id": seg.ingestion_source_version_id,
                "heading": seg.heading,
                "snippet": (seg.body_text or "")[:1200],
                "anchor_key": seg.anchor_key,
                "ordinal": seg.ordinal,
            }
        )
    return out


def fetch_normalized_units_for_policy_segments(
    db: Session,
    *,
    ingestion_source_version_id: str,
    segment_ids: list[str],
) -> list[NormalizedKnowledgeUnit]:
    if not segment_ids:
        return []
    q = (
        db.query(NormalizedKnowledgeUnit)
        .join(NormalizationRun, NormalizedKnowledgeUnit.normalization_run_id == NormalizationRun.id)
        .filter(NormalizedKnowledgeUnit.ingestion_source_version_id == ingestion_source_version_id)
        .filter(NormalizedKnowledgeUnit.ingestion_segment_id.in_(segment_ids))
        .filter(NormalizedKnowledgeUnit.superseded.is_(False))
        .filter(NormalizationRun.validation_status.in_(("PASS", "PASS_WITH_WARNINGS")))
    )
    rows = q.all()
    usable = [u for u in rows if not unit_is_blocked(u)]
    return sort_units_for_display(usable)


def group_units_by_segment_id(units: list[Any]) -> dict[str, list[Any]]:
    return pick_top_per_key(
        units,
        key_fn=lambda u: str(getattr(u, "ingestion_segment_id", "") or ""),
        max_per_key=2,
    )
