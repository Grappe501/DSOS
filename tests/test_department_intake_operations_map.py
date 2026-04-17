"""Department intake + operations map (in-memory DB)."""

from __future__ import annotations

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base


def _memory_db():
    import app.models.ingestion_control  # noqa: F401
    import app.models.knowledge_normalization  # noqa: F401
    import app.models.legal_handbook  # noqa: F401
    import app.models.models  # noqa: F401
    import app.models.operations_map  # noqa: F401
    import app.models.review_feedback  # noqa: F401
    import app.models.scenario_memory  # noqa: F401

    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    return sessionmaker(bind=eng)()


def _user(db):
    from app.models.models import User

    db.merge(User(id="u1", email="d@example.com", password_hash="x"))
    db.commit()


def test_intake_session_creation_links_proposal_and_scenario() -> None:
    from app.models.operations_map import DepartmentIntakeSession
    from app.services.department_intake.intake_session_store import start_intake_session

    db = _memory_db()
    _user(db)
    sess = start_intake_session(db, actor_user_id="u1", department_name="Test Pharmacy Ops")
    db.commit()
    assert sess.proposal_id
    assert sess.scenario_memory_id
    row = db.query(DepartmentIntakeSession).filter(DepartmentIntakeSession.id == sess.id).one()
    assert row.status == "open"


def test_deterministic_followup_when_fields_missing() -> None:
    from app.services.department_intake.followup_generator import compute_followup_questions, default_state

    state = default_state()
    qs = compute_followup_questions(state)
    targets = {q["target_field"] for q in qs}
    assert "profile.mission" in targets
    assert all("question_text" in q and "priority" in q and "reason" in q for q in qs)


def test_response_parser_populates_profile_patch() -> None:
    from app.services.department_intake.response_parser import parse_intake_answer

    out = parse_intake_answer("Verify daily fills and counsel patients.", question_key="mission")
    assert "profile_patch" in out
    assert out["profile_patch"].get("mission")


def test_operations_map_materializes_rows() -> None:
    from app.services.department_intake.intake_session_store import record_answer, start_intake_session
    from app.services.operations_map.department_store import get_department_map
    from app.services.operations_map.map_builder import materialize_operations_map

    db = _memory_db()
    _user(db)
    sess = start_intake_session(db, actor_user_id="u1", department_name="Demo Dept")
    db.commit()
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="Fulfill prescriptions accurately.",
        question_key="mission",
        entry_mode="text",
        transcript_ref=None,
    )
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="Pharmacist, Technician",
        question_key="roles",
        entry_mode="text",
        transcript_ref=None,
    )
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="New Rx intake, Verification",
        question_key="workflows",
        entry_mode="text",
        transcript_ref=None,
    )
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="We depend on Wholesaler; Billing depends on us",
        question_key="dependencies",
        entry_mode="text",
        transcript_ref=None,
    )
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="Hand off to Delivery when ready",
        question_key="handoffs",
        entry_mode="text",
        transcript_ref=None,
    )
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="Escalate inventory issues to PIC",
        question_key="escalation",
        entry_mode="text",
        transcript_ref=None,
    )
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="Short staffing",
        question_key="blockers",
        entry_mode="text",
        transcript_ref=None,
    )
    db.commit()
    materialize_operations_map(db, intake_session_id=sess.id, actor_user_id="u1", is_admin=False)
    db.commit()
    mp = get_department_map(db, department_id=sess.operations_department_id)
    assert mp["read_only"] is True
    assert len(mp["roles"]) >= 1
    assert len(mp["workflows"]) >= 1
    assert len(mp["dependencies"]) >= 1


def test_transcript_ref_on_voice_mode() -> None:
    from app.models.operations_map import DepartmentIntakeAnswer
    from app.services.department_intake.intake_session_store import record_answer, start_intake_session

    db = _memory_db()
    _user(db)
    sess = start_intake_session(db, actor_user_id="u1", department_name="Voice Dept")
    db.commit()
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="spoken answer",
        question_key=None,
        entry_mode="voice_transcript",
        transcript_ref=None,
    )
    db.commit()
    a = db.query(DepartmentIntakeAnswer).one()
    assert a.transcript_ref
    assert a.transcript_ref.startswith("voice_transcript:")


def test_read_only_map_inspection() -> None:
    from app.services.operations_map.department_store import get_department_map
    from app.services.department_intake.intake_session_store import record_answer, start_intake_session
    from app.services.operations_map.map_builder import materialize_operations_map

    db = _memory_db()
    _user(db)
    sess = start_intake_session(db, actor_user_id="u1", department_name="RO Dept")
    db.commit()
    record_answer(
        db,
        session_id=sess.id,
        actor_user_id="u1",
        answer_text="mission text",
        question_key="mission",
        entry_mode="text",
        transcript_ref=None,
    )
    db.commit()
    materialize_operations_map(db, intake_session_id=sess.id, actor_user_id="u1", is_admin=False)
    db.commit()
    m = get_department_map(db, department_id=sess.operations_department_id)
    assert m["governance_note"]


def test_source_evidence_outranks_intake_memory() -> None:
    from app.services.department_intake.safety import evidence_precedence_rank

    assert evidence_precedence_rank("legal_handbook_citation") > evidence_precedence_rank("intake_session_memory")


def test_deterministic_legal_path_unchanged_import() -> None:
    """Sanity: Malone service entrypoint still exposes legal grounding (no second path added)."""
    from app.services.malone_service import handle_malone_request

    assert callable(handle_malone_request)
