"""Outcomes and state mapping for review events (governance, not source truth)."""

from __future__ import annotations

from typing import Any

from app.services.knowledge_normalization.review_state import (
    REVIEW_APPROVED,
    REVIEW_NEEDS_REVISION,
    REVIEW_REJECTED,
    REVIEW_REVIEWED,
    REVIEW_SYSTEM_GENERATED,
    REVIEW_UNDER_REVIEW,
)

OUTCOME_APPROVED = "approved"
OUTCOME_REJECTED = "rejected"
OUTCOME_NEEDS_REVISION = "needs_revision"
OUTCOME_INFORMATIONAL = "informational"
OUTCOME_RISK_FLAG = "risk_flag"

OUTCOMES = frozenset(
    {
        OUTCOME_APPROVED,
        OUTCOME_REJECTED,
        OUTCOME_NEEDS_REVISION,
        OUTCOME_INFORMATIONAL,
        OUTCOME_RISK_FLAG,
    }
)

# Scenario memory / trace audit column (stringly-typed; see scenario_store defaults)
SCENARIO_REVIEW_PENDING = "pending"
SCENARIO_REVIEW_UNDER_REVIEW = "under_review"
SCENARIO_REVIEW_REVIEWED = "reviewed"
SCENARIO_REVIEW_APPROVED = "approved"
SCENARIO_REVIEW_REJECTED = "rejected"
SCENARIO_REVIEW_NEEDS_REVISION = "needs_revision"
SCENARIO_REVIEW_SUPERSEDED = "superseded"


def map_outcome_to_normalized_review_state(
    outcome: str,
    *,
    prior: str | None,
) -> str | None:
    """Return new NormalizedKnowledgeUnit.review_state, or None if unchanged."""
    o = (outcome or "").strip().lower()
    if o == OUTCOME_APPROVED:
        return REVIEW_APPROVED
    if o == OUTCOME_REJECTED:
        return REVIEW_REJECTED
    if o == OUTCOME_NEEDS_REVISION:
        return REVIEW_NEEDS_REVISION
    if o == OUTCOME_INFORMATIONAL:
        return REVIEW_REVIEWED
    if o == OUTCOME_RISK_FLAG:
        return REVIEW_UNDER_REVIEW
    return None


def map_outcome_to_scenario_audit_status(outcome: str, *, prior: str | None) -> str | None:
    o = (outcome or "").strip().lower()
    if o == OUTCOME_APPROVED:
        return SCENARIO_REVIEW_APPROVED
    if o == OUTCOME_REJECTED:
        return SCENARIO_REVIEW_REJECTED
    if o == OUTCOME_NEEDS_REVISION:
        return SCENARIO_REVIEW_NEEDS_REVISION
    if o == OUTCOME_INFORMATIONAL:
        return SCENARIO_REVIEW_REVIEWED
    if o == OUTCOME_RISK_FLAG:
        return SCENARIO_REVIEW_UNDER_REVIEW
    return prior


def head_state_from_normalized(rs: str | None) -> str:
    return (rs or REVIEW_SYSTEM_GENERATED).strip().lower()


def head_state_from_scenario_audit(audit: str | None) -> str:
    return (audit or SCENARIO_REVIEW_PENDING).strip().lower()


def merge_human_review_meta(existing_json: str | None, human_patch: dict[str, Any]) -> str:
    import json

    cur: dict[str, Any] = {}
    if existing_json and str(existing_json).strip():
        try:
            cur = json.loads(existing_json)
        except json.JSONDecodeError:
            cur = {}
    cur.setdefault("human_review", {})
    if isinstance(cur["human_review"], dict):
        cur["human_review"].update(human_patch)
    else:
        cur["human_review"] = dict(human_patch)
    return json.dumps(cur, ensure_ascii=False, default=str)
