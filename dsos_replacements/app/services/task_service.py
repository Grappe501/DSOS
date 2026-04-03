from __future__ import annotations

from typing import Any

from app.db.session import SessionLocal
from app.events.event_bus import event_bus
from app.models.models import Task
from app.services.audit_service import write_audit


def create_task(data: dict[str, Any]) -> Task:
    db = SessionLocal()
    try:
        task = Task(type=data["type"], assigned_to=data["assigned_to"])
        db.add(task)
        db.commit()
        db.refresh(task)

        write_audit(
            "task.created",
            "task",
            task.id,
            {
                "assigned_to": task.assigned_to,
                "department": data.get("department"),
            },
            actor_user_id=data.get("actor_user_id"),
            actor_email=data.get("actor_email"),
            actor_role=data.get("actor_role"),
            actor_department=data.get("actor_department") or data.get("department"),
        )
        event_bus.emit(
            "task.created",
            {
                "task_id": task.id,
                "assigned_to": task.assigned_to,
                "department": data.get("department"),
            },
        )
        return task
    finally:
        db.close()
