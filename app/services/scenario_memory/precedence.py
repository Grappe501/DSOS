"""Explicit precedence: current evidence always wins over stored scenarios."""

from __future__ import annotations

from typing import Any


PRECEDENCE_NOTE = (
    "Current source-grounded retrieval and citations outrank any prior scenario memory. "
    "Prior records are secondary analogs for review and audit only."
)


def current_evidence_outranks_memory() -> bool:
    """Invariant for Malone: memory must never override live evidence."""
    return True


def merge_policy_for_answers() -> dict[str, Any]:
    return {
        "memory_may_inform_review": True,
        "memory_must_not_change_citations": True,
        "memory_must_not_replace_excerpts": True,
        "on_conflict": "prefer_current_evidence",
    }


def _flatten_version_snapshot(snap: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for lane, inner in (snap or {}).items():
        if isinstance(inner, dict):
            for ik, iv in inner.items():
                out[f"{lane}.{ik}"] = iv
    return out


def should_suppress_prior_due_to_conflict(
    *,
    current_source_versions: dict[str, Any],
    prior_source_versions: dict[str, Any],
) -> bool:
    """If source versions shifted materially, prior analogy is weaker."""
    cur = _flatten_version_snapshot(current_source_versions)
    pri = _flatten_version_snapshot(prior_source_versions)
    if not cur or not pri:
        return False
    for k, v in cur.items():
        if v is None:
            continue
        if k in pri and pri.get(k) not in (None, v):
            return True
    return False
