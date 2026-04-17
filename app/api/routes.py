from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.api.schemas import (
    ApprovalResolveRequest,
    ClarificationResolveRequest,
    HealthResponse,
    ScheduleCreate,
)
from app.models.models import (
    AuditLog,
    ClarificationRequest,
    MaloneProposal,
    Schedule,
)
from app.services.approval_service import (
    get_approval_request,
    list_approval_requests,
    resolve_approval_request,
    serialize_approval_request,
)
from app.services.clarification_service import (
    get_clarification_request,
    list_clarification_requests,
    resolve_clarification_request,
    serialize_clarification_request,
)
from app.services.schedule_service import (
    cancel_schedule,
    create_schedule_draft,
    get_schedule_by_id,
    list_schedules,
)
from app.services.workflow_service import (
    get_workflow_instance,
    list_workflow_definitions,
    list_workflow_handlers,
    list_workflow_instances,
    resume_workflow_instance,
    serialize_workflow_definition,
    serialize_workflow_instance,
    start_workflow_instance,
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


def _serialize_recent_audit_rows(rows: list[AuditLog]) -> list[dict[str, Any]]:
    return [_serialize_audit_row(row) for row in rows]


def _normalize_assigned_to(payload: ScheduleCreate) -> str:
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


def _get_actor_payload(actor: Any, role_name: str) -> dict[str, Any]:
    return {
        "id": getattr(actor, "id", None),
        "email": getattr(actor, "email", None),
        "role": role_name,
        "department": getattr(actor, "department", None),
    }


def _require_json_object(payload: Any, *, field_name: str = "payload") -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be an object",
        )
    return payload


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

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
    total_approvals = db.query(
        db.get_bind().execute  # type: ignore[attr-defined]
    ) if False else db.query  # no-op to avoid unused import style drift

    approval_count = db.query(MaloneProposal).filter(MaloneProposal.id == MaloneProposal.id).count()
    total_approvals = db.query(
        __import__("app.models.models", fromlist=["ApprovalRequest"]).ApprovalRequest
    ).count()
    total_clarifications = db.query(ClarificationRequest).count()

    workflows = db.query(AuditLog).filter(AuditLog.action == "state_transition").count()
    messages = db.query(AuditLog).filter(AuditLog.entity_type == "message").count()
    events = db.query(AuditLog).filter(AuditLog.entity_type == "event").count()
    malone_audit_rows = db.query(AuditLog).filter(AuditLog.entity_type == "malone_proposal").count()
    deterministic_audit_rows = db.query(AuditLog).filter(AuditLog.entity_type == "deterministic_action").count()
    pending_approvals = db.query(
        __import__("app.models.models", fromlist=["ApprovalRequest"]).ApprovalRequest
    ).filter_by(status="pending").count()
    pending_clarifications = db.query(ClarificationRequest).filter_by(status="pending").count()

    recent_rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()

    return {
        "totals": {
            "schedules": total_schedules,
            "workflows": workflows,
            "messages": messages,
            "events": events,
            "audit_rows": total_audit_rows,
            "malone_proposals": total_malone_proposals,
            "malone_audit_rows": malone_audit_rows,
            "deterministic_audit_rows": deterministic_audit_rows,
            "approval_requests": total_approvals,
            "pending_approvals": pending_approvals,
            "clarification_requests": total_clarifications,
            "pending_clarifications": pending_clarifications,
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


@api_router.get("/workflow-definitions")
def workflow_definitions_endpoint(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    return [serialize_workflow_definition(row, db=db) for row in list_workflow_definitions(db)]


@api_router.get("/workflow-handlers")
def workflow_handlers_endpoint(
    current=Depends(get_current_user),
) -> dict[str, Any]:
    return {"handlers": list_workflow_handlers()}


@api_router.get("/workflow-instances")
def workflow_instances_endpoint(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    return [serialize_workflow_instance(row, db=db) for row in list_workflow_instances(db, limit=limit)]


@api_router.get("/workflow-instances/{workflow_instance_id}")
def workflow_instance_detail_endpoint(
    workflow_instance_id: str,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> dict[str, Any]:
    row = get_workflow_instance(db, workflow_instance_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow instance not found")
    return serialize_workflow_instance(row, db=db)


@api_router.post("/workflows/start")
def start_workflow_endpoint(
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> dict[str, Any]:
    actor, role_name = current
    payload = _require_json_object(payload)

    workflow_name = str(payload.get("workflow_name") or "").strip()
    if not workflow_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="workflow_name is required",
        )

    context = payload.get("context") or {}
    if not isinstance(context, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="context must be an object",
        )

    context.setdefault("actor", _get_actor_payload(actor, role_name))
    context.setdefault("role_name", role_name)

    instance = start_workflow_instance(
        db,
        workflow_name=workflow_name,
        context=context,
        entity_type=payload.get("entity_type"),
        entity_id=payload.get("entity_id"),
        version=payload.get("version"),
        auto_run=bool(payload.get("auto_run", True)),
    )
    return {"workflow_instance": serialize_workflow_instance(instance, db=db)}


@api_router.post("/workflow-instances/{workflow_instance_id}/resume")
def resume_workflow_endpoint(
    workflow_instance_id: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> dict[str, Any]:
    payload = _require_json_object(payload)
    context_updates = payload.get("context_updates") or {}
    if not isinstance(context_updates, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="context_updates must be an object",
        )

    try:
        instance = resume_workflow_instance(
            db,
            workflow_instance_id=workflow_instance_id,
            context_updates=context_updates,
        )
        return {"workflow_instance": serialize_workflow_instance(instance, db=db)}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@api_router.get("/approvals")
def list_approvals_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    required_role: str | None = Query(default=None),
    workflow_instance_id: str | None = Query(default=None),
    department: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> list[dict[str, Any]]:
    rows = list_approval_requests(
        db,
        status=status_filter,
        required_role=required_role,
        workflow_instance_id=workflow_instance_id,
        department=department,
        limit=limit,
    )
    return [serialize_approval_request(row) for row in rows]


@api_router.get("/approvals/{approval_id}")
def approval_detail_endpoint(
    approval_id: str,
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
) -> dict[str, Any]:
    row = get_approval_request(db, approval_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    return serialize_approval_request(row)


@api_router.post("/approvals/{approval_id}/resolve")
def resolve_approval_endpoint(
    approval_id: str,
    payload: ApprovalResolveRequest,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> dict[str, Any]:
    actor, role_name = current

    row = get_approval_request(db, approval_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")

    try:
        resolved = resolve_approval_request(
            db,
            approval_request=row,
            actor={
                "id": getattr(actor, "id", None),
                "email": getattr(actor, "email", None),
                "role": role_name,
                "department": getattr(actor, "department", None),
            },
            actor_role=role_name,
            approved=payload.approved,
            reason=payload.reason,
        )
        instance = get_workflow_instance(db, resolved.workflow_instance_id)
        return {
            "approval": serialize_approval_request(resolved),
            "workflow_instance": serialize_workflow_instance(instance, db=db) if instance else None,
            "message": "Approval resolved",
        }
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve approval: {exc}",
        ) from exc


@api_router.get("/clarifications")
def list_clarifications_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    workflow_instance_id: str | None = Query(default=None),
    department: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> list[dict[str, Any]]:
    rows = list_clarification_requests(
        db,
        status=status_filter,
        workflow_instance_id=workflow_instance_id,
        department=department,
        limit=limit,
    )
    return [serialize_clarification_request(row) for row in rows]


@api_router.get("/clarifications/{clarification_id}")
def clarification_detail_endpoint(
    clarification_id: str,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> dict[str, Any]:
    row = get_clarification_request(db, clarification_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clarification not found")
    return serialize_clarification_request(row)


@api_router.post("/clarifications/{clarification_id}/resolve")
def resolve_clarification_endpoint(
    clarification_id: str,
    payload: ClarificationResolveRequest,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
) -> dict[str, Any]:
    actor, role_name = current

    row = get_clarification_request(db, clarification_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clarification not found")

    try:
        resolved = resolve_clarification_request(
            db,
            clarification_request=row,
            actor={
                "id": getattr(actor, "id", None),
                "email": getattr(actor, "email", None),
                "role": role_name,
                "department": getattr(actor, "department", None),
            },
            response_payload=payload.response,
            resolution_note=payload.resolution_note,
        )
        instance = get_workflow_instance(db, resolved.workflow_instance_id)
        return {
            "clarification": serialize_clarification_request(resolved),
            "workflow_instance": serialize_workflow_instance(instance, db=db) if instance else None,
            "message": "Clarification resolved",
        }
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve clarification: {exc}",
        ) from exc


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