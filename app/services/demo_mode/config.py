"""Demo readiness flags (env). Does not change legal grounding — presentation and retrieval hints only."""

from __future__ import annotations

import os


def _truthy(val: str | None) -> bool:
    return (val or "").strip().lower() in ("1", "true", "yes", "on")


def demo_mode_active() -> bool:
    return _truthy(os.environ.get("MALONE_DEMO_MODE"))


def demo_safe_responses() -> bool:
    """Prefer tighter formatting and fewer noisy disclaimers (cosmetic)."""
    return _truthy(os.environ.get("MALONE_DEMO_SAFE_RESPONSES"))


def demo_limited_scope() -> bool:
    """Disable web search augmentation for conversational render path when possible."""
    return _truthy(os.environ.get("MALONE_DEMO_LIMITED_SCOPE"))


def demo_config_payload() -> dict[str, object]:
    return {
        "malone_demo_mode": demo_mode_active(),
        "malone_demo_safe_responses": demo_safe_responses(),
        "malone_demo_limited_scope": demo_limited_scope(),
    }
