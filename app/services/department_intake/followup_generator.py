"""Deterministic follow-up questions from missing / thin profile fields."""

from __future__ import annotations

import json
from typing import Any


def _profile(state: dict[str, Any]) -> dict[str, Any]:
    p = state.get("profile")
    return p if isinstance(p, dict) else {}


def _non_empty(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, str):
        return bool(val.strip())
    if isinstance(val, (list, tuple, dict)):
        return len(val) > 0
    return True


def compute_followup_questions(state: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Return inspectable follow-up objects:
    {reason, target_field, question_text, priority}
    """
    p = _profile(state)
    out: list[dict[str, Any]] = []

    def add(reason: str, target: str, text: str, priority: int) -> None:
        out.append(
            {
                "reason": reason,
                "target_field": target,
                "question_text": text,
                "priority": priority,
            }
        )

    if not _non_empty(p.get("mission")):
        add("mission_missing", "profile.mission", "What is the department's primary purpose in one or two sentences?", 1)
    if not _non_empty(p.get("roles")):
        add("owner_unknown", "profile.roles", "Who owns which major responsibilities (roles or titles)?", 2)
    if not _non_empty(p.get("workflows")):
        add("workflow_gap", "profile.workflows", "What are the top recurring workflows or processes?", 3)
    if not _non_empty(p.get("systems")):
        add("no_system_named", "profile.systems", "What systems or tools are used for the main workflows?", 4)
    if not (_non_empty(p.get("inputs")) and _non_empty(p.get("outputs"))):
        add("io_undefined", "profile.inputs_outputs", "What are the key inputs and outputs of this department?", 4)
    if not _non_empty(p.get("depends_on")) and not _non_empty(p.get("dependents")):
        add("dependency_unknown", "profile.dependencies", "Who does this department depend on, and who depends on it?", 5)
    if not _non_empty(p.get("handoffs")):
        add("no_handoff", "profile.handoffs", "Where are handoffs to other teams, and what is exchanged?", 5)
    if not _non_empty(p.get("escalation")):
        add("no_escalation", "profile.escalation", "When do you escalate, and to whom?", 6)
    if not _non_empty(p.get("blockers")):
        add("no_blocker_named", "profile.blockers", "What common blockers or exceptions should be captured?", 6)
    if not _non_empty(p.get("sop_refs")):
        add("no_sop_named", "profile.sop_refs", "Is there a written SOP or policy name we should reference?", 7)

    out.sort(key=lambda x: (x["priority"], x["target_field"]))
    return out


def state_from_json(raw: str | None) -> dict[str, Any]:
    if not raw or not str(raw).strip():
        return default_state()
    try:
        d = json.loads(raw)
        return d if isinstance(d, dict) else default_state()
    except json.JSONDecodeError:
        return default_state()


def default_state() -> dict[str, Any]:
    return {
        "profile": {
            "mission": "",
            "responsibilities": [],
            "roles": [],
            "workflows": [],
            "systems": [],
            "inputs": "",
            "outputs": "",
            "depends_on": [],
            "dependents": [],
            "handoffs": [],
            "escalation": "",
            "blockers": [],
            "sop_refs": [],
            "metrics": "",
        },
        "parser_version": 1,
        "uncertainty_note": "Draft intake map; not asserted complete.",
    }
