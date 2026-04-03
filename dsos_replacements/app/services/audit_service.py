from __future__ import annotations

import json
from typing import Any

from app.db.session import SessionLocal
from app.models.models import AuditLog


ActorContext = dict[str, Any]


def make_actor_context(
    *,
    user_id: str | None = None,
    email: str | None = None,
    role: str | None = None,
    department: str | None = None,
) -> ActorContext:
    return {
        "actor_user_id": user_id,
        "actor_email": email,
        "actor_role": role,
        "actor_department": department,
    }


def write_audit(
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    *,
    actor_user_id: str | None = None,
    actor_email: str | None = None,
    actor_role: str | None = None,
    actor_department: str | None = None,
) -> None:
    """
    Persist an audit entry with normalized actor context.

    Notes:
    - AuditLog uses `meta_json`, not `metadata`, because `metadata` is a reserved
      name in SQLAlchemy declarative models.
    - Actor context is written both to first-class columns where available and to
      the audit payload for easier operational review.
    """
    audit_payload = dict(metadata or {})
    audit_payload.setdefault("actor_user_id", actor_user_id)
    audit_payload.setdefault("actor_email", actor_email)
    audit_payload.setdefault("actor_role", actor_role)
    audit_payload.setdefault("actor_department", actor_department)
    audit_payload.setdefault("department", audit_payload.get("department", actor_department))

    db = SessionLocal()
    try:
        entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            meta_json=json.dumps(audit_payload, default=str),
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def parse_meta_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {"raw": parsed}
    except json.JSONDecodeError:
        return {"raw": value}
