from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import MaloneProposal


ALLOWED_ACTIONS_BY_MODE = {
    "answer": {"respond"},
    "analyst": {"analyze"},
    "builder": {"propose_build"},
    "agentic": {"spawn_agent"},
}


def _safe_json(value: Any) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except Exception:
        return json.dumps({"raw": str(value)})


def _coerce_json(value: str | None) -> Any:
    if value in (None, ""):
        return None
    try:
        return json.loads(value)
    except Exception:
        return value


def _result_bundle(row: MaloneProposal) -> dict[str, Any]:
    raw = _coerce_json(getattr(row, "result_json", None))
    if isinstance(raw, dict) and any(
        key in raw
        for key in [
            "deterministic_result",
            "deterministic_execution",
            "rendered_output",
            "verification",
            "delivery_status",
        ]
    ):
        return raw

    return {
        "deterministic_result": raw,
        "deterministic_execution": None,
        "rendered_output": None,
        "verification": None,
        "delivery_status": "deterministic_only" if raw is not None else None,
    }


def serialize_proposal_record(row: MaloneProposal) -> dict[str, Any]:
    bundle = _result_bundle(row)
    return {
        "id": getattr(row, "id", None),
        "proposal_type": getattr(row, "proposal_type", None),
        "requested_action": getattr(row, "requested_action", None),
        "target": getattr(row, "target", None),
        "source_message": getattr(row, "source_message", None),
        "actor_user_id": getattr(row, "actor_user_id", None),
        "actor_email": getattr(row, "actor_email", None),
        "actor_role": getattr(row, "actor_role", None),
        "actor_department": getattr(row, "actor_department", None),
        "validation_status": getattr(row, "validation_status", None),
        "approval_status": getattr(row, "approval_status", None),
        "execution_status": getattr(row, "execution_status", None),
        "delivery_status": bundle.get("delivery_status"),
        "candidate_output": _coerce_json(getattr(row, "candidate_output_json", None)),
        "validation": _coerce_json(getattr(row, "validation_json", None)),
        "result": bundle.get("deterministic_result"),
        "deterministic_execution": bundle.get("deterministic_execution"),
        "rendered_output": bundle.get("rendered_output"),
        "verification": bundle.get("verification"),
        "created_at": getattr(row, "created_at", None).isoformat()
        if getattr(row, "created_at", None)
        else None,
        "updated_at": getattr(row, "updated_at", None).isoformat()
        if getattr(row, "updated_at", None)
        else None,
    }


def build_proposal_envelope(
    *,
    proposal_type: str,
    requested_action: str,
    candidate_output: dict[str, Any],
    actor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "proposal_type": proposal_type,
        "requested_action": requested_action,
        "candidate_output": candidate_output,
        "origin_actor": actor,
        "validation_status": "pending",
        "approval_status": "pending",
    }


def validate_proposal_envelope(
    *,
    proposal: dict[str, Any],
) -> dict[str, Any]:
    proposal_type = proposal.get("proposal_type")
    requested_action = proposal.get("requested_action")
    actor = proposal.get("origin_actor") or {}

    reasons: list[str] = []

    if proposal_type not in ALLOWED_ACTIONS_BY_MODE:
        reasons.append(f"unknown proposal_type: {proposal_type}")

    allowed_actions = ALLOWED_ACTIONS_BY_MODE.get(proposal_type, set())
    if requested_action not in allowed_actions:
        reasons.append(f"requested_action '{requested_action}' not allowed for mode '{proposal_type}'")

    if not actor.get("id"):
        reasons.append("missing actor id")

    is_valid = len(reasons) == 0

    return {
        "is_valid": is_valid,
        "reasons": reasons,
        "validated_mode": proposal_type,
        "validated_action": requested_action,
    }


def create_proposal_record(
    *,
    db: Session,
    proposal: dict[str, Any],
    source_message: str,
    target: str | None,
) -> MaloneProposal:
    actor = proposal.get("origin_actor") or {}

    row = MaloneProposal(
        proposal_type=proposal.get("proposal_type") or "unknown",
        requested_action=proposal.get("requested_action") or "unknown",
        target=target,
        source_message=source_message,
        actor_user_id=actor.get("id"),
        actor_email=actor.get("email"),
        actor_role=actor.get("role"),
        actor_department=actor.get("department"),
        validation_status=proposal.get("validation_status") or "pending",
        approval_status=proposal.get("approval_status") or "pending",
        execution_status="proposal_only",
        candidate_output_json=_safe_json(proposal.get("candidate_output") or {}),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_proposal_record(
    *,
    db: Session,
    proposal_record: MaloneProposal,
    validation_status: str | None = None,
    approval_status: str | None = None,
    execution_status: str | None = None,
    validation_payload: dict[str, Any] | None = None,
    result_payload: dict[str, Any] | None = None,
    deterministic_execution_payload: dict[str, Any] | None = None,
    rendered_output_payload: dict[str, Any] | None = None,
    verification_payload: dict[str, Any] | None = None,
    delivery_status: str | None = None,
) -> MaloneProposal:
    if validation_status is not None:
        proposal_record.validation_status = validation_status
    if approval_status is not None:
        proposal_record.approval_status = approval_status
    if execution_status is not None:
        proposal_record.execution_status = execution_status
    if validation_payload is not None:
        proposal_record.validation_json = _safe_json(validation_payload)

    current_bundle = _result_bundle(proposal_record)
    next_bundle = {
        "deterministic_result": current_bundle.get("deterministic_result"),
        "deterministic_execution": current_bundle.get("deterministic_execution"),
        "rendered_output": current_bundle.get("rendered_output"),
        "verification": current_bundle.get("verification"),
        "delivery_status": current_bundle.get("delivery_status"),
    }

    if result_payload is not None:
        next_bundle["deterministic_result"] = result_payload
    if deterministic_execution_payload is not None:
        next_bundle["deterministic_execution"] = deterministic_execution_payload
    if rendered_output_payload is not None:
        next_bundle["rendered_output"] = rendered_output_payload
    if verification_payload is not None:
        next_bundle["verification"] = verification_payload
    if delivery_status is not None:
        next_bundle["delivery_status"] = delivery_status

    proposal_record.result_json = _safe_json(next_bundle)

    db.add(proposal_record)
    db.commit()
    db.refresh(proposal_record)
    return proposal_record


def list_recent_proposals(
    *,
    db: Session,
    actor_user_id: str | None = None,
    limit: int = 20,
) -> list[MaloneProposal]:
    query = db.query(MaloneProposal)
    if actor_user_id:
        query = query.filter(MaloneProposal.actor_user_id == actor_user_id)
    return query.order_by(MaloneProposal.created_at.desc()).limit(limit).all()