"""
Purpose:
    Registry and persistence helpers for legal handbook entities (documents, families, units,
    citations, taxonomy, versions).

Role in Malone:
    Read path supplies citation-backed evidence to retrieval and truth packets; writes are
    ingestion-scoped (admin/batch), not Malone chat.

Expected inputs:
    SQLAlchemy sessions, stable keys, ingestion payloads (future).

Expected outputs:
    Serialized rows / lookup helpers for other legal packages.

TODO boundary:
    SQLAlchemy models for legal tables may live here or in `app.models` in a later pass;
    this package stays thin until wired.
"""

from __future__ import annotations
