"""List review heads, events, and artifact summaries."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.knowledge_normalization import NormalizedKnowledgeUnit
from app.models.review_feedback import MaloneReviewArtifactHead, MaloneReviewFeedbackEvent
from app.models.scenario_memory import MaloneScenarioMemory
from app.services.review_feedback.artifact_registry import ARTIFACT_TYPES


def list_heads(
    db: Session,
    *,
    artifact_type: str | None = None,
    current_state: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    q = db.query(MaloneReviewArtifactHead).order_by(MaloneReviewArtifactHead.updated_at.desc())
    if artifact_type:
        q = q.filter(MaloneReviewArtifactHead.artifact_type == artifact_type)
    if current_state:
        q = q.filter(MaloneReviewArtifactHead.current_review_state == current_state)
    rows = q.limit(min(max(limit, 1), 200)).all()
    return [serialize_head(r) for r in rows]


def list_events_for_artifact(
    db: Session,
    *,
    artifact_type: str,
    artifact_id: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    q = (
        db.query(MaloneReviewFeedbackEvent)
        .filter(
            MaloneReviewFeedbackEvent.artifact_type == artifact_type,
            MaloneReviewFeedbackEvent.artifact_id == artifact_id,
        )
        .order_by(MaloneReviewFeedbackEvent.created_at.desc())
    )
    return [serialize_event(r) for r in q.limit(min(max(limit, 1), 500)).all()]


def get_head(db: Session, *, artifact_type: str, artifact_id: str) -> dict[str, Any] | None:
    row = (
        db.query(MaloneReviewArtifactHead)
        .filter(
            MaloneReviewArtifactHead.artifact_type == artifact_type,
            MaloneReviewArtifactHead.artifact_id == artifact_id,
        )
        .one_or_none()
    )
    return serialize_head(row) if row else None


def serialize_head(row: MaloneReviewArtifactHead) -> dict[str, Any]:
    return {
        "id": row.id,
        "artifact_type": row.artifact_type,
        "artifact_id": row.artifact_id,
        "current_review_state": row.current_review_state,
        "current_trust_level": row.current_trust_level,
        "last_outcome": row.last_outcome,
        "last_reviewer_user_id": row.last_reviewer_user_id,
        "last_event_id": row.last_event_id,
        "updated_at": str(row.updated_at),
    }


def serialize_event(row: MaloneReviewFeedbackEvent) -> dict[str, Any]:
    import json

    meta = {}
    if row.meta_json:
        try:
            meta = json.loads(row.meta_json)
        except json.JSONDecodeError:
            meta = {}
    return {
        "id": row.id,
        "artifact_type": row.artifact_type,
        "artifact_id": row.artifact_id,
        "reviewer_user_id": row.reviewer_user_id,
        "outcome": row.outcome,
        "review_state_before": row.review_state_before,
        "review_state_after": row.review_state_after,
        "trust_level": row.trust_level,
        "risk_flag": row.risk_flag,
        "notes": row.notes,
        "meta_json": meta,
        "created_at": str(row.created_at),
    }


def summarize_normalized_unit_stub(db: Session, unit_id: str) -> dict[str, Any] | None:
    u = db.query(NormalizedKnowledgeUnit).filter(NormalizedKnowledgeUnit.id == unit_id).one_or_none()
    if not u:
        return None
    return {
        "id": u.id,
        "normalized_unit_type": u.normalized_unit_type,
        "source_type": u.source_type,
        "review_state": u.review_state,
        "confidence_level": u.confidence_level,
        "superseded": u.superseded,
        "title": u.title,
    }


def summarize_scenario_stub(db: Session, scenario_id: str) -> dict[str, Any] | None:
    sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == scenario_id).one_or_none()
    if not sm:
        return None
    return {
        "id": sm.id,
        "proposal_id": sm.proposal_id,
        "scenario_type": sm.scenario_type,
        "review_audit_status": sm.review_audit_status,
        "memory_status": sm.memory_status,
    }


def artifact_types_catalog() -> dict[str, Any]:
    return {"artifact_types": sorted(ARTIFACT_TYPES)}
