from app.db.session import SessionLocal
from app.models.models import Task
from app.events.event_bus import event_bus
from app.services.audit_service import log_write_action


def create_task(data: dict):
    db = SessionLocal()
    try:
        task = Task(type=data["type"], assigned_to=data["assigned_to"])
        db.add(task)
        db.commit()
        db.refresh(task)

        log_write_action(
            db,
            action="task.created",
            entity_type="task",
            entity_id=task.id,
            actor=None,
            meta_json={"assigned_to": task.assigned_to},
        )

        event_bus.emit("task.created", {"task_id": task.id})

        return task

    finally:
        db.close()