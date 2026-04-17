"""Feature flags for scenario memory (secondary; never overrides evidence)."""

from __future__ import annotations

import os


def malone_scenario_memory_enabled() -> bool:
    v = os.environ.get("MALONE_SCENARIO_MEMORY_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    from app.services.decision_reasoning.fallback import malone_decision_reasoning_enabled

    return malone_decision_reasoning_enabled()


def malone_scenario_memory_priors_enabled() -> bool:
    """Load prior analogs into truth packet (review-only context)."""
    v = os.environ.get("MALONE_SCENARIO_MEMORY_PRIORS_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return malone_scenario_memory_enabled()


def should_persist_trace_for_delivery(*, delivery_status: str | None) -> bool:
    """Skip persistence for blocked approval gate (optional tightening)."""
    if delivery_status == "approval_required":
        return False
    return True
