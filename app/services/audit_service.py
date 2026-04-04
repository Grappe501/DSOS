from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import AuditLog


MALONE_ENTITY_TYPE = "malone_proposal"


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
    entity_id: str | None = None,
    actor_user_id: str | None = None,
    meta_json: dict[str, Any] | None = None,
) -> AuditLog:
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
    entity_id: str | None,
    actor: dict | None,
    before_json: Any = None,
    after_json: Any = None,
    meta_json: dict[str, Any] | None = None,
) -> AuditLog:
    payload = dict(meta_json or {})

    if actor:
        payload.update(
            {
                "actor_email": actor.get("email"),
                "actor_role": actor.get("role"),
                "department": actor.get("department"),
            }
        )

    if before_json is not None:
        payload["before"] = before_json

    if after_json is not None:
        payload["after"] = after_json

    return write_audit(
        db,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor.get("id") if actor else None,
        meta_json=payload,
    )


def log_transition(
    db: Session,
    *,
    entity_type: str,
    entity_id: str,
    from_state: str | None,
    to_state: str,
    actor: dict | None,
    meta_json: dict[str, Any] | None = None,
) -> AuditLog:
    payload = dict(meta_json or {})
    payload["from_state"] = from_state
    payload["to_state"] = to_state

    return log_write_action(
        db,
        action="state_transition",
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
        meta_json=payload,
    )


def log_malone_action(
    db: Session,
    *,
    action: str,
    proposal_id: str,
    actor: dict[str, Any] | None,
    meta_json: dict[str, Any] | None = None,
) -> AuditLog:
    return log_write_action(
        db,
        action=action,
        entity_type=MALONE_ENTITY_TYPE,
        entity_id=proposal_id,
        actor=actor,
        meta_json=meta_json,
    )
