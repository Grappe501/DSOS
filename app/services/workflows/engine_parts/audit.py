from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from app.models.models import WorkflowInstance
from app.services.audit_service import write_audit
from app.services.workflows.constants import WORKFLOW_ENTITY_TYPE
def audit_workflow_instance(db: Session, *, action: str, instance: WorkflowInstance, actor_user_id: str | None, meta_json: dict[str, Any]) -> None:
    write_audit(db, action=action, entity_type=WORKFLOW_ENTITY_TYPE, entity_id=instance.id, actor_user_id=actor_user_id, meta_json=meta_json)
