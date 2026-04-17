"""Tests for normalized retrieval bundle attachment and answer formatting."""

from __future__ import annotations

from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer, format_policy_lookup_answer
from app.services.normalized_retrieval.fallback import unit_is_blocked
from app.services.normalized_retrieval.ranking import sort_units_for_display


class _U:
    def __init__(self, id: str, review_state: str, confidence_level: str) -> None:
        self.id = id
        self.review_state = review_state
        self.confidence_level = confidence_level


def test_sort_units_prefers_higher_review():
    a = _U("a", "approved", "medium")
    b = _U("b", "system_generated", "high")
    out = sort_units_for_display([b, a])
    assert out[0].id == "a"


def test_format_legal_includes_normalized_after_citation():
    items = [
        {
            "citation_key": "K1",
            "legal_unit_chunk_id": "chunk-1",
            "snippet": "body",
            "page_start": 1,
            "page_end": 1,
        }
    ]
    norm = {
        "enabled": True,
        "units_by_chunk_id": {
            "chunk-1": [
                {
                    "normalized_unit_type": "requirement",
                    "requirement_level": "must",
                    "plain_language_summary": "Do the thing.",
                    "confidence_level": "medium",
                    "review_state": "system_generated",
                }
            ]
        },
    }
    text = format_legal_lookup_answer(items, normalized_bundle=norm)
    assert "Citation:" in text
    assert "requirement" in text.lower()
    assert "must" in text.lower()


def test_format_policy_empty_items():
    text = format_policy_lookup_answer([], normalized_bundle=None)
    assert "No matching policy" in text


def test_unit_is_blocked_rejects():
    class R:
        review_state = "rejected"
        superseded = False

    assert unit_is_blocked(R()) is True
