"""Lightweight operational intent classification (keyword heuristics, not a second agent)."""

from __future__ import annotations


def classify_operational_intent(message: str) -> str:
    """
    Returns one of: step_by_step | escalation_focus | lookup

    Drives section emphasis only; does not change evidence retrieval.
    """
    m = (message or "").strip().lower()
    if not m:
        return "lookup"
    esc = ("escalat", "supervisor", "notify", "report to", "chain of command", "stop and")
    if any(x in m for x in esc):
        return "escalation_focus"
    step = (
        "what should we do",
        "what should i do",
        "steps",
        "workflow",
        "procedure",
        "how do we",
        "how should",
        "checklist",
        "who should",
        "runbook",
        "playbook",
    )
    if any(x in m for x in step):
        return "step_by_step"
    return "lookup"
