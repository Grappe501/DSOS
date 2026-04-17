"""Company knowledge review + promotion (governance layer; no source overrides)."""

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


def _user(db):
    from app.models.models import User

    db.merge(User(id="u1", email="ck@example.com", password_hash="x"))
    db.commit()


def _policy_version(db, *, vid: str | None = None, status: str = "validated") -> str:
    from app.models.ingestion_control import IngestionSource, IngestionSourceVersion
    from app.models.models import gen_id

    sid = gen_id()
    iid = vid or gen_id()
    db.add(
        IngestionSource(
            id=sid,
            stable_key=f"sk_{sid}",
            source_type="policy_manual",
            business_domain="internal_policy",
            title="Company policy",
            lifecycle_status="registered",
            authority_tier="internal",
        )
    )
    db.add(
        IngestionSourceVersion(
            id=iid,
            ingestion_source_id=sid,
            version_label="v1",
            parser_profile_key="policy_manual",
            status=status,
            retrieval_ready=False,
            meta_json="{}",
        )
    )
    db.commit()
    return iid


def _norm_unit(db, uid: str = "nu-company") -> str:
    from app.models.knowledge_normalization import NormalizationRun, NormalizedKnowledgeUnit
    from app.models.models import gen_id

    rid = gen_id()
    db.add(
        NormalizationRun(
            id=rid,
            profile_key="policy_manual_v1",
            source_type="policy_manual",
            validation_status="PASS",
        )
    )
    db.add(
        NormalizedKnowledgeUnit(
            id=uid,
            normalization_run_id=rid,
            ordinal=0,
            normalized_unit_type="procedure",
            source_type="policy_manual",
            source_text="procedure text",
            review_state="system_generated",
        )
    )
    db.commit()
    return uid


def test_review_decision_on_company_source_version_lifecycle_meta() -> None:
    from app.models.ingestion_control import IngestionSourceVersion
    from app.services.review_feedback.artifact_registry import ARTIFACT_INGESTION_SOURCE_VERSION
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    _user(db)
    vid = _policy_version(db)
    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_INGESTION_SOURCE_VERSION,
        artifact_id=vid,
        outcome="ready_for_promotion",
        reviewer_user_id="u1",
        notes="staging",
    )
    db.commit()
    v = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == vid).one()
    meta = json.loads(v.meta_json or "{}")
    hr = meta.get("human_review") if isinstance(meta.get("human_review"), dict) else {}
    assert hr.get("company_knowledge_lifecycle") == "validated"
    assert hr.get("promotion_ready") is True


def test_review_decision_on_normalized_unit_ready_and_hold() -> None:
    from app.models.knowledge_normalization import NormalizedKnowledgeUnit
    from app.services.knowledge_normalization.review_state import REVIEW_REVIEWED, REVIEW_UNDER_REVIEW
    from app.services.review_feedback.artifact_registry import ARTIFACT_NORMALIZED_UNIT
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    _user(db)
    uid = _norm_unit(db)
    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_NORMALIZED_UNIT,
        artifact_id=uid,
        outcome="ready_for_promotion",
        reviewer_user_id="u1",
    )
    db.commit()
    u = db.query(NormalizedKnowledgeUnit).filter(NormalizedKnowledgeUnit.id == uid).one()
    assert u.review_state == REVIEW_REVIEWED

    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_NORMALIZED_UNIT,
        artifact_id=uid,
        outcome="hold_for_review",
        reviewer_user_id="u1",
    )
    db.commit()
    u2 = db.query(NormalizedKnowledgeUnit).filter(NormalizedKnowledgeUnit.id == uid).one()
    assert u2.review_state == REVIEW_UNDER_REVIEW


def test_promotion_reviewed_to_approved_to_active() -> None:
    from app.models.ingestion_control import IngestionSourceVersion
    from app.services.review_feedback.artifact_registry import ARTIFACT_INGESTION_SOURCE_VERSION
    from app.services.review_feedback.company_knowledge_promotion import promote_ingestion_version_to_active_trusted
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    _user(db)
    vid = _policy_version(db, status="validated")
    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_INGESTION_SOURCE_VERSION,
        artifact_id=vid,
        outcome="approved",
        reviewer_user_id="u1",
    )
    db.commit()
    out = promote_ingestion_version_to_active_trusted(
        db,
        ingestion_source_version_id=vid,
        reviewer_user_id="u1",
        require_prior_approval=True,
    )
    db.commit()
    assert out.get("retrieval_ready") is True
    ver = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == vid).one()
    assert ver.status == "promoted_active"


def test_promote_without_approval_fails() -> None:
    from app.services.review_feedback.company_knowledge_promotion import promote_ingestion_version_to_active_trusted

    db = _memory_db()
    _user(db)
    vid = _policy_version(db)
    with pytest.raises(ValueError, match="approved"):
        promote_ingestion_version_to_active_trusted(
            db,
            ingestion_source_version_id=vid,
            reviewer_user_id="u1",
            require_prior_approval=True,
        )


