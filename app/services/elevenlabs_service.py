"""
Server-side ElevenLabs text-to-speech (Malone voice layer).

API key stays on the server; callers use the authenticated /api/malone/tts route.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.utils.logger import log

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
ELEVENLABS_TTS_TIMEOUT_SECONDS = float(os.getenv("ELEVENLABS_TTS_TIMEOUT_SECONDS", "60"))
MALONE_TTS_ENABLED = os.getenv("MALONE_TTS_ENABLED", "true").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)
MALONE_TTS_MAX_CHARS = int(os.getenv("MALONE_TTS_MAX_CHARS", "2000"))

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"


class ElevenLabsTTSError(RuntimeError):
    """Raised when TTS cannot be generated (config, network, or provider error)."""


def is_tts_configured() -> bool:
    return bool(ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID) and MALONE_TTS_ENABLED


def voice_status_payload() -> dict[str, Any]:
    return {
        "tts_configured": is_tts_configured(),
        "max_chars": MALONE_TTS_MAX_CHARS,
        "tts_enabled_flag": MALONE_TTS_ENABLED,
    }


def synthesize_speech_mp3(
    text: str,
    *,
    voice_id: str | None = None,
) -> bytes:
    """
    Returns MP3 bytes from ElevenLabs text-to-speech.

    Raises ElevenLabsTTSError on validation or HTTP failures.
    """
    if not MALONE_TTS_ENABLED:
        raise ElevenLabsTTSError("TTS is disabled (MALONE_TTS_ENABLED).")

    if not ELEVENLABS_API_KEY:
        raise ElevenLabsTTSError("ELEVENLABS_API_KEY is not configured.")

    vid = (voice_id or ELEVENLABS_VOICE_ID or "").strip()
    if not vid:
        raise ElevenLabsTTSError("ELEVENLABS_VOICE_ID is not configured.")

    raw = (text or "").strip()
    if not raw:
        raise ElevenLabsTTSError("Text is empty.")

    if len(raw) > MALONE_TTS_MAX_CHARS:
        raise ElevenLabsTTSError(
            f"Text exceeds maximum length ({MALONE_TTS_MAX_CHARS} characters)."
        )

    url = f"{ELEVENLABS_TTS_URL}/{vid}"
    payload: dict[str, Any] = {
        "text": raw,
        "model_id": ELEVENLABS_MODEL_ID,
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=body,
        method="POST",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )

    try:
        with urlopen(req, timeout=ELEVENLABS_TTS_TIMEOUT_SECONDS) as resp:
            return resp.read()
    except HTTPError as exc:
        detail = _read_error_body(exc)
        log(f"ElevenLabs TTS HTTP {exc.code}: {detail[:200]!r}")
        raise ElevenLabsTTSError(f"ElevenLabs error ({exc.code}): {detail}") from exc
    except URLError as exc:
        log(f"ElevenLabs TTS network error: {exc}")
        raise ElevenLabsTTSError("TTS network error.") from exc


def _read_error_body(exc: HTTPError) -> str:
    try:
        raw = exc.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        if isinstance(data, dict):
            detail = data.get("detail")
            if isinstance(detail, str):
                return detail
            if isinstance(detail, list) and detail:
                first = detail[0]
                if isinstance(first, dict) and first.get("msg"):
                    return str(first.get("msg"))
        return raw[:500]
    except Exception:
        return str(exc)
