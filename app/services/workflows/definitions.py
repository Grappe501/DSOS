from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session
from app.models.models import WorkflowDefinition, WorkflowStepDefinition
from app.services.workflows.constants import DEFAULT_WORKFLOW_NAME, DEFAULT_WORKFLOW_VERSION, HANDLER_KEY_MALONE_EXECUTE_ACTION, HANDLER_KEY_MALONE_VALIDATE_ACTION, HANDLER_KEY_WORKFLOW_MARK_COMPLETE
from app.services.workflows.json_utils import normalize_str, safe_json
def _normalize_workflow_name(name: str) -> str:
    normalized = normalize_str(name)
    if not normalized: raise ValueError("workflow name is required")
    return normalized
def _normalize_workflow_version(version: str | None) -> str:
    return normalize_str(version) or DEFAULT_WORKFLOW_VERSION
def get_workflow_definition(db: Session, *, name: str, version: str | None = None) -> WorkflowDefinition | None:
    query = db.query(WorkflowDefinition).filter(WorkflowDefinition.name == _normalize_workflow_name(name))
    if version is not None: query = query.filter(WorkflowDefinition.version == _normalize_workflow_version(version))
    return query.order_by(WorkflowDefinition.created_at.desc()).first()
def list_workflow_definitions(db: Session, *, status: str | None = None) -> list[WorkflowDefinition]:
    query = db.query(WorkflowDefinition)
    if normalize_str(status): query = query.filter(WorkflowDefinition.status == normalize_str(status))
    return query.order_by(WorkflowDefinition.created_at.asc(), WorkflowDefinition.name.asc(), WorkflowDefinition.version.asc()).all()
def get_workflow_definition_by_id(db: Session, workflow_definition_id: str) -> WorkflowDefinition | None:
    return db.query(WorkflowDefinition).filter(WorkflowDefinition.id == normalize_str(workflow_definition_id)).first()
def list_workflow_steps(db: Session, *, workflow_definition_id: str) -> list[WorkflowStepDefinition]:
    return db.query(WorkflowStepDefinition).filter(WorkflowStepDefinition.workflow_definition_id == normalize_str(workflow_definition_id)).order_by(WorkflowStepDefinition.step_order.asc(), WorkflowStepDefinition.created_at.asc()).all()
def get_workflow_step(db: Session, *, step_id: str) -> WorkflowStepDefinition | None:
    return db.query(WorkflowStepDefinition).filter(WorkflowStepDefinition.id == normalize_str(step_id)).first()
def create_workflow_definition(db: Session, *, name: str, version: str | None = None, description: str | None = None, status: str | None = None) -> WorkflowDefinition:
    existing = get_workflow_definition(db, name=name, version=version)
    if existing: return existing
    row = WorkflowDefinition(name=_normalize_workflow_name(name), version=_normalize_workflow_version(version), description=normalize_str(description), status=normalize_str(status) or "active")
    db.add(row); db.commit(); db.refresh(row); return row
def create_workflow_step_definition(db: Session, *, workflow_definition_id: str, name: str, step_key: str, step_order: int, next_step_id: str | None = None, is_terminal: bool = False, config: dict[str, Any] | None = None) -> WorkflowStepDefinition:
    row = WorkflowStepDefinition(workflow_definition_id=normalize_str(workflow_definition_id), name=normalize_str(name), step_key=normalize_str(step_key), step_order=int(step_order), next_step_id=normalize_str(next_step_id), is_terminal=bool(is_terminal), config_json=safe_json(config or {}))
    db.add(row); db.commit(); db.refresh(row); return row
def update_workflow_step_links(db: Session, *, step_id: str, next_step_id: str | None, is_terminal: bool | None = None) -> WorkflowStepDefinition:
    step = get_workflow_step(db, step_id=step_id)
    if not step: raise ValueError("workflow step not found")
    step.next_step_id = normalize_str(next_step_id)
    if is_terminal is not None: step.is_terminal = bool(is_terminal)
    db.add(step); db.commit(); db.refresh(step); return step
def set_workflow_entry_step(db: Session, *, workflow_definition_id: str, entry_step_id: str) -> WorkflowDefinition:
    definition = get_workflow_definition_by_id(db, workflow_definition_id)
    step = get_workflow_step(db, step_id=entry_step_id)
    if not definition or not step or step.workflow_definition_id != definition.id: raise ValueError("entry step must belong to workflow definition")
    definition.entry_step_id = step.id; db.add(definition); db.commit(); db.refresh(definition); return definition
def validate_workflow_definition_integrity(db: Session, *, definition: WorkflowDefinition) -> dict[str, Any]:
    steps = list_workflow_steps(db, workflow_definition_id=definition.id); errors=[]; warnings=[]
    if not steps: errors.append("workflow_has_no_steps")
    if steps and not definition.entry_step_id: errors.append("workflow_missing_entry_step")
    step_ids = {s.id for s in steps}
    for step in steps:
        if step.next_step_id and step.next_step_id not in step_ids: errors.append(f"step_next_step_missing:{step.id}")
    return {"ok": len(errors)==0, "workflow_definition_id": definition.id, "workflow_name": definition.name, "workflow_version": definition.version, "step_count": len(steps), "entry_step_id": definition.entry_step_id, "errors": errors, "warnings": warnings}
def ensure_workflow_seed_data(db: Session) -> None:
    definition = get_workflow_definition(db, name=DEFAULT_WORKFLOW_NAME, version=DEFAULT_WORKFLOW_VERSION)
    if definition: return
    definition = create_workflow_definition(db, name=DEFAULT_WORKFLOW_NAME, version=DEFAULT_WORKFLOW_VERSION, description="Malone deterministic governed execution workflow.", status="active")
    validate_step = create_workflow_step_definition(db, workflow_definition_id=definition.id, name="Validate deterministic action", step_key=HANDLER_KEY_MALONE_VALIDATE_ACTION, step_order=1, config={"purpose": "validate deterministic action routing"})
    execute_step = create_workflow_step_definition(db, workflow_definition_id=definition.id, name="Execute deterministic action", step_key=HANDLER_KEY_MALONE_EXECUTE_ACTION, step_order=2, config={"purpose": "execute registered deterministic action"})
    finalize_step = create_workflow_step_definition(db, workflow_definition_id=definition.id, name="Finalize workflow", step_key=HANDLER_KEY_WORKFLOW_MARK_COMPLETE, step_order=3, is_terminal=True, config={"purpose": "finalize auditable workflow lifecycle"})
    update_workflow_step_links(db, step_id=validate_step.id, next_step_id=execute_step.id, is_terminal=False)
    update_workflow_step_links(db, step_id=execute_step.id, next_step_id=finalize_step.id, is_terminal=False)
    update_workflow_step_links(db, step_id=finalize_step.id, next_step_id=None, is_terminal=True)
    set_workflow_entry_step(db, workflow_definition_id=definition.id, entry_step_id=validate_step.id)
