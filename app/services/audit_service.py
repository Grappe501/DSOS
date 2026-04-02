from __future__ import annotations

import json

from app.db.session import SessionLocal
from app.models.models import AuditLog


def write_audit(
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    """
    Persist an audit entry.

    Notes:
    - AuditLog uses `meta_json`, not `metadata`, because `metadata` is a reserved
      name in SQLAlchemy declarative models.
    - Metadata is serialized to JSON consistently for traceability and replay.
    """
    db = SessionLocal()
    try:
        entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            meta_json=json.dumps(metadata or {}, default=str),
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()