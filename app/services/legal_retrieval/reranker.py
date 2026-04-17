"""
Purpose:
    Deterministic reranking rules (citation match boost, family priors, recency layers).

Role in Malone:
    Shapes top-k evidence without LLM involvement in v1.

Expected inputs:
    Hybrid-scored chunks, user department or profile (future).

Expected outputs:
    Final ordering for `top_k` evidence.

TODO boundary:
    Optional cross-encoder rerank is a later optional adapter, not default.
"""

from __future__ import annotations
