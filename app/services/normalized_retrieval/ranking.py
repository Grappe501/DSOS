"""Order normalized units for display (deterministic)."""

from __future__ import annotations

from typing import Any

from app.services.normalized_retrieval.fallback import confidence_rank, review_rank


def sort_units_for_display(units: list[Any]) -> list[Any]:
    """Prefer higher review rank, then confidence, then stable id."""
    return sorted(
        units,
        key=lambda u: (
            -review_rank(getattr(u, "review_state", None)),
            -confidence_rank(getattr(u, "confidence_level", None)),
            str(getattr(u, "id", "")),
        ),
    )


def pick_top_per_key(
    units: list[Any],
    *,
    key_fn: Any,
    max_per_key: int = 2,
) -> dict[str, list[Any]]:
    """Group by key_fn(unit), keep up to max_per_key sorted units per group."""
    from collections import defaultdict

    buckets: dict[str, list[Any]] = defaultdict(list)
    for u in sort_units_for_display(units):
        k = key_fn(u)
        if not k:
            continue
        if len(buckets[k]) >= max_per_key:
            continue
        buckets[k].append(u)
    return dict(buckets)
