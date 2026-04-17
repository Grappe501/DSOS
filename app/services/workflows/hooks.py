from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.orm import Session

from app.models.models import WorkflowInstance, WorkflowStepDefinition
from app.services.workflows.constants import (
    WORKFLOW_STATUS_BLOCKED_PENDING_APPROVAL,
    WORKFLOW_STATUS_BLOCKED_PENDING_CLARIFICATION,
)


def handle_required_approval(
    db: Session,
    *,
    set_instance_state: Callable[..., WorkflowInstance],
    audit_workflow_instance: Callable[..., None],
    actor_from_context: Callable[[dict[str, Any] | None], dict[str, Any]],
    instance: WorkflowInstance,
    step: WorkflowStepDefinition,
    context: dict[str, Any],
    required_role: str,
    output_payload: dict[str, Any],
) -> WorkflowInstance:
    from app.services.approval_service import create_approval_request

    actor = actor_from_context(context)

    approval_context = {
        "workflow_instance_id": instance.id,
        "workflow_step_id": step.id,
        "workflow_step_name": step.name,
        "workflow_step_key": step.step_key,
        "entity_type": instance.entity_type,
        "entity_id": instance.entity_id,
        "context": context,
        "output": output_payload,
    }

    create_approval_request(
        db,
        workflow_instance=instance,
        required_role=required_role,
        context=approval_context,
    )

    set_instance_state(
        db,
        instance=instance,
        status=WORKFLOW_STATUS_BLOCKED_PENDING_APPROVAL,
        current_step_id=step.id,
        last_error=None,
        mark_completed=False,
    )

    audit_workflow_instance(
        db,
        action="workflow.blocked_for_approval",
        instance=instance,
        actor_user_id=actor.get("id"),
        meta_json={
            "required_role": required_role,
            "step_id": step.id,
            "step_name": step.name,
            "step_key": step.step_key,
        },
    )

    return instance


def handle_required_clarification(
    db: Session,
    *,
    set_instance_state: Callable[..., WorkflowInstance],
    audit_workflow_instance: Callable[..., None],
    actor_from_context: Callable[[dict[str, Any] | None], dict[str, Any]],
    instance: WorkflowInstance,
    step: WorkflowStepDefinition,
    context: dict[str, Any],
    clarification_prompt: str,
    clarification_fields: list[str],
    output_payload: dict[str, Any],
) -> WorkflowInstance:
    from app.services.clarification_service import create_clarification_request

    actor = actor_from_context(context)

    clarification_context = {
        "workflow_instance_id": instance.id,
        "workflow_step_id": step.id,
        "workflow_step_name": step.name,
        "workflow_step_key": step.step_key,
        "entity_type": instance.entity_type,
        "entity_id": instance.entity_id,
        "context": context,
        "output": output_payload,
    }

    create_clarification_request(
        db,
        workflow_instance=instance,
        prompt=clarification_prompt,
        fields=clarification_fields,
        context=clarification_context,
    )

    set_instance_state(
        db,
        instance=instance,
        status=WORKFLOW_STATUS_BLOCKED_PENDING_CLARIFICATION,
        current_step_id=step.id,
        last_error=None,
        mark_completed=False,
    )

    audit_workflow_instance(
        db,
        action="workflow.blocked_for_clarification",
        instance=instance,
        actor_user_id=actor.get("id"),
        meta_json={
            "step_id": step.id,
            "step_name": step.name,
            "step_key": step.step_key,
            "clarification_prompt": clarification_prompt,
            "clarification_fields": clarification_fields,
        },
    )

    return instance