"""Stable transcript reference strings for voice-derived answers (same Malone path)."""

from __future__ import annotations

import hashlib


def build_transcript_ref(*, session_id: str, answer_id: str, text_sample: str) -> str:
    h = hashlib.sha256(f"{session_id}:{answer_id}:{text_sample[:200]}".encode("utf-8")).hexdigest()[:16]
    return f"voice_transcript:{session_id}:{answer_id}:{h}"