def test_reject_needs_revision_and_archive_superseded() -> None:
    from app.models.ingestion_control import IngestionSourceVersion
    from app.models.knowledge_normalization import NormalizedKnowledgeUnit
    from app.services.knowledge_normalization.review_state import REVIEW_NEEDS_REVISION, REVIEW_REJECTED
    from app.services.review_feedback.artifact_registry import ARTIFACT_INGESTION_SOURCE_VERSION, ARTIFACT_NORMALIZED_UNIT
    from app.services.review_feedback.company_knowledge_promotion import archive_company_ingestion_version
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    _user(db)
    uid = _norm_unit(db)
    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_NORMALIZED_UNIT,
        artifact_id=uid,
        outcome="needs_revision",
        reviewer_user_id="u1",
    )
    db.commit()
    assert db.query(NormalizedKnowledgeUnit).filter(NormalizedKnowledgeUnit.id == uid).one().review_state == REVIEW_NEEDS_REVISION

    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_NORMALIZED_UNIT,
        artifact_id=uid,
        outcome="rejected",
        reviewer_user_id="u1",
    )
    db.commit()
    assert db.query(NormalizedKnowledgeUnit).filter(NormalizedKnowledgeUnit.id == uid).one().review_state == REVIEW_REJECTED

    vid = _policy_version(db)
    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_INGESTION_SOURCE_VERSION,
        artifact_id=vid,
        outcome="approved",
        reviewer_user_id="u1",
    )
    db.commit()
    archive_company_ingestion_version(
        db,
        ingestion_source_version_id=vid,
        reviewer_user_id="u1",
        mark_superseded=True,
        notes="replaced by v2",
    )
    db.commit()
    ver = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == vid).one()
    assert ver.status == "archived"
    assert ver.retrieval_ready is False


def test_review_rank_does_not_override_evidence_precedence_contract() -> None:
    from app.services.knowledge_normalization.review_state import REVIEW_APPROVED, REVIEW_SYSTEM_GENERATED
    from app.services.normalized_retrieval.fallback import review_rank

    assert review_rank(REVIEW_APPROVED) > review_rank(REVIEW_SYSTEM_GENERATED)


def test_website_pack_entry_review_state() -> None:
    from app.services.review_feedback.artifact_registry import ARTIFACT_WEBSITE_PACK_ENTRY
    from app.services.review_feedback.review_queries import get_head
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    _user(db)
    eid = "allcare_web:unit_test:line1"
    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_WEBSITE_PACK_ENTRY,
        artifact_id=eid,
        outcome="ready_for_promotion",
        reviewer_user_id="u1",
        notes="pack line ok",
    )
    db.commit()
    head = get_head(db, artifact_type=ARTIFACT_WEBSITE_PACK_ENTRY, artifact_id=eid)
    assert head and head.get("current_review_state") == "ready_for_promotion"


def test_governance_hints_readonly_and_ingestion_ids() -> None:
    from app.services.review_feedback.governance_hints import build_governance_hints_for_turn

    db = _memory_db()
    _user(db)
    vid = _policy_version(db)
    tp = {
        "policy_evidence": {"ingestion_source_version_id": vid, "enabled": True},
        "sop_evidence": {},
    }
    gh = build_governance_hints_for_turn(db, tp)
    assert gh.get("read_only") is True
    assert "precedence_note" in gh
    assert len(gh.get("ingestion_source_versions") or []) == 1


def test_governance_hints_legal_only_packet_has_no_company_ingestion_promotion_rows() -> None:
    """Legal lane alone does not attach company ingestion promotion hints (deterministic legal path unchanged)."""
    from app.services.review_feedback.governance_hints import build_governance_hints_for_turn

    db = _memory_db()
    _user(db)
    gh = build_governance_hints_for_turn(
        db,
        {"legal_evidence": {"legal_source_version_id": "lv-test", "enabled": True}},
    )
    assert (gh.get("ingestion_source_versions") or []) == []


def test_audit_history_visible_after_rejection() -> None:
    from app.services.review_feedback.artifact_registry import ARTIFACT_NORMALIZED_UNIT
    from app.services.review_feedback.review_queries import list_events_for_artifact
    from app.services.review_feedback.review_store import submit_review_feedback

    db = _memory_db()
    _user(db)
    uid = _norm_unit(db)
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
    evs = list_events_for_artifact(db, artifact_type=ARTIFACT_NORMALIZED_UNIT, artifact_id=uid, limit=10)
    assert len(evs) == 2
    assert any(e.get("outcome") == "approved" for e in evs)
    assert any(e.get("outcome") == "rejected" for e in evs)


def test_list_company_knowledge_candidates_includes_policy_row() -> None:
    from app.services.review_feedback.company_knowledge_promotion import list_company_knowledge_source_versions

    db = _memory_db()
    _user(db)
    vid = _policy_version(db)
    rows = list_company_knowledge_source_versions(db, limit=10)
    assert any(r["ingestion_source_version_id"] == vid for r in rows)
