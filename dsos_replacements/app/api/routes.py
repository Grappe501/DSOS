from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.api.schemas import (
    CancelResponse,
    ConflictResolutionRequest,
    QueueMessageRequest,
    ScheduleCreateRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
    TaskCreateRequest,
    TaskCreateResponse,
)
from app.models.models import AuditLog, EventLog, MessageQueue, Reminder, Schedule, WorkflowState
from app.services.audit_service import parse_meta_json
from app.services.messaging_service import queue_message
from app.services.schedule_service import (
    cancel_schedule,
    create_recurring_schedule,
    create_schedule,
    resolve_conflict,
    update_schedule,
)
from app.services.task_service import create_task
from app.utils.logger import log

router = APIRouter()
api_router = APIRouter(prefix="/api", tags=["api"])
GLOBAL_ROLES = {"owner", "admin"}


def _server_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail,
    )


def _actor_payload(user, role_name: str) -> dict[str, Any]:
    return {
        "actor_user_id": user.id,
        "actor_email": user.email,
        "actor_role": role_name,
        "actor_department": user.department,
    }


def _resolve_department_scope(
    requested_department: str | None,
    user,
    role_name: str,
) -> str | None:
    if role_name in GLOBAL_ROLES:
        return requested_department or user.department
    return user.department


def _apply_schedule_scope(query, user, role_name: str):
    if role_name in GLOBAL_ROLES:
        return query
    if user.department:
        return query.filter(Schedule.department == user.department)
    return query.filter(Schedule.department.is_(None))


def _serialize_event(row: EventLog) -> dict[str, Any]:
    return {
        "id": row.id,
        "event_type": row.event_type,
        "payload": row.payload,
        "created_at": row.created_at.isoformat(),
    }


def _serialize_audit(row: AuditLog) -> dict[str, Any]:
    metadata = parse_meta_json(row.meta_json)
    return {
        "id": row.id,
        "action": row.action,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "actor_user_id": row.actor_user_id,
        "actor_email": metadata.get("actor_email"),
        "actor_role": metadata.get("actor_role"),
        "actor_department": metadata.get("actor_department"),
        "department": metadata.get("department") or metadata.get("actor_department"),
        "metadata": metadata,
        "created_at": row.created_at.isoformat(),
    }


def _serialize_schedule(row: Schedule) -> dict[str, Any]:
    return {
        "id": row.id,
        "title": row.title,
        "assigned_to": row.assigned_to,
        "start_time": row.start_time.isoformat(),
        "end_time": row.end_time.isoformat(),
        "status": row.status,
        "recurrence_rule": row.recurrence_rule,
        "parent_schedule_id": row.parent_schedule_id,
        "synced_to_office365": row.synced_to_office365,
        "office365_event_id": row.office365_event_id,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
        "department": row.department,
        "created_by_user_id": row.created_by_user_id,
    }


def _serialize_reminder(row: Reminder) -> dict[str, Any]:
    return {
        "id": row.id,
        "task_id": row.task_id,
        "schedule_id": row.schedule_id,
        "trigger_time": row.trigger_time.isoformat(),
        "status": row.status,
        "message": row.message,
        "created_at": row.created_at.isoformat(),
    }


def _serialize_workflow(row: WorkflowState) -> dict[str, Any]:
    return {
        "id": row.id,
        "workflow_name": row.workflow_name,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "state": row.state,
        "status": row.status,
        "metadata": parse_meta_json(row.meta_json),
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
    }


def _serialize_message(row: MessageQueue) -> dict[str, Any]:
    return {
        "id": row.id,
        "channel": row.channel,
        "recipient": row.recipient,
        "content": row.content,
        "status": row.status,
        "retry_count": row.retry_count,
        "max_retries": row.max_retries,
        "last_error": row.last_error,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
    }


