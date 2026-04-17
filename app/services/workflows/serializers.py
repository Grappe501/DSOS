from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from app.models.models import WorkflowDefinition, WorkflowInstance, WorkflowStepDefinition, WorkflowStepExecution
from app.services.workflows.json_utils import coerce_json, ensure_dict, isoformat_or_none
def serialize_workflow_step_definition(step: WorkflowStepDefinition) -> dict[str, Any]:
    return {"id": step.id, "workflow_definition_id": step.workflow_definition_id, "name": step.name, "step_key": step.step_key, "step_order": step.step_order, "next_step_id": step.next_step_id, "is_terminal": step.is_terminal, "config": ensure_dict(coerce_json(step.config_json)), "created_at": isoformat_or_none(getattr(step, "created_at", None)), "updated_at": isoformat_or_none(getattr(step, "updated_at", None))}
def serialize_workflow_step_execution(execution: WorkflowStepExecution) -> dict[str, Any]:
    return {"id": execution.id, "workflow_instance_id": execution.workflow_instance_id, "workflow_step_id": execution.workflow_step_id, "status": execution.status, "input": ensure_dict(coerce_json(execution.input_json)), "output": ensure_dict(coerce_json(execution.output_json)), "error_message": execution.error_message, "executed_at": isoformat_or_none(execution.executed_at)}
def serialize_workflow_definition(definition: WorkflowDefinition, db: Session | None = None) -> dict[str, Any]:
    steps=[]
    if db is not None:
        rows=(db.query(WorkflowStepDefinition).filter(WorkflowStepDefinition.workflow_definition_id==definition.id).order_by(WorkflowStepDefinition.step_order.asc(), WorkflowStepDefinition.created_at.asc()).all())
        steps=[serialize_workflow_step_definition(r) for r in rows]
    return {"id": definition.id, "name": definition.name, "version": definition.version, "description": definition.description, "status": definition.status, "entry_step_id": definition.entry_step_id, "created_at": isoformat_or_none(getattr(definition, "created_at", None)), "updated_at": isoformat_or_none(getattr(definition, "updated_at", None)), "steps": steps}
def serialize_workflow_instance(instance: WorkflowInstance, db: Session | None = None) -> dict[str, Any]:
    definition=current_step=None; executions=[]
    if db is not None:
        definition=db.query(WorkflowDefinition).filter(WorkflowDefinition.id==instance.workflow_definition_id).first()
        if instance.current_step_id:
            current_step=db.query(WorkflowStepDefinition).filter(WorkflowStepDefinition.id==instance.current_step_id).first()
        rows=(db.query(WorkflowStepExecution).filter(WorkflowStepExecution.workflow_instance_id==instance.id).order_by(WorkflowStepExecution.executed_at.asc()).all())
        executions=[serialize_workflow_step_execution(r) for r in rows]
    context=ensure_dict(coerce_json(instance.context_json))
    return {"id": instance.id, "workflow_definition_id": instance.workflow_definition_id, "workflow_name": definition.name if definition else None, "workflow_version": definition.version if definition else None, "entity_type": instance.entity_type, "entity_id": instance.entity_id, "status": instance.status, "current_step_id": instance.current_step_id, "current_step_name": current_step.name if current_step else None, "context": context, "last_error": instance.last_error, "started_at": isoformat_or_none(instance.started_at), "completed_at": isoformat_or_none(instance.completed_at), "created_at": isoformat_or_none(getattr(instance, "created_at", None)), "updated_at": isoformat_or_none(getattr(instance, "updated_at", None)), "executions": executions}
