"""
Purpose:
    `legal_tags` / `legal_chunk_tags` for topics (controlled substances, dispensing, etc.).

Role in Malone:
    Filters retrieval and formats labeled evidence in assistant output.

Expected inputs:
    Tag slugs, chunk ids, optional hierarchy (parent_id).

Expected outputs:
    Tag assignments for chunks.

TODO boundary:
    Tag sets are curated; no automatic topic model in this foundation pass.
"""

from __future__ import annotations
