"""
Purpose:
    Derive or validate handbook metadata aligned with regulation_source_versions
    (authority, jurisdiction, effective dates, version labels).

Role in Malone:
    Same fields power compliance checks before chunks are cited in Malone responses.

Expected inputs:
    Ingest manifest dict (title, jurisdiction, issuing_authority, dates, etc.).

Expected outputs:
    Normalized metadata dict for DB columns or meta_json.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any


def normalize_version_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    """Strip and pass through known keys only; extend as schema firms up."""
    keys = (
        "title",
        "jurisdiction",
        "issuing_authority",
        "effective_date",
        "version_label",
        "source_type",
    )
    return {k: payload[k] for k in keys if k in payload and payload[k] is not None}
