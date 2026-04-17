from __future__ import annotations
from sqlalchemy.orm import Session
from app.models.models import WorkflowDefinition, WorkflowInstance, WorkflowStepDefinition
def list_workflow_instances(db: Session, *, limit: int = 50) -> list[WorkflowInstance]:
    return db.query(WorkflowInstance).order_by(WorkflowInstance.created_at.desc()).limit(limit).all()
def get_workflow_instance(db: Session, workflow_instance_id: str) -> WorkflowInstance | None:
    return db.query(WorkflowInstance).filter(WorkflowInstance.id == workflow_instance_id).first()
def get_workflow_definition_for_execution(db: Session, *, name: str, version: str | None = None) -> WorkflowDefinition:
    query = db.query(WorkflowDefinition).filter(WorkflowDefinition.name == name)
    if version: query = query.filter(WorkflowDefinition.version == version)
    else: query = query.filter(WorkflowDefinition.status == "active")
    definition = query.order_by(WorkflowDefinition.created_at.desc()).first()
    if not definition: raise ValueError(f"Workflow definition '{name}' was not found")
    if not definition.entry_step_id: raise ValueError(f"Workflow definition '{name}' has no entry step")
    return definition
def get_workflow_step(db: Session, step_id: str | None) -> WorkflowStepDefinition | None:
    if not step_id: return None
    return db.query(WorkflowStepDefinition).filter(WorkflowStepDefinition.id == step_id).first()
