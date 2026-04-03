from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import WorkflowState
from app.services.audit_service import log_transition


def _serialize_meta(meta: dict[str, Any] | None) -> str | None:
    if meta is None:
        return None
    try:
        import json
        return json.dumps(meta, default=str)
    except Exception:
        return str(meta)


def mark_workflow_state(
    db: Session,
    *,
    workflow_name: str,
    entity_type: str,
    entity_id: int,
    state: str,
    status: str = "active",
    actor_user_id: int | None = None,
    department: str | None = None,
    meta_json: dict[str, Any] | None = None,
) -> WorkflowState:
    """
    Backward-compatible workflow writer.
    """
    row = WorkflowState(
        workflow_name=workflow_name,
        entity_type=entity_type,
        entity_id=entity_id,
        state=state,
        status=status,
        meta_json=_serialize_meta(meta_json),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    log_transition(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        from_state=None,
        to_state=state,
        actor_user_id=actor_user_id,
        department=department,
        meta_json={
            "workflow_name": workflow_name,
            "status": status,
            **(meta_json or {}),
        },
    )

    return row


def start_schedule_workflow(
    db: Session,
    *,
    schedule_id: int,
    actor_user_id: int | None = None,
    department: str | None = None,
    initial_state: str = "created",
    meta_json: dict[str, Any] | None = None,
) -> WorkflowState:
    """
    Legacy-compatible entry point used by wiring/schedule flow.
    """
    return mark_workflow_state(
        db,
        workflow_name="schedule_workflow",
        entity_type="schedule",
        entity_id=schedule_id,
        state=initial_state,
        status="active",
        actor_user_id=actor_user_id,
        department=department,
        meta_json=meta_json,
    )


def route_conflict_resolution(
    db: Session,
    *,
    schedule_id: int,
    actor_user_id: int | None = None,
    department: str | None = None,
    reason: str | None = None,
    meta_json: dict[str, Any] | None = None,
) -> WorkflowState:
    """
    Legacy-compatible helper for conflict workflow routing.
    """
    payload = dict(meta_json or {})
    if reason is not None:
        payload["reason"] = reason

    return mark_workflow_state(
        db,
        workflow_name="schedule_workflow",
        entity_type="schedule",
        entity_id=schedule_id,
        state="conflict_resolution",
        status="active",
        actor_user_id=actor_user_id,
        department=department,
        meta_json=payload,
    )


def transition_schedule_state(
    db: Session,
    *,
    schedule_id: int,
    to_state: str,
    actor_user_id: int | None = None,
    department: str | None = None,
    meta_json: dict[str, Any] | None = None,
) -> WorkflowState:
    """
    Phase 3+ normalized helper.
    """
    return mark_workflow_state(
        db,
        workflow_name="schedule_approval",
        entity_type="schedule",
        entity_id=schedule_id,
        state=to_state,
        status="active",
        actor_user_id=actor_user_id,
        department=department,
        meta_json=meta_json,
    )


def get_entity_workflow_history(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
) -> list[WorkflowState]:
    return (
        db.query(WorkflowState)
        .filter(
            WorkflowState.entity_type == entity_type,
            WorkflowState.entity_id == entity_id,
        )
        .order_by(WorkflowState.created_at.asc())
        .all()
    )