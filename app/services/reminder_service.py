
from app.db.session import SessionLocal
from app.models.models import Reminder, Schedule
from app.events.event_bus import event_bus
from app.services.audit_service import write_audit
import datetime

def schedule_task_reminder(task_id: str) -> Reminder:
    db = SessionLocal()
    try:
        reminder = Reminder(
            task_id=task_id,
            trigger_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=10),
            status="scheduled",
            message=f"Task {task_id} reminder"
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        write_audit("reminder.created", "reminder", reminder.id, {"task_id": task_id})
        return reminder
    finally:
        db.close()

def schedule_schedule_reminder(schedule_id: str) -> Reminder | None:
    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule or schedule.status == "cancelled":
            return None
        trigger_time = schedule.start_time - datetime.timedelta(minutes=15)
        if trigger_time < datetime.datetime.utcnow():
            trigger_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        reminder = Reminder(
            schedule_id=schedule_id,
            trigger_time=trigger_time,
            status="scheduled",
            message=f"Upcoming schedule: {schedule.title} for {schedule.assigned_to}"
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        write_audit("reminder.created", "reminder", reminder.id, {"schedule_id": schedule_id})
        return reminder
    finally:
        db.close()

def cancel_schedule_reminders(schedule_id: str) -> int:
    db = SessionLocal()
    try:
        reminders = db.query(Reminder).filter(
            Reminder.schedule_id == schedule_id,
            Reminder.status == "scheduled"
        ).all()
        count = 0
        for reminder in reminders:
            reminder.status = "cancelled"
            count += 1
        db.commit()
        if count:
            write_audit("reminder.cancelled", "schedule", schedule_id, {"count": count})
        return count
    finally:
        db.close()

def process_due_reminders() -> int:
    db = SessionLocal()
    try:
        now = datetime.datetime.utcnow()
        due = db.query(Reminder).filter(
            Reminder.status == "scheduled",
            Reminder.trigger_time <= now
        ).all()
        count = 0
        for reminder in due:
            reminder.status = "triggered"
            db.commit()
            payload = {
                "reminder_id": reminder.id,
                "task_id": reminder.task_id,
                "schedule_id": reminder.schedule_id,
                "message": reminder.message,
                "channel": reminder.channel,
                "recipient": "system"
            }
            event_bus.emit("reminder.triggered", payload)
            count += 1
        return count
    finally:
        db.close()
