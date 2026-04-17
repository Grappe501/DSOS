from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.models import ClarificationRequest, WorkflowInstance
from app.services.audit_service import write_audit
from app.services.workflow_service import resume_workflow_instance
from app.services.workflows.constants import (
    CLARIFICATION_ENTITY_TYPE,
    CLARIFICATION_STATUS_CANCELLED,
    CLARIFICATION_STATUS_PENDING,
    CLARIFICATION_STATUS_RESOLVED,
)
from app.services.workflows.json_utils import (
    actor_id,
    coerce_json,
    extract_actor_from_nested_context,
    normalize_str,
    normalize_string_list,
    safe_json,
    utcnow,
)


def _normalize_prompt(prompt: str | None, *, fields: list[str] | None = None) -> str:
    normalized = normalize_str(prompt)
    if normalized:
        return normalized

    normalized_fields = normalize_string_list(fields or [])
    if normalized_fields:
        return f"Please provide clarification for: {', '.join(normalized_fields)}."

    return "Please clarify your request."


def _normalize_resolution_note(note: str | None) -> str | None:
    return normalize_str(note)


def _normalize_clarification_id(clarification_id: str | None) -> str | None:
    return normalize_str(clarification_id)


def _find_existing_pending_request(
    db: Session,
    *,
    workflow_instance_id: str,
) -> ClarificationRequest | None:
    return (
        db.query(ClarificationRequest)
        .filter(
            ClarificationRequest.workflow_instance_id == workflow_instance_id,
            ClarificationRequest.status == CLARIFICATION_STATUS_PENDING,
        )
        .order_by(ClarificationRequest.created_at.desc())
        .first()
    )


def serialize_clarification_request(row: ClarificationRequest) -> dict[str, Any]:
    return {
        "id": row.id,
        "workflow_instance_id": row.workflow_instance_id,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "status": row.status,
        "department": row.department,
        "requested_by_user_id": row.requested_by_user_id,
        "resolved_by_user_id": row.resolved_by_user_id,
        "prompt": row.prompt,
        "fields_json": coerce_json(row.fields_json),
        "context_json": coerce_json(row.context_json),
        "response_json": coerce_json(row.response_json),
        "resolution_note": row.resolution_note,
        "resolved_at": row.resolved_at.isoformat() if row.resolved_at else None,
        "created_at": row.created_at.isoformat() if getattr(row, "created_at", None) else None,
        "updated_at": row.updated_at.isoformat() if getattr(row, "updated_at", None) else None,
    }


def get_clarification_request(
    db: Session,
    clarification_id: str,
) -> ClarificationRequest | None:
    normalized_id = _normalize_clarification_id(clarification_id)
    if not normalized_id:
        return None

    return (
        db.query(ClarificationRequest)
        .filter(ClarificationRequest.id == normalized_id)
        .first()
    )


def list_clarification_requests(
    db: Session,
    *,
    status: str | None = None,
    workflow_instance_id: str | None = None,
    department: str | None = None,
    limit: int = 100,
) -> list[ClarificationRequest]:
    query = db.query(ClarificationRequest)

    normalized_status = normalize_str(status)
    normalized_workflow_instance_id = normalize_str(workflow_instance_id)
    normalized_department = normalize_str(department)
    normalized_limit = max(1, min(int(limit), 200))

    if normalized_status:
        query = query.filter(ClarificationRequest.status == normalized_status)
    if normalized_workflow_instance_id:
        query = query.filter(
            ClarificationRequest.workflow_instance_id == normalized_workflow_instance_id
        )
    if normalized_department:
        query = query.filter(ClarificationRequest.department == normalized_department)

    return (
        query.order_by(ClarificationRequest.created_at.desc())
        .limit(normalized_limit)
        .all()
    )


