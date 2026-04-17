"""Lifecycle vocabulary for company knowledge (metadata + heads; does not replace source text)."""

from __future__ import annotations

# Stored in meta_json.company_knowledge_lifecycle and/or review artifact heads (stringly-typed).
STATE_DISCOVERED = "discovered"
STATE_INGESTED = "ingested"
STATE_VALIDATED = "validated"
STATE_UNDER_REVIEW = "under_review"
STATE_REVIEWED = "reviewed"
STATE_APPROVED_FOR_USE = "approved_for_use"
STATE_ACTIVE = "active"
STATE_REJECTED = "rejected"
STATE_SUPERSEDED = "superseded"
STATE_ARCHIVED = "archived"

COMPANY_KNOWLEDGE_STATES = frozenset(
    {
        STATE_DISCOVERED,
        STATE_INGESTED,
        STATE_VALIDATED,
        STATE_UNDER_REVIEW,
        STATE_REVIEWED,
        STATE_APPROVED_FOR_USE,
        STATE_ACTIVE,
        STATE_REJECTED,
        STATE_SUPERSEDED,
        STATE_ARCHIVED,
    }
)


def lifecycle_from_review_outcome(outcome: str) -> str:
    """Map review outcome to a coarse lifecycle label (governance metadata only)."""
    from app.services.review_feedback.review_status import (
        OUTCOME_APPROVED,
        OUTCOME_HOLD_FOR_REVIEW,
        OUTCOME_INFORMATIONAL,
        OUTCOME_NEEDS_REVISION,
        OUTCOME_READY_FOR_PROMOTION,
        OUTCOME_REJECTED,
        OUTCOME_RISK_FLAG,
    )

    o = (outcome or "").strip().lower()
    if o == OUTCOME_APPROVED:
        return STATE_APPROVED_FOR_USE
    if o == OUTCOME_REJECTED:
        return STATE_REJECTED
    if o == OUTCOME_NEEDS_REVISION:
        return STATE_UNDER_REVIEW
    if o == OUTCOME_INFORMATIONAL:
        return STATE_REVIEWED
    if o == OUTCOME_RISK_FLAG:
        return STATE_UNDER_REVIEW
    if o == OUTCOME_READY_FOR_PROMOTION:
        return STATE_VALIDATED
    if o == OUTCOME_HOLD_FOR_REVIEW:
        return STATE_UNDER_REVIEW
    return STATE_INGESTED
