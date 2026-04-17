"""
Purpose:
    Thin orchestration for pharmacy-law Q&A over internal legal chunks (future integration
    with Malone truth packets and verification).

Role in Malone:
    Assembles retrieval + compliance + formatting; LLM usage remains behind existing
    render/verify boundaries.

Expected inputs:
    User message, actor, optional citation hint.

Expected outputs:
    Draft answer payload + evidence list + trace ids (when wired).

TODO boundary:
    No direct OpenAI imports here until `malone_service` / truth_packet contracts extend.
"""

from __future__ import annotations
