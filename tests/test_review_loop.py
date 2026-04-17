"""Human review loop: events, heads, governance precedence (in-memory DB)."""

from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base


def _memory_db():
    import app.models.ingestion_control  # noqa: F401
    import app.models.knowledge_normalization  # noqa: F401
    import app.models.legal_handbook  # noqa: F401
    import app.models.models  # noqa: F401
    import app.models.review_feedback  # noqa: F401
    import app.models.scenario_memory  # noqa: F401

    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    return sessionmaker(bind=eng)()


def _minimal_norm_unit(db, uid: str = "nu-1") -> str:
    from app.models.knowledge_normalization import NormalizationRun, NormalizedKnowledgeUnit
    from app.models.models import User, gen_id

    rid = gen_id()
    db.add(
        NormalizationRun(
            id=rid,
            profile_key="test",
            source_type="legal_handbook",
            validation_status="PASS",
        )
    )
    db.add(
        NormalizedKnowledgeUnit(
            id=uid,
            normalization_run_id=rid,
            ordinal=0,
            normalized_unit_type="requirement",
            source_type="legal_handbook",
            source_text="keep",
            review_state="system_generated",
        )
    )
    db.add(User(id="u1", email="r@example.com", password_hash="x"))
    db.commit()
    return uid


def test_review_normalized_unit_approve_and_reject(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_SCENARIO_MEMORY_ENABLED", "0")
    from app.models.knowledge_normalization import NormalizedKnowledgeUnit
    from app.models.review_feedback import MaloneReviewArtifactHead, MaloneReviewFeedbackEvent
    from app.services.knowledge_normalization.review_state import REVIEW_APPROVED, REVIEW_REJECTED
    from app.services.review_feedback.artifact_registry import ARTIFACT_NORMALIZED_UNIT
    from app.services.review_feedback.review_queries import list_events_for_artifact
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    uid = _minimal_norm_unit(db)

    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_NORMALIZED_UNIT,
        artifact_id=uid,
        outcome="approved",
        reviewer_user_id="u1",
        notes="ok",
    )
    db.commit()
    u = db.query(NormalizedKnowledgeUnit).filter(NormalizedKnowledgeUnit.id == uid).one()
    assert u.review_state == REVIEW_APPROVED

    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_NORMALIZED_UNIT,
        artifact_id=uid,
        outcome="rejected",
        reviewer_user_id="u1",
    )
    db.commit()
    u2 = db.query(NormalizedKnowledgeUnit).filter(NormalizedKnowledgeUnit.id == uid).one()
    assert u2.review_state == REVIEW_REJECTED

    evs = list_events_for_artifact(db, artifact_type=ARTIFACT_NORMALIZED_UNIT, artifact_id=uid, limit=10)
    assert len(evs) == 2
    head = db.query(MaloneReviewArtifactHead).filter(MaloneReviewArtifactHead.artifact_id == uid).one()
    assert head.current_review_state == REVIEW_REJECTED


def test_scenario_memory_review_transitions() -> None:
    from app.models.models import MaloneProposal, User, gen_id
    from app.models.scenario_memory import MaloneScenarioMemory
    from app.services.review_feedback.artifact_registry import ARTIFACT_SCENARIO_MEMORY
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    pid = gen_id()
    db.add(User(id="u1", email="r2@example.com", password_hash="x"))
    db.add(
        MaloneProposal(
            id=pid,
            proposal_type="answer",
            requested_action="respond",
            source_message="x",
            validation_status="approved",
            approval_status="approved",
            execution_status="proposal_only",
        )
    )
    sid = gen_id()
    db.add(
        MaloneScenarioMemory(
            id=sid,
            proposal_id=pid,
            prompt_text="q",
            prompt_fingerprint="fp",
            scenario_type="t",
            review_audit_status="pending",
        )
    )
    db.commit()

    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_SCENARIO_MEMORY,
        artifact_id=sid,
        outcome="needs_revision",
        reviewer_user_id="u1",
    )
    db.commit()
    sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == sid).one()
    assert sm.review_audit_status == "needs_revision"
    meta = json.loads(sm.meta_json)
    assert "human_review" in meta


