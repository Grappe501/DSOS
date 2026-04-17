from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.models import WorkflowInstance
from app.services.workflows.constants import (
    STEP_STATUS_COMPLETED,
    STEP_STATUS_FAILED,
    WORKFLOW_STATUS_BLOCKED,
    WORKFLOW_STATUS_BLOCKED_PENDING_APPROVAL,
    WORKFLOW_STATUS_BLOCKED_PENDING_CLARIFICATION,
    WORKFLOW_STATUS_COMPLETED,
    WORKFLOW_STATUS_FAILED,
    WORKFLOW_STATUS_IN_PROGRESS,
    WORKFLOW_STATUS_PENDING,
)
from app.services.workflows.engine_parts.audit import audit_workflow_instance
from app.services.workflows.engine_parts.context import (
    actor_from_context,
    merge_instance_context,
)
from app.services.workflows.engine_parts.persistence import (
    set_instance_state,
    write_step_execution,
)
from app.services.workflows.engine_parts.queries import (
    get_workflow_definition_for_execution,
    get_workflow_instance,
    get_workflow_step,
)
from app.services.workflows.hooks import (
    handle_required_approval,
    handle_required_clarification,
)
from app.services.workflows.json_utils import (
    coerce_json_dict,
    safe_json,
    utcnow,
)
from app.services.workflows.registry import get_workflow_handler
from app.services.workflows.state_helpers import mark_workflow_state


# -----------------------------------------------------------------------------
# Safety
# -----------------------------------------------------------------------------

MAX_WORKFLOW_STEPS = 100


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def start_workflow_instance(
    db: Session,
    *,
    workflow_name: str,
    context: dict,
    entity_type: str | None = None,
    entity_id: str | None = None,
    version: str | None = None,
    auto_run: bool = True,
) -> WorkflowInstance:

    definition = get_workflow_definition_for_execution(
        db,
        name=workflow_name,
        version=version,
    )

    instance = WorkflowInstance(
        workflow_definition_id=definition.id,
        entity_type=entity_type,
        entity_id=entity_id,
        status=WORKFLOW_STATUS_PENDING,
        current_step_id=definition.entry_step_id,
        context_json=safe_json(context),
        started_at=utcnow(),
    )

    db.add(instance)
    db.commit()
    db.refresh(instance)

    actor = actor_from_context(context)

    if entity_type and entity_id:
        mark_workflow_state(
            db,
            workflow_name=workflow_name,
            entity_type=entity_type,
            entity_id=entity_id,
            state="workflow_started",
            status="active",
            actor_user_id=actor.get("id"),
            department=actor.get("department"),
            meta_json={
                "workflow_instance_id": instance.id,
                "workflow_definition_id": definition.id,
                "workflow_version": definition.version,
            },
        )

    audit_workflow_instance(
        db,
        action="workflow.instance.created",
        instance=instance,
        actor_user_id=actor.get("id"),
        meta_json={
            "workflow_name": workflow_name,
            "workflow_version": definition.version,
        },
    )

    return run_workflow_instance(db, workflow_instance_id=instance.id) if auto_run else instance


def resume_workflow_instance(
    db: Session,
    *,
    workflow_instance_id: str,
    context_updates: dict | None = None,
) -> WorkflowInstance:

    instance = get_workflow_instance(db, workflow_instance_id)
    if not instance:
        raise ValueError(f"Workflow instance '{workflow_instance_id}' not found")

    current_context = coerce_json_dict(instance.context_json)

    if context_updates:
        merge_instance_context(instance, context_updates)
        db.add(instance)
        db.commit()
        db.refresh(instance)

    if instance.status not in {
        WORKFLOW_STATUS_PENDING,
        WORKFLOW_STATUS_IN_PROGRESS,
        WORKFLOW_STATUS_BLOCKED,
        WORKFLOW_STATUS_BLOCKED_PENDING_APPROVAL,
        WORKFLOW_STATUS_BLOCKED_PENDING_CLARIFICATION,
    }:
        raise ValueError(f"Workflow instance '{workflow_instance_id}' not resumable")

    if not instance.current_step_id:
        raise ValueError("Cannot resume without current_step_id")

    instance.status = WORKFLOW_STATUS_PENDING
    instance.last_error = None

    db.add(instance)
    db.commit()
    db.refresh(instance)

    audit_workflow_instance(
        db,
        action="workflow.instance.resumed",
        instance=instance,
        actor_user_id=actor_from_context(current_context).get("id"),
        meta_json={"status": instance.status},
    )

    return run_workflow_instance(db, workflow_instance_id=instance.id)


# -----------------------------------------------------------------------------
# Core Engine Loop
# -----------------------------------------------------------------------------

