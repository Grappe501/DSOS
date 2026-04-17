"""Optional merge of embedded numbered substeps into display order hints (non-destructive)."""

from __future__ import annotations

from typing import Any


def attach_embedded_substep_count(action_steps: list[dict[str, Any]]) -> None:
    """Mutates steps in place: sets embedded_substep_count from extraction."""
    for s in action_steps:
        ex = s.get("workflow_extraction") or {}
        ns = ex.get("numbered_steps") or []
        if ns:
            s["embedded_substep_count"] = len(ns)
