"""Deterministic confidence labels for normalization (no ML in this pass)."""

from __future__ import annotations

CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"
CONFIDENCE_UNKNOWN = "unknown"

CONFIDENCE_LEVELS = frozenset(
    {CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW, CONFIDENCE_UNKNOWN}
)


def confidence_for_keyword_rules(*, matched_rules: int, text_len: int) -> str:
    """Heuristic: more pattern hits + sufficient text → higher confidence."""
    if text_len < 40:
        return CONFIDENCE_LOW
    if matched_rules >= 2:
        return CONFIDENCE_HIGH
    if matched_rules == 1:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_UNKNOWN
