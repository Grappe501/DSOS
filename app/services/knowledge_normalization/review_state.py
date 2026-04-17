"""Review / governance states for normalized knowledge units."""

from __future__ import annotations

REVIEW_DRAFT = "draft"
REVIEW_SYSTEM_GENERATED = "system_generated"
REVIEW_UNDER_REVIEW = "under_review"
REVIEW_REVIEWED = "reviewed"
REVIEW_APPROVED = "approved"
REVIEW_REJECTED = "rejected"
REVIEW_SUPERSEDED = "superseded"
REVIEW_NEEDS_REVISION = "needs_revision"

REVIEW_STATES = frozenset(
    {
        REVIEW_DRAFT,
        REVIEW_SYSTEM_GENERATED,
        REVIEW_UNDER_REVIEW,
        REVIEW_REVIEWED,
        REVIEW_APPROVED,
        REVIEW_REJECTED,
        REVIEW_SUPERSEDED,
        REVIEW_NEEDS_REVISION,
    }
)
