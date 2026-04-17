from __future__ import annotations
from typing import Any
from app.models.models import WorkflowInstance
from app.services.workflows.json_utils import actor_from_context as _actor_from_context, coerce_json_dict, merge_context_dict, safe_json
def actor_from_context(context: dict[str, Any] | None) -> dict[str, Any]:
    return _actor_from_context(context)
def merge_instance_context(instance: WorkflowInstance, updates: dict[str, Any] | None) -> dict[str, Any]:
    context = coerce_json_dict(instance.context_json)
    merged = merge_context_dict(context, updates or {})
    instance.context_json = safe_json(merged)
    return merged
