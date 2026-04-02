
from app.db.session import SessionLocal
from app.models.models import Schedule
from app.events.event_bus import event_bus
from app.adapters.office365_adapter import office365_adapter
from app.services.audit_service import write_audit
import datetime

def detect_conflict(assigned_to: str, start_time, end_time, exclude_schedule_id: str | None = None) -> bool:
    db = SessionLocal()
    try:
        query = db.query(Schedule).filter(
            Schedule.assigned_to == assigned_to,
            Schedule.status != "cancelled",
            Schedule.start_time < end_time,
            Schedule.end_time > start_time
        )
        if exclude_schedule_id:
            query = query.filter(Schedule.id != exclude_schedule_id)
        return query.first() is not None
    finally:
        db.close()

def _create_schedule_record(db, data: dict, parent_schedule_id: str | None = None):
    conflict_detected = detect_conflict(data["assigned_to"], data["start_time"], data["end_time"])
    schedule = Schedule(
        title=data["title"],
        assigned_to=data["assigned_to"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        status="conflict" if conflict_detected else "scheduled",
        source="local",
        recurrence_rule=data.get("recurrence_rule"),
        parent_schedule_id=parent_schedule_id
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule, conflict_detected

def _emit_created(schedule, conflict_detected: bool):
    event_bus.emit("schedule.created", {
        "schedule_id": schedule.id,
        "title": schedule.title,
        "assigned_to": schedule.assigned_to,
        "start_time": schedule.start_time.isoformat(),
        "end_time": schedule.end_time.isoformat(),
        "conflict_detected": conflict_detected,
        "status": schedule.status
    })

def _sync_create(db, schedule):
    result = office365_adapter.create_event({"id": schedule.id, "title": schedule.title, "assigned_to": schedule.assigned_to})
    if result.get("success"):
        schedule.synced_to_office365 = True
        schedule.office365_event_id = result.get("office365_event_id")
        db.commit()

def create_schedule(data: dict):
    db = SessionLocal()
    try:
        schedule, conflict_detected = _create_schedule_record(db, data)
        if data.get("sync_to_office365"):
            _sync_create(db, schedule)
        write_audit("schedule.created", "schedule", schedule.id, {"conflict_detected": conflict_detected})
        _emit_created(schedule, conflict_detected)
        return schedule, conflict_detected
    finally:
        db.close()

def create_recurring_schedule(data: dict, occurrences: int = 3):
    db = SessionLocal()
    created = []
    try:
        first, first_conflict = _create_schedule_record(db, data)
        if data.get("sync_to_office365"):
            _sync_create(db, first)
        created.append((first, first_conflict))
        write_audit("schedule.created", "schedule", first.id, {"recurring": True, "occurrence": 1})
        _emit_created(first, first_conflict)

        if data.get("recurrence_rule") == "daily":
            for i in range(1, occurrences):
                shifted = data.copy()
                shifted["start_time"] = data["start_time"] + datetime.timedelta(days=i)
                shifted["end_time"] = data["end_time"] + datetime.timedelta(days=i)
                child, child_conflict = _create_schedule_record(db, shifted, parent_schedule_id=first.id)
                created.append((child, child_conflict))
                write_audit("schedule.created", "schedule", child.id, {"recurring": True, "occurrence": i + 1})
                _emit_created(child, child_conflict)
        return created
    finally:
        db.close()

def update_schedule(schedule_id: str, data: dict):
    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return None, False
        new_title = data.get("title", schedule.title)
        new_assigned_to = data.get("assigned_to", schedule.assigned_to)
        new_start = data.get("start_time", schedule.start_time)
        new_end = data.get("end_time", schedule.end_time)
        new_rule = data.get("recurrence_rule", schedule.recurrence_rule)
        conflict_detected = detect_conflict(new_assigned_to, new_start, new_end, exclude_schedule_id=schedule.id)

        schedule.title = new_title
        schedule.assigned_to = new_assigned_to
        schedule.start_time = new_start
        schedule.end_time = new_end
        schedule.recurrence_rule = new_rule
        schedule.status = "conflict" if conflict_detected else "scheduled"
        schedule.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(schedule)

        if schedule.office365_event_id:
            office365_adapter.update_event(schedule.office365_event_id, {"id": schedule.id, "title": schedule.title})

        write_audit("schedule.updated", "schedule", schedule.id, {"conflict_detected": conflict_detected})
        event_bus.emit("schedule.updated", {
            "schedule_id": schedule.id,
            "assigned_to": schedule.assigned_to,
            "conflict_detected": conflict_detected,
            "status": schedule.status
        })
        return schedule, conflict_detected
    finally:
        db.close()

def cancel_schedule(schedule_id: str):
    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return None
        schedule.status = "cancelled"
        schedule.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(schedule)

        if schedule.office365_event_id:
            office365_adapter.cancel_event(schedule.office365_event_id)

        write_audit("schedule.cancelled", "schedule", schedule.id, {})
        event_bus.emit("schedule.cancelled", {
            "schedule_id": schedule.id,
            "assigned_to": schedule.assigned_to
        })
        return schedule
    finally:
        db.close()

def resolve_conflict(schedule_id: str, strategy: str):
    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return None, False
        if strategy == "mark_conflict":
            schedule.status = "conflict"
        elif strategy == "cancel_new":
            schedule.status = "cancelled"
        elif strategy == "auto_shift_30m":
            schedule.start_time = schedule.start_time + datetime.timedelta(minutes=30)
            schedule.end_time = schedule.end_time + datetime.timedelta(minutes=30)
            schedule.status = "scheduled" if not detect_conflict(schedule.assigned_to, schedule.start_time, schedule.end_time, exclude_schedule_id=schedule.id) else "conflict"
        else:
            return schedule, False
        schedule.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(schedule)
        write_audit("schedule.conflict.resolved", "schedule", schedule.id, {"strategy": strategy, "status": schedule.status})
        event_bus.emit("schedule.conflict.resolved", {"schedule_id": schedule.id, "strategy": strategy, "status": schedule.status})
        return schedule, True
    finally:
        db.close()
