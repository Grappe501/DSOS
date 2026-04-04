from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.api.schemas import HealthResponse, ScheduleCreate
from app.models.models import AuditLog, MaloneProposal, Schedule
from app.services.schedule_service import (
    cancel_schedule,
    create_schedule_draft,
    get_schedule_by_id,
    list_schedules,
)

api_router = APIRouter(prefix="/api")
router = api_router


def _serialize_dt(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    try:
        return value.isoformat()
    except Exception:
        return str(value)


def _coerce_meta(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value

    return value


def _serialize_audit_row(row: AuditLog) -> dict[str, Any]:
    return {
        "id": getattr(row, "id", None),
        "action": getattr(row, "action", None),
        "entity_type": getattr(row, "entity_type", None),
        "entity_id": getattr(row, "entity_id", None),
        "actor_user_id": getattr(row, "actor_user_id", None),
        "created_at": _serialize_dt(getattr(row, "created_at", None)),
        "meta_json": _coerce_meta(getattr(row, "meta_json", None)),
    }


def _serialize_schedule_row(row: Schedule) -> dict[str, Any]:
    return {
        "id": getattr(row, "id", None),
        "title": getattr(row, "title", None),
        "assigned_to": getattr(row, "assigned_to", None),
        "start_time": _serialize_dt(getattr(row, "start_time", None)),
        "end_time": _serialize_dt(getattr(row, "end_time", None)),
        "department": getattr(row, "department", None),
        "notes": getattr(row, "notes", None),
        "status": getattr(row, "status", None),
        "assigned_user_id": getattr(row, "assigned_user_id", None),
        "created_by_user_id": getattr(row, "created_by_user_id", None),
        "cancelled_by_user_id": getattr(row, "cancelled_by_user_id", None),
        "created_at": _serialize_dt(getattr(row, "created_at", None)),
        "updated_at": _serialize_dt(getattr(row, "updated_at", None)),
        "submitted_at": _serialize_dt(getattr(row, "submitted_at", None)),
        "approved_at": _serialize_dt(getattr(row, "approved_at", None)),
        "rejected_at": _serialize_dt(getattr(row, "rejected_at", None)),
        "cancelled_at": _serialize_dt(getattr(row, "cancelled_at", None)),
        "rejection_reason": getattr(row, "rejection_reason", None),
        "recurrence_rule": getattr(row, "recurrence_rule", None),
    }


def _normalize_assigned_to(payload: ScheduleCreate) -> str:
    """
    Schedules currently persist assigned_to as a non-null string.
    Keep compatibility with both assigned_to and assigned_user_id inputs.
    """
    raw_assigned_to = getattr(payload, "assigned_to", None)
    if raw_assigned_to is not None:
        text = str(raw_assigned_to).strip()
        if text:
            return text

    raw_assigned_user_id = getattr(payload, "assigned_user_id", None)
    if raw_assigned_user_id is not None:
        text = str(raw_assigned_user_id).strip()
        if text:
            return text

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="assigned_to is required",
    )


def _validate_schedule_times(start_time: datetime, end_time: datetime) -> None:
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be after start_time",
        )


def _serialize_recent_audit_rows(rows: list[AuditLog]) -> list[dict[str, Any]]:
    return [_serialize_audit_row(row) for row in rows]


@api_router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@api_router.get("/me")
def me(current=Depends(get_current_user)) -> dict[str, Any]:
    actor, role_name = current
    return {
        "id": actor.id,
        "email": actor.email,
        "full_name": getattr(actor, "full_name", None),
        "role": role_name,
        "department": getattr(actor, "department", None),
        "is_active": getattr(actor, "is_active", True),
    }


@api_router.get("/schedules")
def schedules_feed(
    department: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    actor, role_name = current
    rows = list_schedules(
        db,
        actor=actor,
        role_name=role_name,
        department=department,
    )
    return [_serialize_schedule_row(row) for row in rows]


@api_router.post("/schedules")
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin", "scheduler")),
) -> dict[str, Any]:
    actor, _role_name = current

    start_time = payload.start_time
    end_time = payload.end_time
    _validate_schedule_times(start_time, end_time)

    try:
        row = create_schedule_draft(
            db,
            payload={
                "title": payload.title,
                "assigned_to": _normalize_assigned_to(payload),
                "start_time": start_time,
                "end_time": end_time,
                "department": payload.department,
                "recurrence_rule": payload.recurrence_rule,
                "status": "scheduled",
            },
            actor=actor,
        )

        return {
            "schedule_id": row.id,
            "schedule": _serialize_schedule_row(row),
            "message": "Schedule created",
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {exc}",
        ) from exc


@api_router.post("/schedules/{schedule_id}/cancel")
def cancel_schedule_endpoint(
    schedule_id: str,
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin", "scheduler")),
) -> dict[str, Any]:
    actor, role_name = current
    row = get_schedule_by_id(
        db,
        schedule_id=schedule_id,
        actor=actor,
        role_name=role_name,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Schedule not found")

    try:
        row = cancel_schedule(
            db,
            schedule=row,
            actor=actor,
        )

        return {
            "schedule_id": row.id,
            "schedule": _serialize_schedule_row(row),
            "message": "Schedule cancelled",
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel schedule: {exc}",
        ) from exc


@api_router.get("/audit")
def list_audit(
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    actor_user_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> list[dict[str, Any]]:
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if actor_user_id:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)

    rows = query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return _serialize_recent_audit_rows(rows)


@api_router.get("/operational/summary")
def operational_summary(
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> dict[str, Any]:
    total_schedules = db.query(Schedule).count()
    total_audit_rows = db.query(AuditLog).count()
    total_malone_proposals = db.query(MaloneProposal).count()

    workflows = db.query(AuditLog).filter(AuditLog.action == "state_transition").count()
    messages = db.query(AuditLog).filter(AuditLog.entity_type == "message").count()
    events = db.query(AuditLog).filter(AuditLog.entity_type == "event").count()
    malone_audit_rows = db.query(AuditLog).filter(AuditLog.entity_type == "malone_proposal").count()

    recent_rows = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "totals": {
            "schedules": total_schedules,
            "workflows": workflows,
            "messages": messages,
            "events": events,
            "audit_rows": total_audit_rows,
            "malone_proposals": total_malone_proposals,
            "malone_audit_rows": malone_audit_rows,
        },
        "recent_activity": _serialize_recent_audit_rows(recent_rows),
    }


@api_router.get("/workflows")
def list_workflows_endpoint(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    rows = (
        db.query(AuditLog)
        .filter(AuditLog.action == "state_transition")
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )
    return _serialize_recent_audit_rows(rows)


@api_router.get("/messages")
def list_messages(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    rows = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == "message")
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )
    return _serialize_recent_audit_rows(rows)


@api_router.get("/events")
def list_events(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    rows = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == "event")
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )
    return _serialize_recent_audit_rows(rows)
