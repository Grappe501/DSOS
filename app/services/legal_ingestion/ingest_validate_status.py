"""
Deterministic PASS / PASS_WITH_WARNINGS / FAIL classification for Arkansas handbook ingest QA.

Used by ``tracking/scripts/run_arkansas_handbook_ingest_validate.py`` and unit tests.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def decide_overall_status(failures: Sequence[str], warnings: Sequence[str]) -> str:
    """If any hard failure exists, FAIL; else if any warning, PASS_WITH_WARNINGS; else PASS."""
    if failures:
        return "FAIL"
    if warnings:
        return "PASS_WITH_WARNINGS"
    return "PASS"


def retrieval_is_broad_failure(query_results: Sequence[Mapping[str, Any]]) -> bool:
    """
    True when every retrieval probe returned zero hits (scoped to the ingested source version).

    Expects each mapping to include ``hit_count`` (int >= 0).
    """
    if not query_results:
        return True
    return all(int(r.get("hit_count") or 0) == 0 for r in query_results)
