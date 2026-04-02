
from app.events.event_bus import event_bus
from app.services.reminder_service import schedule_task_reminder, schedule_schedule_reminder, cancel_schedule_reminders
from app.services.messaging_service import send_message
from app.services.workflow_service import start_schedule_workflow, route_conflict_resolution, mark_workflow_state
from app.utils.logger import log

def notify_conflict(payload: dict) -> None:
    send_message({
        "message": f"Conflict detected for {payload['assigned_to']} on schedule {payload['schedule_id']}",
        "recipient": payload["assigned_to"],
        "channel": "in_app"
    })

def wire_events() -> None:
    event_bus.subscribe("task.created", lambda payload: schedule_task_reminder(payload["task_id"]))
    event_bus.subscribe("reminder.triggered", send_message)

    event_bus.subscribe("schedule.created", start_schedule_workflow)
    event_bus.subscribe("schedule.created", route_conflict_resolution)
    event_bus.subscribe("workflow.started", lambda payload: (
        mark_workflow_state(payload["schedule_id"], "workflow_started", payload),
        schedule_schedule_reminder(payload["schedule_id"])
    ))
    event_bus.subscribe("schedule.updated", lambda payload: (
        mark_workflow_state(payload["schedule_id"], "schedule_updated", payload),
        schedule_schedule_reminder(payload["schedule_id"]) if not payload["conflict_detected"] else None
    ))
    event_bus.subscribe("schedule.cancelled", lambda payload: (
        mark_workflow_state(payload["schedule_id"], "cancelled", payload),
        cancel_schedule_reminders(payload["schedule_id"])
    ))
    event_bus.subscribe("schedule.conflict.detected", lambda payload: (
        mark_workflow_state(payload["schedule_id"], "conflict_detected", payload),
        notify_conflict(payload)
    ))
    event_bus.subscribe("schedule.conflict.resolved", lambda payload: mark_workflow_state(payload["schedule_id"], "conflict_resolved", payload))

    log("Event wiring complete")
