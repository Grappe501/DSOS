from __future__ import annotations

import datetime
import json
from typing import Any

from app.db.session import SessionLocal
from app.events.event_bus import event_bus
from app.models.models import WorkflowState
from app.services.audit_service import write_audit
from app.utils.logger import log


def _upsert_workflow(
    workflow_name: str,
    entity_type: str,
    entity_id: str,
    state: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    db = SessionLocal()
    try:
        row = (
            db.query(WorkflowState)
            .filter(
                WorkflowState.workflow_name == workflow_name,
                WorkflowState.entity_type == entity_type,
                WorkflowState.entity_id == entity_id,
                WorkflowState.status == "active",
            )
            .first()
        )

        payload = json.dumps(metadata or {}, default=str)

        if row:
            row.state = state
            row.meta_json = payload
            row.updated_at = datetime.datetime.utcnow()
        else:
            row = WorkflowState(
                workflow_name=workflow_name,
                entity_type=entity_type,
                entity_id=entity_id,
                state=state,
                status="active",
                meta_json=payload,
                updated_at=datetime.datetime.utcnow(),
            )
            db.add(row)

        db.commit()

    except Exception as exc:
        db.rollback()
        log(f"Workflow upsert failed: {exc}")
        raise

    finally:
        db.close()


def start_schedule_workflow(payload: dict[str, Any]) -> None:
    log(f"Starting workflow for schedule {payload['schedule_id']}")

    _upsert_workflow(
        "schedule_followup",
        "schedule",
        payload["schedule_id"],
        "created",
        payload,
    )

    write_audit(
        "workflow.started",
        "schedule",
        payload["schedule_id"],
        {
            "workflow": "schedule_followup",
            "department": payload.get("department"),
        },
        actor_user_id=payload.get("actor_user_id"),
        actor_email=payload.get("actor_email"),
        actor_role=payload.get("actor_role"),
        actor_department=payload.get("actor_department") or payload.get("department"),
    )

    event_bus.emit(
        "workflow.started",
        {
            "workflow": "schedule_followup",
            "schedule_id": payload["schedule_id"],
            "assigned_to": payload["assigned_to"],
            "conflict_detected": payload["conflict_detected"],
            "department": payload.get("department"),
            "actor_user_id": payload.get("actor_user_id"),
            "actor_email": payload.get("actor_email"),
            "actor_role": payload.get("actor_role"),
            "actor_department": payload.get("actor_department") or payload.get("department"),
        },
    )


def route_conflict_resolution(payload: dict[str, Any]) -> None:
    if payload.get("conflict_detected"):
        _upsert_workflow(
            "schedule_followup",
            "schedule",
            payload["schedule_id"],
            "conflict_detected",
            payload,
        )

        event_bus.emit(
            "schedule.conflict.detected",
            {
                "schedule_id": payload["schedule_id"],
                "assigned_to": payload["assigned_to"],
                "department": payload.get("department"),
                "actor_user_id": payload.get("actor_user_id"),
                "actor_email": payload.get("actor_email"),
                "actor_role": payload.get("actor_role"),
                "actor_department": payload.get("actor_department") or payload.get("department"),
            },
        )


def mark_workflow_state(
    schedule_id: str,
    state: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    _upsert_workflow(
        "schedule_followup",
        "schedule",
        schedule_id,
        state,
        metadata or {},
    )