def create_clarification_request(
    db: Session,
    *,
    workflow_instance: WorkflowInstance,
    prompt: str,
    fields: list[str] | None,
    context: dict[str, Any],
) -> ClarificationRequest:
    existing = _find_existing_pending_request(
        db,
        workflow_instance_id=str(workflow_instance.id),
    )
    if existing:
        return existing

    actor = extract_actor_from_nested_context(context)
    normalized_fields = normalize_string_list(fields or [])
    normalized_prompt = _normalize_prompt(prompt, fields=normalized_fields)

    row = ClarificationRequest(
        workflow_instance_id=workflow_instance.id,
        entity_type=workflow_instance.entity_type,
        entity_id=workflow_instance.entity_id,
        status=CLARIFICATION_STATUS_PENDING,
        department=normalize_str(actor.get("department")),
        requested_by_user_id=actor_id(actor),
        prompt=normalized_prompt,
        fields_json=safe_json(normalized_fields, default="[]"),
        context_json=safe_json(context, default="{}"),
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    write_audit(
        db,
        action="clarification.request.created",
        entity_type=CLARIFICATION_ENTITY_TYPE,
        entity_id=row.id,
        actor_user_id=actor_id(actor),
        meta_json={
            "workflow_instance_id": workflow_instance.id,
            "entity_type": workflow_instance.entity_type,
            "entity_id": workflow_instance.entity_id,
            "fields": normalized_fields,
            "prompt": normalized_prompt,
        },
    )

    return row


def resolve_clarification_request(
    db: Session,
    *,
    clarification_request: ClarificationRequest,
    actor: dict[str, Any],
    response_payload: dict[str, Any],
    resolution_note: str | None = None,
) -> ClarificationRequest:
    if clarification_request.status != CLARIFICATION_STATUS_PENDING:
        raise ValueError("Clarification already resolved")

    if not isinstance(response_payload, dict):
        raise ValueError("response_payload must be an object")

    resolved_by_user_id = actor_id(actor)
    normalized_note = _normalize_resolution_note(resolution_note)

    clarification_request.status = CLARIFICATION_STATUS_RESOLVED
    clarification_request.resolved_by_user_id = resolved_by_user_id
    clarification_request.response_json = safe_json(response_payload, default="{}")
    clarification_request.resolution_note = normalized_note
    clarification_request.resolved_at = utcnow()

    db.add(clarification_request)
    db.commit()
    db.refresh(clarification_request)

    write_audit(
        db,
        action="clarification.request.resolved",
        entity_type=CLARIFICATION_ENTITY_TYPE,
        entity_id=clarification_request.id,
        actor_user_id=resolved_by_user_id,
        meta_json={
            "workflow_instance_id": clarification_request.workflow_instance_id,
            "resolution_note": normalized_note,
            "response_keys": sorted(list(response_payload.keys())),
        },
    )

    resume_workflow_instance(
        db,
        workflow_instance_id=clarification_request.workflow_instance_id,
        context_updates={
            "clarification": {
                "clarification_request_id": clarification_request.id,
                "status": clarification_request.status,
                "resolved_by_user_id": resolved_by_user_id,
                "resolution_note": normalized_note,
                "resolved_at": clarification_request.resolved_at.isoformat()
                if clarification_request.resolved_at
                else None,
            },
            **response_payload,
        },
    )

    return clarification_request


def cancel_clarification_request(
    db: Session,
    *,
    clarification_request: ClarificationRequest,
    actor: dict[str, Any] | None = None,
    resolution_note: str | None = None,
) -> ClarificationRequest:
    if clarification_request.status != CLARIFICATION_STATUS_PENDING:
        raise ValueError("Only pending clarification requests can be cancelled")

    resolved_by_user_id = actor_id(actor or {})
    normalized_note = _normalize_resolution_note(resolution_note)

    clarification_request.status = CLARIFICATION_STATUS_CANCELLED
    clarification_request.resolved_by_user_id = resolved_by_user_id
    clarification_request.resolution_note = normalized_note
    clarification_request.resolved_at = utcnow()

    db.add(clarification_request)
    db.commit()
    db.refresh(clarification_request)

    write_audit(
        db,
        action="clarification.request.cancelled",
        entity_type=CLARIFICATION_ENTITY_TYPE,
        entity_id=clarification_request.id,
        actor_user_id=resolved_by_user_id,
        meta_json={
            "workflow_instance_id": clarification_request.workflow_instance_id,
            "resolution_note": normalized_note,
        },
    )

    return clarification_request