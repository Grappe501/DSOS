"""
Purpose:
    Sequence: citation lookup → retrieval → authority filter → compliance → formatter.

Role in Malone:
    Single entry for “legal handbook” intent once routed from `intent_service` (future).

Expected inputs:
    Normalized request dict, db session handle (future).

Expected outputs:
    Structured response envelope with evidence and trace references.

TODO boundary:
    Stub only; wire-up happens after ingestion produces chunk rows.
"""

from __future__ import annotations
