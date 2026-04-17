"""When smart patterns downgrade to the standard citation-first shape."""

from __future__ import annotations

from typing import Any


def malone_smart_answer_patterns_enabled() -> bool:
    import os

    v = os.environ.get("MALONE_SMART_ANSWER_PATTERNS_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return True


def should_fallback_to_standard_pattern(
    *,
    pattern_id: str,
    confidence: str,
    items: list[dict[str, Any]],
    normalized_units: list[dict[str, Any]],
) -> bool:
    """
    Safe downgrade: weak evidence or conflicting signals -> use standard formatter only.

    confidence is 'high' | 'medium' | 'low' from selector.
    """
    if confidence == "low":
        return True
    if not items:
        return True
    # Workflow / requirement patterns need some normalized support to avoid hollow sections
    if pattern_id in ("requirement", "workflow", "exception") and not normalized_units:
        if confidence != "high":
            return True
    return False
