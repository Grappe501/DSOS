"""Demo mode envelope and presentation (no logic rewrites)."""

from __future__ import annotations

import pytest

from app.services.demo_mode.config import demo_config_payload
from app.services.demo_mode.response_adjustments import (
    apply_demo_limited_scope_truth_packet,
    attach_demo_envelope,
    build_presentation_layer,
)


def test_demo_config_defaults_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MALONE_DEMO_MODE", raising=False)
    monkeypatch.delenv("MALONE_DEMO_SAFE_RESPONSES", raising=False)
    monkeypatch.delenv("MALONE_DEMO_LIMITED_SCOPE", raising=False)
    c = demo_config_payload()
    assert c["malone_demo_mode"] is False
    assert c["malone_demo_safe_responses"] is False
    assert c["malone_demo_limited_scope"] is False


def test_demo_limited_scope_disables_web_search(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_DEMO_LIMITED_SCOPE", "1")
    tp: dict = {"retrieval_rules": {"allow_web_search": True}}
    apply_demo_limited_scope_truth_packet(tp)
    assert tp["retrieval_rules"]["allow_web_search"] is False


def test_attach_demo_envelope_sets_flags_without_breaking_delivery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_DEMO_MODE", "1")
    monkeypatch.setenv("MALONE_DEMO_SAFE_RESPONSES", "0")
    out = attach_demo_envelope(
        {
            "delivery": {"answer": "Hello\n\n\nWorld", "mode": "x"},
            "truth_packet": {
                "policy_evidence": {"items": [{"body_text": "Rule A applies."}]},
                "operating_copilot": {
                    "enabled": True,
                    "guidance": {"recommended_next_steps": ["Step one"], "operating_summary_bullets": ["Bullet"]},
                },
                "decision_workflow": {},
            },
            "verification": {"delivery_mode": "policy_grounded_deterministic"},
        }
    )
    assert out["demo"]["active"] is True
    assert "presentation" in out
    assert out["delivery"]["answer"] == "Hello\n\n\nWorld"
    pres = out["presentation"]
    assert pres.get("what_the_rules_say")


def test_presentation_layer_non_empty_for_structured_turn() -> None:
    pres = build_presentation_layer(
        {
            "truth_packet": {
                "sop_evidence": {"items": [{"body_text": "Verify NDC."}]},
                "operating_copilot": {
                    "enabled": True,
                    "guidance": {
                        "recommended_next_steps": ["Confirm insurance"],
                        "who_should_act": ["Technician"],
                        "when_to_escalate": ["If rejection"],
                    },
                },
                "decision_workflow": {"title": "SOP match"},
            },
            "verification": {"delivery_mode": "sop_grounded_deterministic"},
        }
    )
    assert pres["what_the_rules_say"]
    assert pres["next_best_actions"]
    assert pres["operating_copilot_enabled"] is True


def test_demo_mode_off_skips_presentation_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MALONE_DEMO_MODE", raising=False)
    out = attach_demo_envelope({"delivery": {"answer": "x"}, "truth_packet": {}})
    assert out.get("presentation") is None
    assert out["demo"]["active"] is False


def test_demo_safe_collapses_excess_blank_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_DEMO_MODE", "1")
    monkeypatch.setenv("MALONE_DEMO_SAFE_RESPONSES", "1")
    out = attach_demo_envelope({"delivery": {"answer": "A\n\n\n\nB"}, "truth_packet": {}})
    assert out["delivery"]["answer"] == "A\n\nB"
