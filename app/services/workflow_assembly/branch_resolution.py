"""Collect branch/exception strings from extraction (no execution engine)."""

from __future__ import annotations

from typing import Any


def collect_branch_hints(action_steps: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for s in action_steps:
        ex = s.get("workflow_extraction") or {}
        for b in ex.get("branch_conditions") or []:
            t = (b.get("branch_condition_text") or "").strip()
            if t:
                out.append(t)
    return out[:25]
