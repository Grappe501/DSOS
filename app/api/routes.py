from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.api.schemas import HealthResponse
from app.models.models import AuditLog, Schedule


api_router = APIRouter(prefix="/api")
router = api_router


def _serialize_dt(value):
    return value.isoformat() if value is not None else None


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
        "id": row.id,
        "action": row.action,
        "entity_type": row.entity_type,
        "entity_id": getattr(row, "entity_id", None),
        "actor_user_id": getattr(row, "actor_user_id", None),
        "created_at": _serialize_dt(getattr(row, "created_at", None)),
        "meta_json": _coerce_meta(getattr(row, "meta_json", None)),
    }


@api_router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@api_router.get("/me")
def me(current=Depends(get_current_user)) -> dict[str, Any]:
    user, role_name = current
    return {
        "id": user.id,
        "email": user.email,
        "full_name": getattr(user, "full_name", None),
        "role": role_name,
        "department": getattr(user, "department", None),
        "department_id": getattr(user, "department_id", None),
        "is_active": getattr(user, "is_active", True),
    }


@api_router.get("/schedules")
def list_schedules(
    department: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    user, role_name = current
    query = db.query(Schedule)

    user_department = getattr(user, "department", None)

    if role_name not in {"owner", "admin"} and user_department:
        query = query.filter(Schedule.department == user_department)

    if department and (role_name in {"owner", "admin"} or department == user_department):
        query = query.filter(Schedule.department == department)

    rows = query.order_by(Schedule.start_time.desc()).all()

    return [
        {
            "id": row.id,
            "title": row.title,
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
        }
        for row in rows
    ]


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
    return [_serialize_audit_row(row) for row in rows]


@api_router.get("/operational/summary")
def operational_summary(
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> dict[str, Any]:
    total_schedules = db.query(Schedule).count()
    total_audit_rows = db.query(AuditLog).count()

    workflows = db.query(AuditLog).filter(AuditLog.action == "state_transition").count()
    messages = db.query(AuditLog).filter(AuditLog.entity_type == "message").count()
    events = db.query(AuditLog).filter(AuditLog.entity_type == "event").count()

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
        },
        "recent_activity": [_serialize_audit_row(row) for row in recent_rows],
    }


@api_router.get("/workflows")
def list_workflows(
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
    return [_serialize_audit_row(row) for row in rows]


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
    return [_serialize_audit_row(row) for row in rows]


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
    return [_serialize_audit_row(row) for row in rows]