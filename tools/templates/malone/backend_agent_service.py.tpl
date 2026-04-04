"""{generated_note} - Malone agent lifecycle service."""
from __future__ import annotations

from typing import Any


def spawn_agent(agent_type: str, goal: str, scope: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Malone sub-agents are bounded worker processes.
    This v1 scaffold returns a normalized agent run envelope.
    """
    return {{
        "agent_type": agent_type,
        "goal": goal,
        "scope": scope or {{}},
        "status": "planned",
    }}
