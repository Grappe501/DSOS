from __future__ import annotations

"""
Workflow service facade.

Purpose:
- preserve the long-lived import path: `app.services.workflow_service`
- provide a stable compatibility layer while workflow internals live in
  `app.services.workflows.*`
- keep workflow implementation split across focused modules

CRITICAL RULES:
- DO NOT add execution logic here
- DO NOT add handlers here
- DO NOT add workflow state logic here
- ONLY re-export stable public API

This file is a SYSTEM FACADE — not an implementation layer.
"""

from typing import Any


# -----------------------------------------------------------------------------
# Safe imports (fail loudly but clearly)
# -----------------------------------------------------------------------------

try:
    # -------------------------------------------------------------------------
    # Constants
    # -------------------------------------------------------------------------
    from app.services.workflows.constants import (
        DEFAULT_WORKFLOW_NAME,
        DEFAULT_WORKFLOW_VERSION,
        STEP_STATUS_BLOCKED,
        STEP_STATUS_COMPLETED,
        STEP_STATUS_FAILED,
        STEP_STATUS_PENDING,
        WORKFLOW_ENTITY_TYPE,
        WORKFLOW_STATUS_BLOCKED,
        WORKFLOW_STATUS_BLOCKED_PENDING_APPROVAL,
        WORKFLOW_STATUS_BLOCKED_PENDING_CLARIFICATION,
        WORKFLOW_STATUS_COMPLETED,
        WORKFLOW_STATUS_FAILED,
        WORKFLOW_STATUS_IN_PROGRESS,
        WORKFLOW_STATUS_PENDING,
        get_required_builtin_handler_keys,
    )

    # -------------------------------------------------------------------------
    # Registry
    # -------------------------------------------------------------------------
    from app.services.workflows.registry import (
        WorkflowHandler,
        get_workflow_handler,
        list_workflow_handlers,
        register_workflow_handler,
        verify_required_workflow_handlers,
    )

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------
    from app.services.workflows.serializers import (
        serialize_workflow_definition,
        serialize_workflow_instance,
        serialize_workflow_step_definition,
        serialize_workflow_step_execution,
    )

    # -------------------------------------------------------------------------
    # Legacy state helpers
    # -------------------------------------------------------------------------
    from app.services.workflows.state_helpers import (
        get_entity_workflow_history,
        mark_workflow_state,
        route_conflict_resolution,
        start_schedule_workflow,
        transition_schedule_state,
    )

    # -------------------------------------------------------------------------
    # Definitions
    # -------------------------------------------------------------------------
    from app.services.workflows.definitions import (
        ensure_workflow_seed_data,
        list_workflow_definitions,
    )

    # -------------------------------------------------------------------------
    # Engine
    # -------------------------------------------------------------------------
    from app.services.workflows.engine import (
        get_workflow_instance,
        list_workflow_instances,
        resume_workflow_instance,
        run_workflow_instance,
        start_workflow_instance,
    )

except Exception as e:
    raise RuntimeError(
        "Workflow system failed to initialize. "
        "Ensure app/services/workflows package is fully installed and valid."
    ) from e


# -----------------------------------------------------------------------------
# Bootstrap
# -----------------------------------------------------------------------------

def bootstrap_workflow_handlers() -> None:
    """
    Import built-in workflow handlers so registry decorators execute.

    Safe to call multiple times.
    """
    try:
        from app.services.workflows import handlers_malone as _handlers_malone  # noqa: F401
    except Exception as e:
        raise RuntimeError("Failed to bootstrap workflow handlers") from e


# -----------------------------------------------------------------------------
# Diagnostics
# -----------------------------------------------------------------------------

def get_workflow_public_api() -> dict[str, Any]:
    """
    Introspection helper for system diagnostics.
    """
    return {
        "workflow_name": DEFAULT_WORKFLOW_NAME,
        "workflow_version": DEFAULT_WORKFLOW_VERSION,
        "entity_type": WORKFLOW_ENTITY_TYPE,
        "handler_count": len(list_workflow_handlers()),
        "handlers": list_workflow_handlers(),
    }


def verify_workflow_package_health() -> dict[str, Any]:
    """
    Full workflow system verification.

    Validates:
    - handler registry
    - required handlers present
    - facade wiring is correct
    """
    bootstrap_workflow_handlers()

    registry_check = verify_required_workflow_handlers()
    required_handlers = get_required_builtin_handler_keys()

    return {
        "ok": registry_check["ok"],
        "required_handlers": required_handlers,
        "missing_required_handlers": registry_check["missing_required_handlers"],
        "registered_handler_count": registry_check["registered_handler_count"],
        "registered_handlers": list_workflow_handlers(),
    }


# -----------------------------------------------------------------------------
# Boot
# -----------------------------------------------------------------------------

# Ensure handlers are registered immediately
bootstrap_workflow_handlers()


# -----------------------------------------------------------------------------
# Public API Contract
# -----------------------------------------------------------------------------

__all__ = [
    # constants
    "DEFAULT_WORKFLOW_NAME",
    "DEFAULT_WORKFLOW_VERSION",
    "WORKFLOW_ENTITY_TYPE",
    "WORKFLOW_STATUS_PENDING",
    "WORKFLOW_STATUS_IN_PROGRESS",
    "WORKFLOW_STATUS_COMPLETED",
    "WORKFLOW_STATUS_FAILED",
    "WORKFLOW_STATUS_BLOCKED",
    "WORKFLOW_STATUS_BLOCKED_PENDING_APPROVAL",
    "WORKFLOW_STATUS_BLOCKED_PENDING_CLARIFICATION",
    "STEP_STATUS_PENDING",
    "STEP_STATUS_COMPLETED",
    "STEP_STATUS_BLOCKED",
    "STEP_STATUS_FAILED",

    # registry
    "WorkflowHandler",
    "register_workflow_handler",
    "list_workflow_handlers",
    "get_workflow_handler",

    # serializers
    "serialize_workflow_step_definition",
    "serialize_workflow_step_execution",
    "serialize_workflow_definition",
    "serialize_workflow_instance",

    # legacy helpers
    "mark_workflow_state",
    "start_schedule_workflow",
    "route_conflict_resolution",
    "transition_schedule_state",
    "get_entity_workflow_history",

    # definitions
    "ensure_workflow_seed_data",
    "list_workflow_definitions",

    # engine
    "list_workflow_instances",
    "get_workflow_instance",
    "start_workflow_instance",
    "resume_workflow_instance",
    "run_workflow_instance",

    # diagnostics
    "bootstrap_workflow_handlers",
    "get_workflow_public_api",
    "verify_workflow_package_health",
]