"""
Purpose:
    Package boundary for regulation knowledge: source registry, versions, citations,
    and taxonomy—the authoritative store for what may be cited.

Role in Malone:
    Read paths supply evidence lists to retrieval and truth_packet assembly; writes stay
    admin/ingestion scoped (not Malone chat).

Expected inputs:
    N/A at package level; see submodules.

Expected outputs:
    N/A at package level; see submodules.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations
