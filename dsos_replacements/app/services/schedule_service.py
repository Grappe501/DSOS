from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import or_

from app.adapters.office365_adapter import office365_adapter
from app.db.session import SessionLocal
from app.events.event_bus import event_bus
from app.models.models import Schedule
from app.services.audit_service import write_audit


GLOBAL_ROLES = {"owner", "admin"}


def _apply_schedule_scope(query, actor_role: str | None, actor_department: str | None):
    if actor_role in GLOBAL_ROLES:
        return query
    if actor_department:
        return query.filter(Schedule.department == actor_department)
    return query.filter(Schedule.department.is_(None))


def detect_conflict(
    assigned_to: str,
    start_time,
    end_time,
    exclude_schedule_id: str | None = None,
) -> bool:
    db = SessionLocal()
    try:
        query = db.query(Schedule).filter(
            Schedule.assigned_to == assigned_to,
            Schedule.status != "cancelled",
            Schedule.start_time < end_time,
            Schedule.end_time > start_time,
        )
        if exclude_schedule_id:
            query = query.filter(Schedule.id != exclude_schedule_id)
        return query.first() is not None
    finally:
        db.close()


def _create_schedule_record(db, data: dict[str, Any], parent_schedule_id: str | None = None):
    conflict_detected = detect_conflict(data["assigned_to"], data["start_time"], data["end_time"])
    schedule = Schedule(
        title=data["title"],
        assigned_to=data["assigned_to"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        status="conflict" if conflict_detected else "scheduled",
        source="local",
        recurrence_rule=data.get("recurrence_rule"),
        parent_schedule_id=parent_schedule_id,
        created_by_user_id=data.get("created_by_user_id"),
        department=data.get("department"),
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule, conflict_detected


def _actor_kwargs(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "actor_user_id": data.get("actor_user_id"),
        "actor_email": data.get("actor_email"),
        "actor_role": data.get("actor_role"),
        "actor_department": data.get("actor_department") or data.get("department"),
    }


def _emit_created(schedule: Schedule, conflict_detected: bool, data: dict[str, Any]):
    event_bus.emit(
        "schedule.created",
        {
            "schedule_id": schedule.id,
            "title": schedule.title,
            "assigned_to": schedule.assigned_to,
            "start_time": schedule.start_time.isoformat(),
            "end_time": schedule.end_time.isoformat(),
            "conflict_detected": conflict_detected,
            "status": schedule.status,
            "department": schedule.department,
            **_actor_kwargs(data),
        },
    )


def _emit_updated(schedule: Schedule, conflict_detected: bool, data: dict[str, Any]):
    event_bus.emit(
        "schedule.updated",
        {
            "schedule_id": schedule.id,
            "assigned_to": schedule.assigned_to,
            "conflict_detected": conflict_detected,
            "status": schedule.status,
            "department": schedule.department,
            **_actor_kwargs(data),
        },
    )


def _emit_cancelled(schedule: Schedule, data: dict[str, Any]):
    event_bus.emit(
        "schedule.cancelled",
        {
            "schedule_id": schedule.id,
            "assigned_to": schedule.assigned_to,
            "department": schedule.department,
            **_actor_kwargs(data),
        },
    )


def _sync_create(db, schedule: Schedule):
    result = office365_adapter.create_event(
        {"id": schedule.id, "title": schedule.title, "assigned_to": schedule.assigned_to}
    )
    if result.get("success"):
        schedule.synced_to_office365 = True
        schedule.office365_event_id = result.get("office365_event_id")
        db.commit()


def create_schedule(data: dict[str, Any]):
    db = SessionLocal()
    try:
        schedule, conflict_detected = _create_schedule_record(db, data)
        if data.get("sync_to_office365"):
            _sync_create(db, schedule)

        write_audit(
            "schedule.created",
            "schedule",
            schedule.id,
            {
                "conflict_detected": conflict_detected,
                "department": schedule.department,
                "assigned_to": schedule.assigned_to,
                "status": schedule.status,
            },
            **_actor_kwargs(data),
        )
        _emit_created(schedule, conflict_detected, data)
        return schedule, conflict_detected
    finally:
        db.close()


def create_recurring_schedule(data: dict[str, Any], occurrences: int = 3):
    db = SessionLocal()
    created = []
    try:
        first, first_conflict = _create_schedule_record(db, data)
        if data.get("sync_to_office365"):
            _sync_create(db, first)
        created.append((first, first_conflict))
        write_audit(
            "schedule.created",
            "schedule",
            first.id,
            {
                "recurring": True,
                "occurrence": 1,
                "department": first.department,
                "assigned_to": first.assigned_to,
                "status": first.status,
            },
            **_actor_kwargs(data),
        )
        _emit_created(first, first_conflict, data)

        if data.get("recurrence_rule") == "daily":
            for i in range(1, occurrences):
                shifted = data.copy()
                shifted["start_time"] = data["start_time"] + datetime.timedelta(days=i)
                shifted["end_time"] = data["end_time"] + datetime.timedelta(days=i)
                child, child_conflict = _create_schedule_record(db, shifted, parent_schedule_id=first.id)
                created.append((child, child_conflict))
                write_audit(
                    "schedule.created",
                    "schedule",
                    child.id,
                    {
                        "recurring": True,
                        "occurrence": i + 1,
                        "department": child.department,
                        "assigned_to": child.assigned_to,
                        "status": child.status,
                    },
                    **_actor_kwargs(shifted),
                )
                _emit_created(child, child_conflict, shifted)
        return created
    finally:
        db.close()


def update_schedule(schedule_id: str, data: dict[str, Any]):
    db = SessionLocal()
    try:
        query = db.query(Schedule).filter(Schedule.id == schedule_id)
        query = _apply_schedule_scope(
            query,
            data.get("actor_role"),
            data.get("actor_department"),
        )
        schedule = query.first()
        if not schedule:
            return None, False

        new_title = data.get("title", schedule.title)
        new_assigned_to = data.get("assigned_to", schedule.assigned_to)
        new_start = data.get("start_time", schedule.start_time)
        new_end = data.get("end_time", schedule.end_time)
        new_rule = data.get("recurrence_rule", schedule.recurrence_rule)
        conflict_detected = detect_conflict(
            new_assigned_to,
            new_start,
            new_end,
            exclude_schedule_id=schedule.id,
        )

        schedule.title = new_title
        schedule.assigned_to = new_assigned_to
        schedule.start_time = new_start
        schedule.end_time = new_end
        schedule.recurrence_rule = new_rule
        if data.get("department"):
            schedule.department = data["department"]
        schedule.status = "conflict" if conflict_detected else "scheduled"
        schedule.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(schedule)

        if schedule.office365_event_id:
            office365_adapter.update_event(schedule.office365_event_id, {"id": schedule.id, "title": schedule.title})

        write_audit(
            "schedule.updated",
            "schedule",
            schedule.id,
            {
                "conflict_detected": conflict_detected,
                "department": schedule.department,
                "assigned_to": schedule.assigned_to,
                "status": schedule.status,
            },
            **_actor_kwargs(data),
        )
        _emit_updated(schedule, conflict_detected, data)
        return schedule, conflict_detected
    finally:
        db.close()


def cancel_schedule(schedule_id: str, data: dict[str, Any] | None = None):
    data = data or {}
    db = SessionLocal()
    try:
        query = db.query(Schedule).filter(Schedule.id == schedule_id)
        query = _apply_schedule_scope(
            query,
            data.get("actor_role"),
            data.get("actor_department"),
        )
        schedule = query.first()
        if not schedule:
            return None
        schedule.status = "cancelled"
        schedule.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(schedule)

        if schedule.office365_event_id:
            office365_adapter.cancel_event(schedule.office365_event_id)

        write_audit(
            "schedule.cancelled",
            "schedule",
            schedule.id,
            {
                "department": schedule.department,
                "assigned_to": schedule.assigned_to,
                "status": schedule.status,
            },
            **_actor_kwargs(data),
        )
        _emit_cancelled(schedule, data)
        return schedule
    finally:
        db.close()


def resolve_conflict(schedule_id: str, strategy: str, data: dict[str, Any] | None = None):
    data = data or {}
    db = SessionLocal()
    try:
        query = db.query(Schedule).filter(Schedule.id == schedule_id)
        query = _apply_schedule_scope(
            query,
            data.get("actor_role"),
            data.get("actor_department"),
        )
        schedule = query.first()
        if not schedule:
            return None, False
        if strategy == "mark_conflict":
            schedule.status = "conflict"
        elif strategy == "cancel_new":
            schedule.status = "cancelled"
        elif strategy == "auto_shift_30m":
            schedule.start_time = schedule.start_time + datetime.timedelta(minutes=30)
            schedule.end_time = schedule.end_time + datetime.timedelta(minutes=30)
            schedule.status = (
                "scheduled"
                if not detect_conflict(
                    schedule.assigned_to,
                    schedule.start_time,
                    schedule.end_time,
                    exclude_schedule_id=schedule.id,
                )
                else "conflict"
            )
        else:
            return schedule, False
        schedule.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(schedule)
        write_audit(
            "schedule.conflict.resolved",
            "schedule",
            schedule.id,
            {"strategy": strategy, "status": schedule.status, "department": schedule.department},
            **_actor_kwargs(data),
        )
        event_bus.emit(
            "schedule.conflict.resolved",
            {
                "schedule_id": schedule.id,
                "strategy": strategy,
                "status": schedule.status,
                "department": schedule.department,
                **_actor_kwargs(data),
            },
        )
        return schedule, True
    finally:
        db.close()
