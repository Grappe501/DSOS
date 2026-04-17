"""
Purpose:
    Extract internal and external legal cross-references from chunk text (e.g. “see
    5-64-101”, “A.C.A. § …”) for `legal_cross_references` and later resolution.

Role in Malone:
    Feeds deterministic linking passes; unresolved refs remain flagged for audit.

Expected inputs:
    Chunk text, jurisdiction context (Arkansas), optional citation registry snapshot.

Expected outputs:
    Reference records with `raw_reference_text`, optional `to_citation_key`, resolution status.

TODO boundary:
    Resolution to `to_legal_unit_id` is a separate linker step, not done inline on first pass.
"""

from __future__ import annotations
