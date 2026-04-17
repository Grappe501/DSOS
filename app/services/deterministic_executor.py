from __future__ import annotations

import time
from typing import Any

from app.services.deterministic_registry import get_action


def execute_action(
    *,
    action_key: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    started_at = time.time()
    action = get_action(action_key)

    if not action:
        return {
            "success": False,
            "action_key": action_key,
            "entity_type": None,
            "target": None,
            "read_only": False,
            "requires_approval": False,
            "error_code": "action_not_registered",
            "message": f"Action '{action_key}' is not registered",
            "result": None,
            "duration_ms": int((time.time() - started_at) * 1000),
        }

    try:
        result = action.executor(**context)
        return {
            "success": True,
            "action_key": action.action_key,
            "entity_type": action.entity_type,
            "target": action.target,
            "read_only": action.read_only,
            "requires_approval": action.requires_approval,
            "error_code": None,
            "message": None,
            "result": result,
            "duration_ms": int((time.time() - started_at) * 1000),
        }
    except Exception as exc:
        return {
            "success": False,
            "action_key": action.action_key,
            "entity_type": action.entity_type,
            "target": action.target,
            "read_only": action.read_only,
            "requires_approval": action.requires_approval,
            "error_code": "execution_failed",
            "message": str(exc),
            "result": None,
            "duration_ms": int((time.time() - started_at) * 1000),
        }