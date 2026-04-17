"""Enable / disable gates and safe downgrade for the operating copilot layer."""

from __future__ import annotations

from typing import Any


def malone_operating_copilot_enabled() -> bool:
    import os

    v = os.environ.get("MALONE_OPERATING_COPILOT_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    from app.services.decision_reasoning.fallback import malone_decision_reasoning_enabled

    return malone_decision_reasoning_enabled()


def should_emit_operating_copilot_section(block: dict[str, Any] | None) -> bool:
    if not block or not block.get("enabled"):
        return False
    if block.get("fallback_reason") and block.get("emit_minimal_only"):
        return True
    if block.get("fallback_reason"):
        return False
    return True


def should_build_copilot_body(block: dict[str, Any] | None) -> bool:
    """Full structured section vs skip entirely."""
    if not block or not block.get("enabled"):
        return False
    if block.get("fallback_reason"):
        return False
    return True