def test_decision_trace_review_meta() -> None:
    from app.models.models import MaloneProposal, User, gen_id
    from app.models.scenario_memory import MaloneDecisionTrace, MaloneScenarioMemory
    from app.services.review_feedback.artifact_registry import ARTIFACT_DECISION_TRACE
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    pid = gen_id()
    db.add(User(id="u1", email="r3@example.com", password_hash="x"))
    db.add(
        MaloneProposal(
            id=pid,
            proposal_type="answer",
            requested_action="respond",
            source_message="x",
            validation_status="approved",
            approval_status="approved",
            execution_status="proposal_only",
        )
    )
    sid = gen_id()
    db.add(
        MaloneScenarioMemory(
            id=sid,
            proposal_id=pid,
            prompt_text="q",
            prompt_fingerprint="fp",
            scenario_type="t",
            review_audit_status="pending",
        )
    )
    tid = gen_id()
    db.add(
        MaloneDecisionTrace(
            id=tid,
            scenario_memory_id=sid,
            answer_pattern_json="{}",
            deterministic_legal_mode="unknown",
            decision_workflow_json="{}",
            source_evidence_map_json="{}",
            normalized_unit_refs_json="[]",
            fallback_flags_json="{}",
            packet_meta_snapshot_json="{}",
            verification_snapshot_json="{}",
            meta_json="{}",
        )
    )
    db.commit()

    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_DECISION_TRACE,
        artifact_id=tid,
        outcome="informational",
        reviewer_user_id="u1",
        notes="noted",
    )
    db.commit()
    tr = db.query(MaloneDecisionTrace).filter(MaloneDecisionTrace.id == tid).one()
    m = json.loads(tr.meta_json)
    assert m.get("human_review", {}).get("notes") == "noted"


def test_website_pack_entry_head_only() -> None:
    from app.models.models import User
    from app.models.review_feedback import MaloneReviewArtifactHead
    from app.services.review_feedback.artifact_registry import ARTIFACT_WEBSITE_PACK_ENTRY
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    db.add(User(id="u1", email="r4@example.com", password_hash="x"))
    db.commit()

    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_WEBSITE_PACK_ENTRY,
        artifact_id="allcare:page:services",
        outcome="approved",
        reviewer_user_id="u1",
        meta_json={"priority": 2},
    )
    db.commit()
    h = (
        db.query(MaloneReviewArtifactHead)
        .filter(
            MaloneReviewArtifactHead.artifact_type == ARTIFACT_WEBSITE_PACK_ENTRY,
            MaloneReviewArtifactHead.artifact_id == "allcare:page:services",
        )
        .one()
    )
    assert h.current_review_state == "approved"


def test_precedence_review_does_not_rewrite_source_text() -> None:
    from app.services.review_feedback.safety import assert_no_source_text_mutation_fields

    with pytest.raises(ValueError):
        assert_no_source_text_mutation_fields({"source_text": "x"})


def test_governance_hints_for_turn() -> None:
    from app.services.review_feedback.governance_hints import build_governance_hints_for_turn

    db = _memory_db()
    uid = _minimal_norm_unit(db)
    tp = {"legal_evidence": {"normalized": {"units_by_chunk_id": {"c1": [{"id": uid}]}}}}
    g = build_governance_hints_for_turn(db, tp)
    assert g["read_only"] is True
    assert len(g["normalized_units"]) == 1
    assert g["normalized_units"][0]["normalized_unit_id"] == uid


def test_deterministic_legal_format_unchanged_by_governance() -> None:
    from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer

    items = [
        {
            "citation_key": "K1",
            "legal_unit_chunk_id": "c1",
            "snippet": "body",
            "page_start": 1,
            "page_end": 1,
        }
    ]
    t1 = format_legal_lookup_answer(items, normalized_bundle=None)
    t2 = format_legal_lookup_answer(items, normalized_bundle=None)
    assert t1 == t2


def test_review_event_rows_persist_after_rejection() -> None:
    from app.models.knowledge_normalization import NormalizedKnowledgeUnit
    from app.models.review_feedback import MaloneReviewFeedbackEvent
    from app.services.knowledge_normalization.review_state import REVIEW_REJECTED
    from app.services.review_feedback.artifact_registry import ARTIFACT_NORMALIZED_UNIT
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    uid = _minimal_norm_unit(db)

    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_NORMALIZED_UNIT,
        artifact_id=uid,
        outcome="approved",
        reviewer_user_id="u1",
    )
    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_NORMALIZED_UNIT,
        artifact_id=uid,
        outcome="rejected",
        reviewer_user_id="u1",
    )
    db.commit()
    assert db.query(MaloneReviewFeedbackEvent).count() == 2
    assert db.query(NormalizedKnowledgeUnit).one().review_state == REVIEW_REJECTED
