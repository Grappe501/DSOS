"""
Purpose:
    Query the version graph: active vs superseded rows, effective dating, and which
    versions apply for a given point in time.

Role in Malone:
    Compliance calls this (directly or via shared helpers) before chunks are cited.

Expected inputs:
    source_id, status/superseded fields, optional as_of date.

Expected outputs:
    Applicable regulation_source_versions (future DB queries); placeholder helpers today.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from datetime import date


def is_version_active_row(
    *,
    status: str,
    superseded_at: str | None,
    as_of: date | None = None,
) -> bool:
    """Heuristic placeholder until DB-backed rules exist."""
    del as_of, superseded_at
    return status == "active"
