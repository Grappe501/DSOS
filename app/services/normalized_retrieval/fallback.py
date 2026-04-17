"""When to use normalized fields vs raw evidence only."""

from __future__ import annotations

from app.services.knowledge_normalization.review_state import (
    REVIEW_APPROVED,
    REVIEW_DRAFT,
    REVIEW_NEEDS_REVISION,
    REVIEW_REJECTED,
    REVIEW_REVIEWED,
    REVIEW_SUPERSEDED,
    REVIEW_SYSTEM_GENERATED,
    REVIEW_UNDER_REVIEW,
)


def review_rank(review_state: str | None) -> int:
    """Higher = more trustworthy for augmentation."""
    r = (review_state or "").strip().lower()
    return {
        REVIEW_APPROVED: 6,
        REVIEW_REVIEWED: 5,
        REVIEW_SYSTEM_GENERATED: 4,
        REVIEW_UNDER_REVIEW: 3,
        REVIEW_DRAFT: 2,
        REVIEW_NEEDS_REVISION: 2,
        REVIEW_REJECTED: 0,
        REVIEW_SUPERSEDED: 0,
    }.get(r, 2)


def confidence_rank(confidence_level: str | None) -> int:
    c = (confidence_level or "").strip().lower()
    return {"high": 3, "medium": 2, "low": 1, "unknown": 0}.get(c, 1)


def unit_is_blocked(unit: object) -> bool:
    """Do not surface normalized content when blocked."""
    rs = getattr(unit, "review_state", None) or ""
    if rs == REVIEW_REJECTED:
        return True
    if getattr(unit, "superseded", False):
        return True
    return False


def unit_needs_caveat(unit: object) -> bool:
    """Extra caution line for LLM or user (not blocking deterministic append)."""
    c = getattr(unit, "confidence_level", None) or ""
    rs = getattr(unit, "review_state", None) or ""
    return c == "unknown" or rs in (REVIEW_DRAFT, REVIEW_NEEDS_REVISION)
