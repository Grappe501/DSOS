from __future__ import annotations
from typing import Any
from app.services.workflows.engine_parts.queries import get_workflow_definition_for_execution, get_workflow_instance, get_workflow_step, list_workflow_instances
from app.services.workflows.engine_parts.context import actor_from_context, merge_instance_context
from app.services.workflows.engine_parts.persistence import set_instance_state, write_step_execution
from app.services.workflows.engine_parts.audit import audit_workflow_instance
from app.services.workflows.engine_parts.lifecycle import resume_workflow_instance, run_workflow_instance, start_workflow_instance
def get_engine_public_api() -> dict[str, Any]:
    return {"engine_module": "app.services.workflows.engine", "public_functions": ["list_workflow_instances","get_workflow_instance","get_workflow_step","get_workflow_definition_for_execution","actor_from_context","merge_instance_context","write_step_execution","set_instance_state","audit_workflow_instance","start_workflow_instance","resume_workflow_instance","run_workflow_instance"], "engine_parts": ["queries","context","persistence","audit","lifecycle"]}
def verify_engine_package_health() -> dict[str, Any]:
    required_exports = {"list_workflow_instances": list_workflow_instances, "get_workflow_instance": get_workflow_instance, "get_workflow_step": get_workflow_step, "get_workflow_definition_for_execution": get_workflow_definition_for_execution, "actor_from_context": actor_from_context, "merge_instance_context": merge_instance_context, "write_step_execution": write_step_execution, "set_instance_state": set_instance_state, "audit_workflow_instance": audit_workflow_instance, "start_workflow_instance": start_workflow_instance, "resume_workflow_instance": resume_workflow_instance, "run_workflow_instance": run_workflow_instance}
    missing = [name for name, value in required_exports.items() if value is None]
    return {"ok": len(missing) == 0, "missing_exports": missing, "export_count": len(required_exports), "public_api": get_engine_public_api()}
__all__ = ["list_workflow_instances","get_workflow_instance","get_workflow_step","get_workflow_definition_for_execution","actor_from_context","merge_instance_context","write_step_execution","set_instance_state","audit_workflow_instance","start_workflow_instance","resume_workflow_instance","run_workflow_instance","get_engine_public_api","verify_engine_package_health"]
