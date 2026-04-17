from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from app.models.models import WorkflowState
from app.services.audit_service import log_transition
from app.services.workflows.json_utils import normalize_str, serialize_meta, utcnow
def _normalize_entity_id(entity_id: int | str) -> str:
    text = normalize_str(entity_id)
    if not text:
        raise ValueError("entity_id is required")
    return text
def _normalize_state(value: str, *, field_name: str) -> str:
    text = normalize_str(value)
    if not text:
        raise ValueError(f"{field_name} is required")
    return text
def mark_workflow_state(db: Session, *, workflow_name: str, entity_type: str, entity_id: int | str, state: str, status: str="active", actor_user_id: int | str | None=None, department: str | None=None, meta_json: dict[str, Any] | None=None) -> WorkflowState:
    row = WorkflowState(workflow_name=_normalize_state(workflow_name, field_name="workflow_name"), entity_type=_normalize_state(entity_type, field_name="entity_type"), entity_id=_normalize_entity_id(entity_id), state=_normalize_state(state, field_name="state"), status=_normalize_state(status, field_name="status"), meta_json=serialize_meta(meta_json) or "{}", created_at=utcnow(), updated_at=utcnow())
    db.add(row); db.commit(); db.refresh(row)
    log_transition(db, entity_type=row.entity_type, entity_id=row.entity_id, from_state=None, to_state=row.state, actor={"id": str(actor_user_id) if actor_user_id is not None else None, "department": normalize_str(department)}, meta_json={"workflow_name": row.workflow_name, "status": row.status, **(meta_json or {})})
    return row
def start_schedule_workflow(db: Session, *, schedule_id: int | str, actor_user_id: int | str | None=None, department: str | None=None, initial_state: str="created", meta_json: dict[str, Any] | None=None) -> WorkflowState:
    return mark_workflow_state(db, workflow_name="schedule_workflow", entity_type="schedule", entity_id=schedule_id, state=initial_state, status="active", actor_user_id=actor_user_id, department=department, meta_json=meta_json)
def route_conflict_resolution(db: Session, *, schedule_id: int | str, actor_user_id: int | str | None=None, department: str | None=None, reason: str | None=None, meta_json: dict[str, Any] | None=None) -> WorkflowState:
    payload=dict(meta_json or {})
    if normalize_str(reason) is not None:
        payload["reason"]=normalize_str(reason)
    return mark_workflow_state(db, workflow_name="schedule_workflow", entity_type="schedule", entity_id=schedule_id, state="conflict_resolution", status="active", actor_user_id=actor_user_id, department=department, meta_json=payload)
def transition_schedule_state(db: Session, *, schedule_id: int | str, to_state: str, actor_user_id: int | str | None=None, department: str | None=None, meta_json: dict[str, Any] | None=None) -> WorkflowState:
    return mark_workflow_state(db, workflow_name="schedule_approval", entity_type="schedule", entity_id=schedule_id, state=to_state, status="active", actor_user_id=actor_user_id, department=department, meta_json=meta_json)
def get_entity_workflow_history(db: Session, *, entity_type: str, entity_id: int | str, workflow_name: str | None=None) -> list[WorkflowState]:
    query=db.query(WorkflowState).filter(WorkflowState.entity_type==_normalize_state(entity_type, field_name="entity_type"), WorkflowState.entity_id==_normalize_entity_id(entity_id))
    if normalize_str(workflow_name):
        query=query.filter(WorkflowState.workflow_name==normalize_str(workflow_name))
    return query.order_by(WorkflowState.created_at.asc()).all()
