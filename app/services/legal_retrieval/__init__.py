"""
Purpose:
    Citation-first retrieval over `legal_unit_chunks` (lexical + hybrid + rerank + authority).

Role in Malone:
    Supplies evidence bundles to `truth_packet_service` extensions and `legal_assistant`
    without bypassing verification.

Expected inputs:
    Query text, actor scope, optional citation hints, filters.

Expected outputs:
    Ranked chunk lists with citation keys and anchors for trace logging.

TODO boundary:
    No OpenAI calls inside this package; embedding calls isolated in a future adapter.
"""

from __future__ import annotations
