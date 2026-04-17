from __future__ import annotations

from typing import Any

from app.services.deterministic_registry import DeterministicAction, register_action
from app.services.schedule_service import list_schedules


MAX_SCHEDULE_ROWS = 100


def _serialize_schedule(row: Any) -> dict[str, Any]:
    return {
        "id": getattr(row, "id", None),
        "title": getattr(row, "title", None),
        "assigned_to": getattr(row, "assigned_to", None),
        "department": getattr(row, "department", None),
        "status": getattr(row, "status", None),
        "start_time": getattr(row, "start_time", None).isoformat()
        if getattr(row, "start_time", None)
        else None,
        "end_time": getattr(row, "end_time", None).isoformat()
        if getattr(row, "end_time", None)
        else None,
    }


def schedule_read_executor(*, db: Any, actor: Any, role_name: str, **_: Any) -> dict[str, Any]:
    rows = list_schedules(
        db,
        actor=actor,
        role_name=role_name,
        department=None,
    )[:MAX_SCHEDULE_ROWS]

    serialized = [_serialize_schedule(row) for row in rows]
    return {
        "type": "schedule_list",
        "count": len(serialized),
        "items": serialized,
    }


def schedule_analyze_executor(*, db: Any, actor: Any, role_name: str, **_: Any) -> dict[str, Any]:
    rows = list_schedules(
        db,
        actor=actor,
        role_name=role_name,
        department=None,
    )[:MAX_SCHEDULE_ROWS]

    counts = {
        "scheduled": 0,
        "draft": 0,
        "submitted": 0,
        "cancelled": 0,
    }

    for row in rows:
        status = getattr(row, "status", None)
        if status in counts:
            counts[status] += 1

    return {
        "type": "schedule_analysis",
        "total": len(rows),
        "by_status": counts,
    }


def register_schedule_actions() -> None:
    register_action(
        DeterministicAction(
            action_key="schedule.read",
            description="Read schedules within deterministic scope",
            entity_type="schedule",
            target="schedules",
            read_only=True,
            requires_approval=False,
            executor=schedule_read_executor,
        )
    )
    register_action(
        DeterministicAction(
            action_key="schedule.analyze",
            description="Analyze schedules within deterministic scope",
            entity_type="schedule",
            target="schedules",
            read_only=True,
            requires_approval=False,
            executor=schedule_analyze_executor,
        )
    )