@router.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <html>
      <head><title>AllCare Pharmacy Runtime</title></head>
      <body style="font-family: Arial, sans-serif; max-width: 1000px; margin: 40px auto; line-height: 1.5;">
        <h1>AllCare Pharmacy Runtime</h1>
        <p>Backend is running.</p>
        <ul>
          <li><a href="/docs">Swagger UI</a></li>
          <li><a href="/health">Health</a></li>
          <li><a href="/api/health">API Health</a></li>
          <li><a href="/api/auth/me">API Me</a></li>
          <li><a href="/api/schedules">API Schedules</a></li>
          <li><a href="/api/events">API Events</a></li>
          <li><a href="/api/audit">API Audit</a></li>
          <li><a href="/api/workflows">API Workflows</a></li>
          <li><a href="/api/messages">API Messages</a></li>
          <li><a href="/api/reminders">API Reminders</a></li>
        </ul>
      </body>
    </html>
    """


@api_router.get("/health")
def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "allcare-pharmacy-runtime"}


@api_router.get("/operational/summary")
def get_operational_summary(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> dict[str, Any]:
    try:
        user, role_name = current
        schedule_query = _apply_schedule_scope(db.query(Schedule), user, role_name)
        schedules = schedule_query.all()
        workflows = db.query(WorkflowState).count()
        events = db.query(EventLog).count()
        summary = {
            "role": role_name,
            "department": user.department,
            "schedules_total": len(schedules),
            "scheduled_count": sum(1 for row in schedules if row.status == "scheduled"),
            "conflict_count": sum(1 for row in schedules if row.status == "conflict"),
            "cancelled_count": sum(1 for row in schedules if row.status == "cancelled"),
            "department_breakdown": {},
            "workflow_count": workflows,
            "event_count": events,
        }
        if role_name in GLOBAL_ROLES:
            summary["audit_count"] = db.query(AuditLog).count()
            summary["message_count"] = db.query(MessageQueue).count()

        for row in schedules:
            key = row.department or "unscoped"
            summary["department_breakdown"][key] = summary["department_breakdown"].get(key, 0) + 1
        return summary
    except Exception as exc:
        log(f"Operational summary failed: {exc}")
        raise _server_error("Operational summary failed")


@api_router.post("/tasks/create", response_model=TaskCreateResponse)
def create_task_json(
    data: TaskCreateRequest,
    current=Depends(require_roles("owner", "admin", "scheduler")),
) -> dict[str, str]:
    try:
        user, role_name = current
        payload = data.model_dump()
        payload["department"] = _resolve_department_scope(payload.get("department"), user, role_name)
        payload.update(_actor_payload(user, role_name))
        task = create_task(payload)
        return {"task_id": task.id, "status": task.status}
    except Exception as exc:
        log(f"Task creation failed: {exc}")
        raise _server_error("Task creation failed")


@api_router.post("/schedules/create", response_model=ScheduleResponse)
def create_schedule_json(
    data: ScheduleCreateRequest,
    current=Depends(require_roles("owner", "admin", "scheduler")),
) -> dict[str, Any]:
    try:
        payload = data.model_dump()
        user, role_name = current
        payload["created_by_user_id"] = user.id
        payload["department"] = _resolve_department_scope(payload.get("department"), user, role_name)
        payload.update(_actor_payload(user, role_name))

        recurrence_rule = payload.get("recurrence_rule")
        if recurrence_rule:
            created = create_recurring_schedule(payload)
            if not created:
                raise _server_error("Recurring schedule creation returned no results")
            first, first_conflict = created[0]
            return {
                "schedule_id": first.id,
                "status": first.status,
                "conflict_detected": first_conflict,
            }

        schedule, conflict_detected = create_schedule(payload)
        return {
            "schedule_id": schedule.id,
            "status": schedule.status,
            "conflict_detected": conflict_detected,
        }
    except HTTPException:
        raise
    except Exception as exc:
        log(f"Schedule creation failed: {exc}")
        raise _server_error("Schedule creation failed")


@api_router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def update_schedule_json(
    schedule_id: str,
    data: ScheduleUpdateRequest,
    current=Depends(require_roles("owner", "admin", "scheduler")),
) -> dict[str, Any]:
    try:
        user, role_name = current
        payload = data.model_dump(exclude_none=True)
        if "department" in payload:
            payload["department"] = _resolve_department_scope(payload.get("department"), user, role_name)
        payload.update(_actor_payload(user, role_name))
        schedule, conflict_detected = update_schedule(schedule_id, payload)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found",
            )
        return {
            "schedule_id": schedule.id,
            "status": schedule.status,
            "conflict_detected": conflict_detected,
        }
    except HTTPException:
        raise
    except Exception as exc:
        log(f"Schedule update failed: {exc}")
        raise _server_error("Schedule update failed")


@api_router.post("/schedules/{schedule_id}/cancel", response_model=CancelResponse)
def cancel_schedule_json(
    schedule_id: str,
    current=Depends(require_roles("owner", "admin", "scheduler")),
) -> dict[str, str]:
    try:
        user, role_name = current
        schedule = cancel_schedule(schedule_id, _actor_payload(user, role_name))
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found",
            )
        return {"schedule_id": schedule.id, "status": schedule.status}
    except HTTPException:
        raise
    except Exception as exc:
        log(f"Schedule cancel failed: {exc}")
        raise _server_error("Schedule cancel failed")


@api_router.post("/schedules/{schedule_id}/resolve-conflict")
def resolve_conflict_json(
    schedule_id: str,
    data: ConflictResolutionRequest,
    current=Depends(require_roles("owner", "admin")),
) -> dict[str, Any]:
    try:
        user, role_name = current
        schedule, ok = resolve_conflict(schedule_id, data.strategy, _actor_payload(user, role_name))
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found",
            )
        return {
            "schedule_id": schedule.id,
            "status": schedule.status,
            "resolution_applied": ok,
        }
    except HTTPException:
        raise
    except Exception as exc:
        log(f"Conflict resolution failed: {exc}")
        raise _server_error("Conflict resolution failed")


@api_router.post("/messages/queue")
def queue_message_json(
    data: QueueMessageRequest,
    current=Depends(require_roles("owner", "admin")),
) -> dict[str, str]:
    try:
        user, role_name = current
        department = _resolve_department_scope(data.department, user, role_name)
        item = queue_message(
            recipient=data.recipient,
            content=data.content,
            channel=data.channel,
            actor_user_id=user.id,
            actor_email=user.email,
            actor_role=role_name,
            actor_department=user.department,
            department=department,
        )
        return {"message_id": item.id, "status": item.status}
    except Exception as exc:
        log(f"Message queue failed: {exc}")
        raise _server_error("Message queue failed")


@api_router.get("/events")
def list_events(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    try:
        rows = db.query(EventLog).order_by(EventLog.created_at.desc()).all()
        return [_serialize_event(row) for row in rows]
    except Exception as exc:
        log(f"Event query failed: {exc}")
        raise _server_error("Event query failed")


@api_router.get("/audit")
def list_audit(
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    actor_user_id: str | None = Query(default=None),
    department: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> list[dict[str, Any]]:
    try:
        _user, _role_name = current
        query = db.query(AuditLog)
        if action:
            query = query.filter(AuditLog.action == action)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if actor_user_id:
            query = query.filter(AuditLog.actor_user_id == actor_user_id)

        rows = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
        serialized = [_serialize_audit(row) for row in rows]
        if department:
            serialized = [
                row
                for row in serialized
                if (row.get("department") or "") == department
            ]
        return serialized
    except Exception as exc:
        log(f"Audit query failed: {exc}")
        raise _server_error("Audit query failed")


@api_router.get("/schedules")
def list_schedules(
    status: str | None = Query(default=None),
    assigned_to: str | None = Query(default=None),
    department: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    try:
        user, role_name = current
        query = _apply_schedule_scope(db.query(Schedule), user, role_name)

        if status:
            query = query.filter(Schedule.status == status)
        if assigned_to:
            query = query.filter(Schedule.assigned_to == assigned_to)
        if department and role_name in GLOBAL_ROLES:
            query = query.filter(Schedule.department == department)

        rows = query.order_by(Schedule.created_at.desc()).all()
        return [_serialize_schedule(row) for row in rows]
    except Exception as exc:
        log(f"Schedule query failed: {exc}")
        raise _server_error("Schedule query failed")


@api_router.get("/reminders")
def list_reminders(
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    try:
        query = db.query(Reminder)
        if status:
            query = query.filter(Reminder.status == status)
        rows = query.order_by(Reminder.created_at.desc()).all()
        return [_serialize_reminder(row) for row in rows]
    except Exception as exc:
        log(f"Reminder query failed: {exc}")
        raise _server_error("Reminder query failed")


@api_router.get("/workflows")
def list_workflows(
    status: str | None = Query(default=None),
    workflow_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    try:
        query = db.query(WorkflowState)
        if status:
            query = query.filter(WorkflowState.status == status)
        if workflow_name:
            query = query.filter(WorkflowState.workflow_name == workflow_name)
        rows = query.order_by(WorkflowState.updated_at.desc()).all()
        return [_serialize_workflow(row) for row in rows]
    except Exception as exc:
        log(f"Workflow query failed: {exc}")
        raise _server_error("Workflow query failed")


@api_router.get("/messages")
def list_messages(
    status: str | None = Query(default=None),
    channel: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> list[dict[str, Any]]:
    try:
        query = db.query(MessageQueue)
        if status:
            query = query.filter(MessageQueue.status == status)
        if channel:
            query = query.filter(MessageQueue.channel == channel)
        rows = query.order_by(MessageQueue.created_at.desc()).all()
        return [_serialize_message(row) for row in rows]
    except Exception as exc:
        log(f"Message query failed: {exc}")
        raise _server_error("Message query failed")
