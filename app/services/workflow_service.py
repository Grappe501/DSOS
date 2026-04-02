import datetime
import json

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
    metadata: dict | None = None,
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

    except Exception as e:
        db.rollback()
        log(f"Workflow upsert failed: {e}")
        raise

    finally:
        db.close()


def start_schedule_workflow(payload: dict) -> None:
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
        {"workflow": "schedule_followup"},
    )

    event_bus.emit(
        "workflow.started",
        {
            "workflow": "schedule_followup",
            "schedule_id": payload["schedule_id"],
            "assigned_to": payload["assigned_to"],
            "conflict_detected": payload["conflict_detected"],
        },
    )


def route_conflict_resolution(payload: dict) -> None:
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
            },
        )


def mark_workflow_state(
    schedule_id: str,
    state: str,
    metadata: dict | None = None,
) -> None:
    _upsert_workflow(
        "schedule_followup",
        "schedule",
        schedule_id,
        state,
        metadata or {},
    )