"""Unit tests for ElevenLabs TTS helper (no network)."""

from __future__ import annotations

from unittest import mock

import pytest

import app.services.elevenlabs_service as el


def test_synthesize_requires_api_key(monkeypatch):
    monkeypatch.setattr(el, "ELEVENLABS_API_KEY", "")
    monkeypatch.setattr(el, "ELEVENLABS_VOICE_ID", "vid")
    monkeypatch.setattr(el, "MALONE_TTS_ENABLED", True)

    with pytest.raises(el.ElevenLabsTTSError, match="API_KEY"):
        el.synthesize_speech_mp3("hello")


def test_synthesize_success(monkeypatch):
    monkeypatch.setattr(el, "ELEVENLABS_API_KEY", "test-key")
    monkeypatch.setattr(el, "ELEVENLABS_VOICE_ID", "voice-id-1")
    monkeypatch.setattr(el, "MALONE_TTS_ENABLED", True)
    monkeypatch.setattr(el, "MALONE_TTS_MAX_CHARS", 2000)

    fake_mp3 = b"ID3fake"

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return fake_mp3

    def fake_urlopen(req, timeout=None):
        assert "voice-id-1" in getattr(req, "full_url", str(req))
        return FakeResponse()

    with mock.patch("app.services.elevenlabs_service.urlopen", fake_urlopen):
        out = el.synthesize_speech_mp3("Hello Malone.")
        assert out == fake_mp3


def test_text_length_cap(monkeypatch):
    monkeypatch.setattr(el, "ELEVENLABS_API_KEY", "k")
    monkeypatch.setattr(el, "ELEVENLABS_VOICE_ID", "v")
    monkeypatch.setattr(el, "MALONE_TTS_ENABLED", True)
    monkeypatch.setattr(el, "MALONE_TTS_MAX_CHARS", 5)

    with pytest.raises(el.ElevenLabsTTSError, match="maximum length"):
        el.synthesize_speech_mp3("123456")
