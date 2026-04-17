"""Tiny keyword classifier for routing answers (deterministic)."""

from __future__ import annotations


def classify_answer_lane(text: str) -> str:
    low = (text or "").lower()
    if any(k in low for k in ("escalat", "manager", "on-call")):
        return "escalation"
    if any(k in low for k in ("handoff", "transfer", "send to")):
        return "handoff"
    if any(k in low for k in ("depends on", "upstream", "vendor")):
        return "dependency"
    return "general"
