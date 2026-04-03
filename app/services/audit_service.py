from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import AuditLog


def _safe_json(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except Exception:
        return str(value)


def write_audit(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    actor_user_id: int | None = None,
    meta_json: dict[str, Any] | str | None = None,
) -> AuditLog:
    """
    Backward-compatible audit writer used by existing services.
    """
    row = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        meta_json=_safe_json(meta_json),
        created_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def log_write_action(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    actor_user_id: int | None = None,
    department: str | None = None,
    before_json: Any = None,
    after_json: Any = None,
    request_id: str | None = None,
    meta_json: dict[str, Any] | None = None,
) -> AuditLog:
    """
    Phase 3+ normalized audit helper.
    Keeps compatibility by storing extended fields inside meta_json
    unless the model has dedicated columns for them.
    """
    payload: dict[str, Any] = dict(meta_json or {})
    if department is not None:
        payload["department"] = department
    if request_id is not None:
        payload["request_id"] = request_id
    if before_json is not None:
        payload["before_json"] = before_json
    if after_json is not None:
        payload["after_json"] = after_json

    return write_audit(
        db,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        meta_json=payload or None,
    )


def log_transition(
    db: Session,
    *,
    entity_type: str,
    entity_id: int | None,
    from_state: str | None,
    to_state: str,
    actor_user_id: int | None = None,
    department: str | None = None,
    meta_json: dict[str, Any] | None = None,
) -> AuditLog:
    payload: dict[str, Any] = dict(meta_json or {})
    payload["from_state"] = from_state
    payload["to_state"] = to_state
    if department is not None:
        payload["department"] = department

    return write_audit(
        db,
        action="state_transition",
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        meta_json=payload,
    )