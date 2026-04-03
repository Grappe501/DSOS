"""Schedule workflow starter for v0.7.0."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import Schedule
from app.services.audit_service import log_write_action

ALLOWED_TRANSITIONS = {
    "draft": {"submitted", "cancelled"},
    "submitted": {"approved", "rejected", "cancelled"},
    "approved": {"scheduled", "cancelled"},
    "scheduled": {"cancelled"},
    "rejected": {"draft", "cancelled"},
    "cancelled": set(),
}


def validate_transition(current_status: str, next_status: str) -> bool:
    return next_status in ALLOWED_TRANSITIONS.get(current_status, set())


def create_schedule_draft(db: Session, payload: dict[str, Any], actor) -> Schedule:
    row = Schedule(
        title=payload["title"],
        assigned_to=payload["assigned_to"],
        start_time=payload["start_time"],
        end_time=payload["end_time"],
        department=payload.get("department") or getattr(actor, "department", None),
        created_by_user_id=getattr(actor, "id", None),
        status="draft",
        recurrence_rule=payload.get("recurrence_rule"),
    )
    db.add(row)
    db.flush()
    log_write_action(
        db,
        action="schedule.created",
        entity_type="schedule",
        entity_id=row.id,
        actor_user_id=getattr(actor, "id", None),
        department=row.department,
        after={"status": row.status, "title": row.title},
    )
    return row


def transition_schedule(db: Session, schedule: Schedule, *, next_status: str, actor, reason: str | None = None) -> Schedule:
    if not validate_transition(schedule.status, next_status):
        raise ValueError(f"invalid transition: {schedule.status} -> {next_status}")
    before = {"status": schedule.status}
    schedule.status = next_status
    if next_status == "submitted":
        setattr(schedule, "submitted_by_user_id", getattr(actor, "id", None))
        setattr(schedule, "submitted_at", datetime.utcnow())
    elif next_status == "approved":
        setattr(schedule, "approved_by_user_id", getattr(actor, "id", None))
        setattr(schedule, "approved_at", datetime.utcnow())
    elif next_status == "rejected":
        setattr(schedule, "rejected_by_user_id", getattr(actor, "id", None))
        setattr(schedule, "rejected_at", datetime.utcnow())
        setattr(schedule, "rejection_reason", reason)
    elif next_status == "cancelled":
        setattr(schedule, "cancelled_by_user_id", getattr(actor, "id", None))
        setattr(schedule, "cancelled_at", datetime.utcnow())
    db.flush()
    log_write_action(
        db,
        action=f"schedule.{next_status}",
        entity_type="schedule",
        entity_id=schedule.id,
        actor_user_id=getattr(actor, "id", None),
        department=getattr(schedule, "department", None),
        before=before,
        after={"status": schedule.status, "reason": reason},
    )
    return schedule
