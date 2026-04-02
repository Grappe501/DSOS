
from app.db.session import SessionLocal
from app.models.models import Task
from app.events.event_bus import event_bus
from app.services.audit_service import write_audit

def create_task(data: dict) -> Task:
    db = SessionLocal()
    try:
        task = Task(type=data["type"], assigned_to=data["assigned_to"])
        db.add(task)
        db.commit()
        db.refresh(task)
        write_audit("task.created", "task", task.id, {"assigned_to": task.assigned_to})
        event_bus.emit("task.created", {"task_id": task.id, "assigned_to": task.assigned_to})
        return task
    finally:
        db.close()
