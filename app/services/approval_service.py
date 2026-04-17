from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.models import ApprovalRequest, WorkflowInstance
from app.services.audit_service import write_audit
from app.services.workflow_service import resume_workflow_instance
from app.services.workflows.constants import (
    APPROVAL_ENTITY_TYPE,
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_PENDING,
    APPROVAL_STATUS_REJECTED,
)
from app.services.workflows.json_utils import (
    actor_id,
    coerce_json,
    extract_actor_from_nested_context,
    normalize_str,
    safe_json,
    utcnow,
)


def _normalize_required_role(required_role: str | None) -> str:
    return normalize_str(required_role) or "admin"


def _normalize_reason(reason: str | None) -> str | None:
    return normalize_str(reason)


def _can_resolve(required_role: str, actor_role: str) -> bool:
    normalized_actor_role = normalize_str(actor_role)
    if normalized_actor_role == "owner":
        return True
    return normalized_actor_role == required_role


def _find_existing_pending_request(
    db: Session,
    *,
    workflow_instance_id: str,
) -> ApprovalRequest | None:
    return (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.workflow_instance_id == workflow_instance_id,
            ApprovalRequest.status == APPROVAL_STATUS_PENDING,
        )
        .order_by(ApprovalRequest.created_at.desc())
        .first()
    )


def serialize_approval_request(row: ApprovalRequest) -> dict[str, Any]:
    return {
        "id": row.id,
        "workflow_instance_id": row.workflow_instance_id,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "required_role": row.required_role,
        "status": row.status,
        "department": row.department,
        "requested_by_user_id": row.requested_by_user_id,
        "resolved_by_user_id": row.resolved_by_user_id,
        "context_json": coerce_json(row.context_json),
        "decision_reason": row.decision_reason,
        "decision_at": row.decision_at.isoformat() if row.decision_at else None,
        "created_at": row.created_at.isoformat() if getattr(row, "created_at", None) else None,
        "updated_at": row.updated_at.isoformat() if getattr(row, "updated_at", None) else None,
    }


def get_approval_request(
    db: Session,
    approval_id: str,
) -> ApprovalRequest | None:
    normalized_id = normalize_str(approval_id)
    if not normalized_id:
        return None

    return (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.id == normalized_id)
        .first()
    )


def list_approval_requests(
    db: Session,
    *,
    status: str | None = None,
    required_role: str | None = None,
    workflow_instance_id: str | None = None,
    department: str | None = None,
    limit: int = 100,
) -> list[ApprovalRequest]:
    query = db.query(ApprovalRequest)

    normalized_status = normalize_str(status)
    normalized_required_role = normalize_str(required_role)
    normalized_workflow_instance_id = normalize_str(workflow_instance_id)
    normalized_department = normalize_str(department)
    normalized_limit = max(1, min(int(limit), 200))

    if normalized_status:
        query = query.filter(ApprovalRequest.status == normalized_status)
    if normalized_required_role:
        query = query.filter(ApprovalRequest.required_role == normalized_required_role)
    if normalized_workflow_instance_id:
        query = query.filter(ApprovalRequest.workflow_instance_id == normalized_workflow_instance_id)
    if normalized_department:
        query = query.filter(ApprovalRequest.department == normalized_department)

    return (
        query.order_by(ApprovalRequest.created_at.desc())
        .limit(normalized_limit)
        .all()
    )


def create_approval_request(
    db: Session,
    *,
    workflow_instance: WorkflowInstance,
    required_role: str,
    context: dict[str, Any],
) -> ApprovalRequest:
    existing = _find_existing_pending_request(
        db,
        workflow_instance_id=str(workflow_instance.id),
    )
    if existing:
        return existing

    normalized_required_role = _normalize_required_role(required_role)
    actor = extract_actor_from_nested_context(context)

    row = ApprovalRequest(
        workflow_instance_id=workflow_instance.id,
        entity_type=workflow_instance.entity_type,
        entity_id=workflow_instance.entity_id,
        required_role=normalized_required_role,
        status=APPROVAL_STATUS_PENDING,
        department=normalize_str(actor.get("department")),
        requested_by_user_id=actor_id(actor),
        context_json=safe_json(context),
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    write_audit(
        db,
        action="approval.request.created",
        entity_type=APPROVAL_ENTITY_TYPE,
        entity_id=row.id,
        actor_user_id=actor_id(actor),
        meta_json={
            "workflow_instance_id": workflow_instance.id,
            "entity_type": workflow_instance.entity_type,
            "entity_id": workflow_instance.entity_id,
            "required_role": normalized_required_role,
            "department": normalize_str(actor.get("department")),
        },
    )

    return row


def resolve_approval_request(
    db: Session,
    *,
    approval_request: ApprovalRequest,
    actor: dict[str, Any],
    actor_role: str,
    approved: bool,
    reason: str | None = None,
) -> ApprovalRequest:
    if approval_request.status != APPROVAL_STATUS_PENDING:
        raise ValueError("Approval already resolved")

    if not _can_resolve(approval_request.required_role, actor_role):
        raise ValueError("Unauthorized role")

    normalized_reason = _normalize_reason(reason)
    resolved_by_user_id = actor_id(actor)
    normalized_actor_role = normalize_str(actor_role)

    approval_request.status = (
        APPROVAL_STATUS_APPROVED if approved else APPROVAL_STATUS_REJECTED
    )
    approval_request.resolved_by_user_id = resolved_by_user_id
    approval_request.decision_reason = normalized_reason
    approval_request.decision_at = utcnow()

    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)

    write_audit(
        db,
        action="approval.request.resolved",
        entity_type=APPROVAL_ENTITY_TYPE,
        entity_id=approval_request.id,
        actor_user_id=resolved_by_user_id,
        meta_json={
            "status": approval_request.status,
            "reason": normalized_reason,
            "workflow_instance_id": approval_request.workflow_instance_id,
            "required_role": approval_request.required_role,
            "resolved_by_role": normalized_actor_role,
        },
    )

    if approved:
        resume_workflow_instance(
            db,
            workflow_instance_id=approval_request.workflow_instance_id,
            context_updates={
                "approval": {
                    "approval_request_id": approval_request.id,
                    "status": approval_request.status,
                    "required_role": approval_request.required_role,
                    "resolved_by_user_id": resolved_by_user_id,
                    "resolved_by_role": normalized_actor_role,
                    "decision_reason": normalized_reason,
                    "decision_at": approval_request.decision_at.isoformat()
                    if approval_request.decision_at
                    else None,
                }
            },
        )
    else:
        write_audit(
            db,
            action="workflow.approval.rejected",
            entity_type="workflow_instance",
            entity_id=approval_request.workflow_instance_id,
            actor_user_id=resolved_by_user_id,
            meta_json={
                "approval_request_id": approval_request.id,
                "reason": normalized_reason,
            },
        )

    return approval_request


def reject_approval_request(
    db: Session,
    *,
    approval_request: ApprovalRequest,
    actor: dict[str, Any],
    actor_role: str,
    reason: str | None = None,
) -> ApprovalRequest:
    return resolve_approval_request(
        db,
        approval_request=approval_request,
        actor=actor,
        actor_role=actor_role,
        approved=False,
        reason=reason,
    )