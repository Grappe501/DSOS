from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import MaloneProposal, WorkflowInstance, WorkflowStepDefinition
from app.services.audit_service import log_malone_action
from app.services.deterministic_executor import execute_action
from app.services.deterministic_validator import validate_action
from app.services.workflows.constants import (
    HANDLER_KEY_MALONE_EXECUTE_ACTION,
    HANDLER_KEY_MALONE_VALIDATE_ACTION,
    HANDLER_KEY_WORKFLOW_MARK_COMPLETE,
    STEP_STATUS_BLOCKED,
    STEP_STATUS_COMPLETED,
    WORKFLOW_STATUS_BLOCKED,
    WORKFLOW_STATUS_COMPLETED,
)
from app.services.workflows.json_utils import safe_json
from app.services.workflows.registry import register_workflow_handler


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _get_actor(context: dict[str, Any]) -> dict[str, Any]:
    return context.get("actor") or {}


def _get_proposal(db: Session, proposal_id: Any) -> MaloneProposal | None:
    if not proposal_id:
        return None
    return db.query(MaloneProposal).filter(MaloneProposal.id == proposal_id).first()


def _persist_proposal(
    db: Session,
    proposal: MaloneProposal,
    *,
    execution_status: str,
    validation_payload: dict[str, Any] | None = None,
) -> None:
    if validation_payload is not None:
        proposal.validation_json = safe_json(validation_payload)

    proposal.execution_status = execution_status
    db.add(proposal)
    db.commit()
    db.refresh(proposal)


def _handler_response(
    *,
    step_status: str,
    output: dict[str, Any],
    context_updates: dict[str, Any] | None = None,
    lifecycle_status: str | None = None,
    requires_approval: bool = False,
    required_role: str | None = None,
    requires_clarification: bool = False,
    clarification_prompt: str | None = None,
    clarification_fields: list[str] | None = None,
    error_message: str | None = None,
) -> dict[str, Any]:
    return {
        "step_status": step_status,
        "output": output,
        "context_updates": context_updates or {},
        "lifecycle_status": lifecycle_status,
        "requires_approval": requires_approval,
        "required_role": required_role,
        "requires_clarification": requires_clarification,
        "clarification_prompt": clarification_prompt,
        "clarification_fields": clarification_fields or [],
        "error_message": error_message,
    }


# -----------------------------------------------------------------------------
# VALIDATION HANDLER
# -----------------------------------------------------------------------------

@register_workflow_handler(HANDLER_KEY_MALONE_VALIDATE_ACTION)
def handle_malone_validate_action(
    db: Session,
    instance: WorkflowInstance,
    step: WorkflowStepDefinition,
    context: dict[str, Any],
) -> dict[str, Any]:

    actor = _get_actor(context)
    role_name = context.get("role_name")
    action_key = context.get("action_key")
    proposal_id = context.get("proposal_id")

    proposal = _get_proposal(db, proposal_id)

    if not action_key:
        action_validation = {"skipped": True, "is_valid": True}
    else:
        action_validation = validate_action(
            action_key=action_key,
            actor=actor,
            role_name=role_name,
        )

    if proposal:
        _persist_proposal(
            db,
            proposal,
            execution_status="proposal_only"
            if action_validation.get("is_valid")
            else WORKFLOW_STATUS_BLOCKED,
            validation_payload={"action_validation": action_validation},
        )

        log_malone_action(
            db,
            action="malone.proposal.workflow_validated",
            proposal_id=proposal.id,
            actor=actor,
            meta_json={"action_validation": action_validation},
        )

    if not action_validation.get("is_valid"):
        return _handler_response(
            step_status=STEP_STATUS_BLOCKED,
            lifecycle_status=WORKFLOW_STATUS_BLOCKED,
            output={"action_validation": action_validation},
            context_updates={
                "action_validation": action_validation,
                "execution_status": WORKFLOW_STATUS_BLOCKED,
            },
            error_message="; ".join(action_validation.get("reasons", [])),
        )

    return _handler_response(
        step_status=STEP_STATUS_COMPLETED,
        output={"action_validation": action_validation},
        context_updates={"action_validation": action_validation},
        requires_approval=bool(action_validation.get("requires_approval")),
        required_role=action_validation.get("required_role") or "admin",
        requires_clarification=bool(action_validation.get("requires_clarification")),
        clarification_prompt=action_validation.get("clarification_prompt"),
        clarification_fields=action_validation.get("clarification_fields", []),
    )


# -----------------------------------------------------------------------------
# EXECUTION HANDLER
# -----------------------------------------------------------------------------

@register_workflow_handler(HANDLER_KEY_MALONE_EXECUTE_ACTION)
def handle_malone_execute_action(
    db: Session,
    instance: WorkflowInstance,
    step: WorkflowStepDefinition,
    context: dict[str, Any],
) -> dict[str, Any]:

    actor = _get_actor(context)
    role_name = context.get("role_name")
    action_key = context.get("action_key")
    proposal_id = context.get("proposal_id")

    proposal = _get_proposal(db, proposal_id)

    if not action_key:
        if proposal:
            _persist_proposal(db, proposal, execution_status="proposal_only")

        return _handler_response(
            step_status=STEP_STATUS_COMPLETED,
            output={"execution_status": "proposal_only"},
            context_updates={"execution_status": "proposal_only"},
        )

    actor_ctx = SimpleNamespace(
        id=actor.get("id"),
        email=actor.get("email"),
        department=actor.get("department"),
        role=actor.get("role") or role_name,
    )

    execution = execute_action(
        action_key=action_key,
        context={"db": db, "actor": actor_ctx, "role_name": role_name},
    )

    success = bool(execution.get("success"))
    result = execution.get("result") if success else None

    status = "executed" if success else WORKFLOW_STATUS_BLOCKED

    if proposal:
        _persist_proposal(db, proposal, execution_status=status)

        log_malone_action(
            db,
            action="malone.proposal.executed" if success else "malone.proposal.failed",
            proposal_id=proposal.id,
            actor=actor,
            meta_json={"execution_status": status},
        )

    if not success:
        return _handler_response(
            step_status=STEP_STATUS_BLOCKED,
            lifecycle_status=WORKFLOW_STATUS_BLOCKED,
            output={"execution": execution},
            context_updates={"execution": execution},
            error_message=execution.get("message"),
        )

    return _handler_response(
        step_status=STEP_STATUS_COMPLETED,
        output={"execution": execution, "result": result},
        context_updates={"execution": execution, "result": result},
    )


# -----------------------------------------------------------------------------
# FINALIZATION HANDLER
# -----------------------------------------------------------------------------

@register_workflow_handler(HANDLER_KEY_WORKFLOW_MARK_COMPLETE)
def handle_workflow_mark_complete(
    db: Session,
    instance: WorkflowInstance,
    step: WorkflowStepDefinition,
    context: dict[str, Any],
) -> dict[str, Any]:

    actor = _get_actor(context)
    proposal_id = context.get("proposal_id")

    proposal = _get_proposal(db, proposal_id)

    if proposal:
        log_malone_action(
            db,
            action="malone.workflow.completed",
            proposal_id=proposal.id,
            actor=actor,
            meta_json={
                "workflow_instance_id": instance.id,
                "execution_status": context.get("execution_status"),
            },
        )

    return _handler_response(
        step_status=STEP_STATUS_COMPLETED,
        lifecycle_status=WORKFLOW_STATUS_COMPLETED,
        output={"workflow_instance_id": instance.id},
        context_updates={"workflow_instance_id": instance.id},
    )