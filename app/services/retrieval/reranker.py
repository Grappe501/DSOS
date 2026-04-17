"""
Purpose:
    Optional second-stage reranking of retrieval candidates (cross-encoder, small LLM,
    or heuristic).

Role in Malone:
    May reorder evidence only; must not invent facts or replace citation-backed text.

Expected inputs:
    Query string; list of candidate chunk dicts with prior scores.

Expected outputs:
    Reordered candidate list (same items, new order).

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any


def rerank_placeholder(
    query: str,
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    del query
    return list(candidates)