def run_workflow_instance(
    db: Session,
    *,
    workflow_instance_id: str,
) -> WorkflowInstance:

    instance = get_workflow_instance(db, workflow_instance_id)
    if not instance:
        raise ValueError("Workflow instance not found")

    step_counter = 0

    while instance.status in {WORKFLOW_STATUS_PENDING, WORKFLOW_STATUS_IN_PROGRESS}:

        step_counter += 1
        if step_counter > MAX_WORKFLOW_STEPS:
            return _fail_workflow(
                db,
                instance,
                error="Max workflow steps exceeded",
            )

        if not instance.current_step_id:
            return _complete_workflow(db, instance)

        step = get_workflow_step(db, instance.current_step_id)
        if not step:
            return _fail_workflow(
                db,
                instance,
                error="Missing step definition",
            )

        handler = get_workflow_handler(step.step_key)
        if not handler:
            return _fail_workflow(
                db,
                instance,
                error=f"No handler for '{step.step_key}'",
            )

        input_payload = coerce_json_dict(instance.context_json)

        set_instance_state(
            db,
            instance=instance,
            status=WORKFLOW_STATUS_IN_PROGRESS,
            current_step_id=instance.current_step_id,
            last_error=None,
            mark_completed=False,
        )

        try:
            response = handler(db, instance, step, input_payload) or {}
        except Exception as exc:
            return _fail_step(db, instance, step, input_payload, str(exc))

        normalized = _normalize_handler_response(response)

        merged_context = merge_instance_context(
            instance,
            normalized["context_updates"],
        )

        actor = actor_from_context(merged_context)

        write_step_execution(
            db,
            workflow_instance_id=instance.id,
            step_id=step.id,
            status=normalized["step_status"],
            input_payload=input_payload,
            output_payload=normalized["output"],
            error_message=normalized["error_message"],
        )

        audit_workflow_instance(
            db,
            action="workflow.step.executed",
            instance=instance,
            actor_user_id=actor.get("id"),
            meta_json={"step_key": step.step_key},
        )

        # --- BLOCKING CONDITIONS ---

        if normalized["requires_clarification"]:
            return handle_required_clarification(
                db,
                set_instance_state=set_instance_state,
                audit_workflow_instance=audit_workflow_instance,
                actor_from_context=actor_from_context,
                instance=instance,
                step=step,
                context=merged_context,
                clarification_prompt=normalized["clarification_prompt"],
                clarification_fields=normalized["clarification_fields"],
                output_payload=normalized["output"],
            )

        if normalized["requires_approval"]:
            return handle_required_approval(
                db,
                set_instance_state=set_instance_state,
                audit_workflow_instance=audit_workflow_instance,
                actor_from_context=actor_from_context,
                instance=instance,
                step=step,
                context=merged_context,
                required_role=normalized["required_role"],
                output_payload=normalized["output"],
            )

        # --- TERMINATION ---

        if step.is_terminal:
            return _complete_workflow(db, instance)

        # --- NEXT STEP ---

        if normalized["next_step_id"]:
            set_instance_state(
                db,
                instance=instance,
                status=WORKFLOW_STATUS_IN_PROGRESS,
                current_step_id=normalized["next_step_id"],
                last_error=None,
                mark_completed=False,
            )
            instance = get_workflow_instance(db, instance.id)
            continue

        return _complete_workflow(db, instance)

    return instance


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _normalize_handler_response(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "step_status": response.get("step_status") or STEP_STATUS_COMPLETED,
        "output": response.get("output") or {},
        "context_updates": response.get("context_updates") or {},
        "error_message": response.get("error_message"),
        "requires_approval": bool(response.get("requires_approval")),
        "required_role": response.get("required_role") or "admin",
        "requires_clarification": bool(response.get("requires_clarification")),
        "clarification_prompt": response.get("clarification_prompt")
        or "Please clarify your request.",
        "clarification_fields": response.get("clarification_fields") or [],
        "next_step_id": response.get("next_step_id"),
    }


def _fail_step(
    db: Session,
    instance: WorkflowInstance,
    step,
    input_payload,
    error: str,
) -> WorkflowInstance:

    set_instance_state(
        db,
        instance=instance,
        status=WORKFLOW_STATUS_FAILED,
        current_step_id=None,
        last_error=error,
        mark_completed=True,
    )

    write_step_execution(
        db,
        workflow_instance_id=instance.id,
        step_id=step.id,
        status=STEP_STATUS_FAILED,
        input_payload=input_payload,
        output_payload={},
        error_message=error,
    )

    return instance


def _fail_workflow(
    db: Session,
    instance: WorkflowInstance,
    *,
    error: str,
) -> WorkflowInstance:

    set_instance_state(
        db,
        instance=instance,
        status=WORKFLOW_STATUS_FAILED,
        current_step_id=None,
        last_error=error,
        mark_completed=True,
    )

    return instance


def _complete_workflow(
    db: Session,
    instance: WorkflowInstance,
) -> WorkflowInstance:

    set_instance_state(
        db,
        instance=instance,
        status=WORKFLOW_STATUS_COMPLETED,
        current_step_id=None,
        last_error=None,
        mark_completed=True,
    )

    return instance