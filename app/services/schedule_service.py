from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Query, Session

from app.models.models import Schedule
from app.services.audit_service import log_write_action


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"submitted", "cancelled"},
    "submitted": {"approved", "rejected", "cancelled"},
    "approved": {"scheduled", "cancelled"},
    "scheduled": {"cancelled"},
    "rejected": {"draft", "cancelled"},
    "cancelled": set(),
}


def _actor_payload(actor: Any, department: str | None = None) -> dict[str, Any] | None:
    if actor is None:
        return None

    return {
        "id": getattr(actor, "id", None),
        "email": getattr(actor, "email", None),
        "role": getattr(actor, "role", None),
        "department": department if department is not None else getattr(actor, "department", None),
    }


def _serialize_schedule(schedule: Schedule) -> dict[str, Any]:
    return {
        "id": getattr(schedule, "id", None),
        "title": getattr(schedule, "title", None),
        "assigned_to": getattr(schedule, "assigned_to", None),
        "department": getattr(schedule, "department", None),
        "status": getattr(schedule, "status", None),
        "start_time": getattr(schedule, "start_time", None).isoformat()
        if getattr(schedule, "start_time", None)
        else None,
        "end_time": getattr(schedule, "end_time", None).isoformat()
        if getattr(schedule, "end_time", None)
        else None,
        "recurrence_rule": getattr(schedule, "recurrence_rule", None),
        "created_by_user_id": getattr(schedule, "created_by_user_id", None),
        "submitted_by_user_id": getattr(schedule, "submitted_by_user_id", None),
        "approved_by_user_id": getattr(schedule, "approved_by_user_id", None),
        "rejected_by_user_id": getattr(schedule, "rejected_by_user_id", None),
        "cancelled_by_user_id": getattr(schedule, "cancelled_by_user_id", None),
        "submitted_at": getattr(schedule, "submitted_at", None).isoformat()
        if getattr(schedule, "submitted_at", None)
        else None,
        "approved_at": getattr(schedule, "approved_at", None).isoformat()
        if getattr(schedule, "approved_at", None)
        else None,
        "rejected_at": getattr(schedule, "rejected_at", None).isoformat()
        if getattr(schedule, "rejected_at", None)
        else None,
        "cancelled_at": getattr(schedule, "cancelled_at", None).isoformat()
        if getattr(schedule, "cancelled_at", None)
        else None,
        "rejection_reason": getattr(schedule, "rejection_reason", None),
        "created_at": getattr(schedule, "created_at", None).isoformat()
        if getattr(schedule, "created_at", None)
        else None,
        "updated_at": getattr(schedule, "updated_at", None).isoformat()
        if getattr(schedule, "updated_at", None)
        else None,
    }


def validate_transition(current_status: str | None, next_status: str) -> bool:
    if current_status is None:
        return next_status in {"draft", "submitted", "scheduled"}
    return next_status in ALLOWED_TRANSITIONS.get(current_status, set())


def apply_schedule_scope(
    query: Query,
    *,
    actor: Any,
    role_name: str,
) -> Query:
    if role_name in {"owner", "admin"}:
        return query

    actor_department = getattr(actor, "department", None)
    if actor_department:
        return query.filter(Schedule.department == actor_department)

    return query.filter(False)


def list_schedules(
    db: Session,
    *,
    actor: Any,
    role_name: str,
    department: str | None = None,
) -> list[Schedule]:
    query = db.query(Schedule)
    query = apply_schedule_scope(query, actor=actor, role_name=role_name)

    if department:
        if role_name in {"owner", "admin"} or department == getattr(actor, "department", None):
            query = query.filter(Schedule.department == department)

    return query.order_by(Schedule.start_time.desc()).all()


def get_schedule_by_id(
    db: Session,
    *,
    schedule_id: int | str,
    actor: Any,
    role_name: str,
) -> Schedule | None:
    query = db.query(Schedule).filter(Schedule.id == schedule_id)
    query = apply_schedule_scope(query, actor=actor, role_name=role_name)
    return query.first()


def create_schedule_draft(
    db: Session,
    payload: dict[str, Any],
    actor: Any,
) -> Schedule:
    department = payload.get("department") or getattr(actor, "department", None)

    row = Schedule(
        title=payload["title"],
        assigned_to=payload["assigned_to"],
        start_time=payload["start_time"],
        end_time=payload["end_time"],
        department=department,
        created_by_user_id=getattr(actor, "id", None),
        status=payload.get("status") or "draft",
        recurrence_rule=payload.get("recurrence_rule"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    log_write_action(
        db,
        action="schedule.created",
        entity_type="schedule",
        entity_id=row.id,
        actor=_actor_payload(actor, department=row.department),
        after_json=_serialize_schedule(row),
        meta_json={
            "assigned_to": getattr(row, "assigned_to", None),
            "recurrence_rule": getattr(row, "recurrence_rule", None),
        },
    )

    return row


def update_schedule(
    db: Session,
    *,
    schedule: Schedule,
    updates: dict[str, Any],
    actor: Any,
) -> Schedule:
    before = _serialize_schedule(schedule)

    mutable_fields = {
        "title",
        "assigned_to",
        "start_time",
        "end_time",
        "department",
        "recurrence_rule",
        "status",
    }

    for field, value in updates.items():
        if field in mutable_fields and value is not None:
            setattr(schedule, field, value)

    schedule.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(schedule)

    log_write_action(
        db,
        action="schedule.updated",
        entity_type="schedule",
        entity_id=schedule.id,
        actor=_actor_payload(actor, department=getattr(schedule, "department", None)),
        before_json=before,
        after_json=_serialize_schedule(schedule),
    )

    return schedule


def transition_schedule(
    db: Session,
    schedule: Schedule,
    *,
    next_status: str,
    actor: Any,
    reason: str | None = None,
) -> Schedule:
    current_status = getattr(schedule, "status", None)

    if not validate_transition(current_status, next_status):
        raise ValueError(f"invalid transition: {current_status} -> {next_status}")

    before = _serialize_schedule(schedule)

    schedule.status = next_status
    schedule.updated_at = datetime.utcnow()

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

    elif next_status == "scheduled":
        pass

    db.commit()
    db.refresh(schedule)

    log_write_action(
        db,
        action=f"schedule.{next_status}",
        entity_type="schedule",
        entity_id=schedule.id,
        actor=_actor_payload(actor, department=getattr(schedule, "department", None)),
        before_json=before,
        after_json=_serialize_schedule(schedule),
        meta_json={"reason": reason} if reason else None,
    )

    return schedule


def cancel_schedule(
    db: Session,
    *,
    schedule: Schedule,
    actor: Any,
    reason: str | None = None,
) -> Schedule:
    if getattr(schedule, "status", None) == "cancelled":
        return schedule

    if validate_transition(getattr(schedule, "status", None), "cancelled"):
        return transition_schedule(
            db,
            schedule,
            next_status="cancelled",
            actor=actor,
            reason=reason,
        )

    before = _serialize_schedule(schedule)

    schedule.status = "cancelled"
    schedule.cancelled_by_user_id = getattr(actor, "id", None)
    schedule.cancelled_at = datetime.utcnow()
    schedule.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(schedule)

    log_write_action(
        db,
        action="schedule.cancelled",
        entity_type="schedule",
        entity_id=schedule.id,
        actor=_actor_payload(actor, department=getattr(schedule, "department", None)),
        before_json=before,
        after_json=_serialize_schedule(schedule),
        meta_json={"reason": reason} if reason else None,
    )

    return schedule