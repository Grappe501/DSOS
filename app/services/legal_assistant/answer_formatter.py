"""
Purpose:
    Format answers with required anchors: Ark. Code citation, rule section, family title,
    subsection path, page anchor.

Role in Malone:
    Ensures user-visible strings remain tied to `legal_citations` / `anchor_json`.

Expected inputs:
    Evidence chunks, citation records, date layer summaries.

Expected outputs:
    Markdown or plain text blocks suitable for render verification inputs.

TODO boundary:
    No paraphrase that omits anchors; verbosity controlled by policy constants later.
"""

from __future__ import annotations
