"""Trust labels for telemetry / UI (secondary to evidence precedence)."""

from __future__ import annotations

TRUST_HIGH = "high"
TRUST_MEDIUM = "medium"
TRUST_LOW = "low"


def trust_from_head(current_state: str | None, *, trust_level: str | None) -> str:
    """Coarse trust bucket for display; not used to override citations."""
    tl = (trust_level or "").strip().lower()
    if tl in (TRUST_HIGH, TRUST_MEDIUM, TRUST_LOW):
        return tl
    st = (current_state or "").strip().lower()
    if st == "approved":
        return TRUST_MEDIUM
    if st in ("rejected", "superseded"):
        return TRUST_LOW
    return TRUST_LOW
