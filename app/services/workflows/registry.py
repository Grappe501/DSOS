from __future__ import annotations
from typing import Any, Callable
from app.services.workflows.constants import get_required_builtin_handler_keys
from app.services.workflows.json_utils import normalize_str
WorkflowHandler = Callable[[Any, Any, Any, dict[str, Any]], dict[str, Any]]
_WORKFLOW_HANDLERS: dict[str, WorkflowHandler] = {}
def _normalize_step_key(step_key: str) -> str:
    normalized = normalize_str(step_key)
    if not normalized:
        raise ValueError("workflow step_key is required")
    return normalized
def register_workflow_handler(step_key: str, *, allow_overwrite: bool = False):
    normalized_step_key = _normalize_step_key(step_key)
    def decorator(func: WorkflowHandler) -> WorkflowHandler:
        existing = _WORKFLOW_HANDLERS.get(normalized_step_key)
        if existing is not None and existing is not func and not allow_overwrite:
            raise ValueError(f"workflow handler already registered for step_key '{normalized_step_key}'")
        _WORKFLOW_HANDLERS[normalized_step_key] = func
        return func
    return decorator
def list_workflow_handlers() -> list[str]:
    return sorted(_WORKFLOW_HANDLERS.keys())
def get_workflow_handler(step_key: str) -> WorkflowHandler | None:
    normalized_step_key = normalize_str(step_key)
    return _WORKFLOW_HANDLERS.get(normalized_step_key) if normalized_step_key else None
def verify_required_workflow_handlers(required_keys: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    required = [k for k in (required_keys or get_required_builtin_handler_keys()) if normalize_str(k)]
    missing = [key for key in required if key not in _WORKFLOW_HANDLERS]
    return {"ok": len(missing) == 0, "required_handlers": list(required), "missing_required_handlers": missing, "registered_handler_count": len(_WORKFLOW_HANDLERS)}
