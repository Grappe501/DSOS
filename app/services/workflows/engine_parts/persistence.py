from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from app.models.models import WorkflowInstance, WorkflowStepExecution
from app.services.workflows.json_utils import safe_json, utcnow
def write_step_execution(db: Session, *, workflow_instance_id: str, step_id: str, status: str, input_payload: dict[str, Any], output_payload: dict[str, Any] | None = None, error_message: str | None = None) -> WorkflowStepExecution:
    row = WorkflowStepExecution(workflow_instance_id=workflow_instance_id, workflow_step_id=step_id, status=status, input_json=safe_json(input_payload), output_json=safe_json(output_payload or {}), error_message=error_message, executed_at=utcnow())
    db.add(row); db.commit(); db.refresh(row); return row
def set_instance_state(db: Session, *, instance: WorkflowInstance, status: str, current_step_id: str | None, last_error: str | None = None, mark_completed: bool = False) -> WorkflowInstance:
    instance.status=status; instance.current_step_id=current_step_id; instance.last_error=last_error
    if mark_completed: instance.completed_at=utcnow()
    db.add(instance); db.commit(); db.refresh(instance); return instance
