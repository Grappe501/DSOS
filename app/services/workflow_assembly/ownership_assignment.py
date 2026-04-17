"""Merge normalized applies_to_role with regex role hints (explicit priority to unit field)."""

from __future__ import annotations

from typing import Any


def merge_step_ownership(step: dict[str, Any]) -> dict[str, Any]:
    base = (step.get("applies_to_role") or "").strip()
    ex = step.get("workflow_extraction") or {}
    hints = ex.get("role_hints") or []
    if base:
        step["ownership_resolved"] = base
        step["ownership_source"] = "normalized_unit"
        return step
    if hints:
        step["applies_to_role"] = hints[0].get("role_key")
        step["ownership_resolved"] = step["applies_to_role"]
        step["ownership_source"] = "text_extraction"
        return step
    step["ownership_resolved"] = None
    step["ownership_source"] = "unknown"
    return step
