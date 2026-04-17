"""Smart answer pattern selection and shaping (no DB)."""

from __future__ import annotations

from app.services.answer_patterns.pattern_selector import select_answer_pattern
from app.services.answer_patterns.signals import PATTERN_EXCEPTION, PATTERN_REQUIREMENT, PATTERN_SOURCE_LOCATOR, PATTERN_WORKFLOW
from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer, format_policy_lookup_answer


def test_selector_requirement_question():
    sel = select_answer_pattern(
        message="What is required for PDMP reporting — is this mandatory?",
        source_type="legal_handbook",
        normalized_units=[],
    )
    assert sel["pattern_id"] == PATTERN_REQUIREMENT
    assert sel["confidence"] == "high"


def test_selector_workflow_question():
    sel = select_answer_pattern(
        message="Walk me through the process — what do I do next?",
        source_type="policy_manual",
        normalized_units=[],
    )
    assert sel["pattern_id"] == PATTERN_WORKFLOW


def test_selector_exception_question():
    sel = select_answer_pattern(
        message="Are there exceptions — what if the patient is exempt?",
        source_type="policy_manual",
        normalized_units=[],
    )
    assert sel["pattern_id"] == PATTERN_EXCEPTION


def test_selector_source_locator_question():
    sel = select_answer_pattern(
        message="Where does it say that — show me the citation and what section?",
        source_type="legal_handbook",
        normalized_units=[],
    )
    assert sel["pattern_id"] == PATTERN_SOURCE_LOCATOR


def test_neutral_message_selects_standard():
    sel = select_answer_pattern(
        message="hello world generic text",
        source_type="legal_handbook",
        normalized_units=[],
    )
    assert sel["pattern_id"] == "standard"


def test_legal_answer_preserves_citation_line():
    items = [
        {
            "citation_key": "AC.A.1.2",
            "legal_unit_chunk_id": "c1",
            "snippet": "Sample statutory text for testing.",
            "page_start": 10,
            "page_end": 11,
            "family_title": "Test Family",
        }
    ]
    text = format_legal_lookup_answer(
        items,
        message="Where does it say that?",
        normalized_bundle=None,
        decision_workflow=None,
        truth_packet=None,
    )
    assert "Citation:" in text or "Primary citation:" in text
    assert "AC.A.1.2" in text


def test_policy_surfaces_operational_fields():
    items = [{"heading": "H1", "ingestion_segment_id": "s1", "snippet": "Policy body text.", "ordinal": 1}]
    norm = {
        "enabled": True,
        "units_by_segment_id": {
            "s1": [
                {
                    "normalized_unit_type": "requirement",
                    "requirement_level": "must",
                    "applies_to_role": "Manager",
                    "plain_language_summary": "Submit form within 24h.",
                    "confidence_level": "medium",
                    "review_state": "system_generated",
                }
            ]
        },
    }
    text = format_policy_lookup_answer(
        items,
        message="What is required by company policy?",
        normalized_bundle=norm,
        decision_workflow=None,
        truth_packet=None,
    )
    assert "Bottom line" in text
    assert "Manager" in text
