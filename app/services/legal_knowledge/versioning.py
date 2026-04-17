"""
Purpose:
    Relate compiled edition, ingest checksum, and optional bridge to `regulation_sources`
    stable keys when both corpora coexist.

Role in Malone:
    Answers “November 2025 compiled edition” vs “embedded May 2023 act text” questions.

Expected inputs:
    legal_document / legal_source_version metadata, optional regulation stable_key.

Expected outputs:
    Version lineage records and comparison helpers (future).

TODO boundary:
    No automatic merge of overlapping regulation_* and legal_* rows without explicit policy.
"""

from __future__ import annotations
