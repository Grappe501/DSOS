"""
Purpose:
    Boundary package for deterministic parsing and chunking of compiled legal handbooks
    (TOC families, legal units, subsections, citations, cross-references, date layers).

Role in Malone:
    Produces structured records for `legal_knowledge` storage and downstream retrieval;
    never owns conversational answers or execution authority.

Expected inputs:
    Ingestion job descriptors, normalized PDF/text extracts, and profile configuration
    (see `profile.py`).

Expected outputs:
    Parse artifacts (trees, spans, citation candidates) for persistence by ingestion jobs.

TODO boundary:
    No LLM-based rewriting of legal text here; only extraction, segmentation, and labeling.
"""

from __future__ import annotations
