"""Create and update intake sessions (linked to proposal + scenario memory for audit)."""

from __future__ import annotations

import json
import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import MaloneProposal, gen_id
from app.models.operations_map import DepartmentIntakeAnswer, DepartmentIntakeSession, OperationsDepartment
from app.models.scenario_memory import MaloneDecisionTrace, MaloneScenarioMemory
from app.services.department_intake.followup_generator import (
    compute_followup_questions,
    default_state,
    state_from_json,
)
from app.services.department_intake.intake_questionnaire import initial_prompts
from app.services.department_intake.response_parser import dumps_parser_output, parse_intake_answer
from app.services.department_intake.transcript_linking import build_transcript_ref
from app.services.scenario_memory.retrieval import prompt_fingerprint


def _slug_key(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return s or "department"


def _merge_profile(profile: dict[str, Any], patch: dict[str, Any]) -> None:
    for k, v in patch.items():
        if isinstance(v, list):
            cur = profile.get(k)
            if not isinstance(cur, list):
                cur = []
            merged = list(dict.fromkeys([*(cur or []), *v]))
            profile[k] = merged
        elif isinstance(v, str) and isinstance(profile.get(k), str) and (profile.get(k) or "").strip():
            profile[k] = f"{profile[k].strip()} {v.strip()}".strip()
        else:
            profile[k] = v


def start_intake_session(
    db: Session,
    *,
    actor_user_id: str,
    department_name: str,
    department_description: str | None = None,
) -> DepartmentIntakeSession:
    """Create department shell + proposal + scenario stub + open intake session."""
    sk = _slug_key(department_name)
    existing = db.query(OperationsDepartment).filter(OperationsDepartment.stable_key == sk).one_or_none()
    if existing:
        stable = f"{sk}-{gen_id()[:8]}"
    else:
        stable = sk

    dept = OperationsDepartment(
        id=gen_id(),
        stable_key=stable,
        name=department_name.strip()[:500],
        description=(department_description or "").strip() or None,
        meta_json=json.dumps({"created_via": "department_intake"}, ensure_ascii=False),
    )
    db.add(dept)
    db.flush()

    prop = MaloneProposal(
        proposal_type="department_intake",
        requested_action="session",
        target="operations_map",
        source_message=f"Department intake for {department_name}"[:8000],
        actor_user_id=actor_user_id,
        validation_status="pending",
        approval_status="pending",
        execution_status="proposal_only",
        candidate_output_json=json.dumps({"operations_department_id": dept.id}, ensure_ascii=False),
    )
    db.add(prop)
    db.flush()

    msg = f"Department intake session {dept.name}"
    scenario = MaloneScenarioMemory(
        id=gen_id(),
        proposal_id=prop.id,
        actor_user_id=actor_user_id,
        prompt_text=msg[:8000],
        prompt_fingerprint=prompt_fingerprint(msg),
        scenario_type="department_intake",
        intent_target="operations_map",
        source_types_json="[]",
        source_version_snapshot_json="{}",
        memory_status="active",
        review_audit_status="pending",
        delivery_mode="intake",
        delivery_status="intake_open",
        meta_json=json.dumps(
            {"operations_department_id": dept.id, "lane": "department_intake"},
            ensure_ascii=False,
        ),
    )
    db.add(scenario)
    db.flush()

    trace = MaloneDecisionTrace(
        id=gen_id(),
        scenario_memory_id=scenario.id,
        answer_pattern_json="{}",
        deterministic_legal_mode="non_deterministic",
        decision_workflow_json=json.dumps({"intake_stub": True, "deterministic": True}, ensure_ascii=False),
        source_evidence_map_json="{}",
        normalized_unit_refs_json="[]",
        fallback_flags_json="{}",
        packet_meta_snapshot_json=json.dumps({"intake": True}, ensure_ascii=False),
        verification_snapshot_json="{}",
        meta_json="{}",
    )
    db.add(trace)
    db.flush()

    st = default_state()
    sess = DepartmentIntakeSession(
        id=gen_id(),
        operations_department_id=dept.id,
        actor_user_id=actor_user_id,
        status="open",
        proposal_id=prop.id,
        scenario_memory_id=scenario.id,
        state_json=json.dumps(st, ensure_ascii=False),
        meta_json=json.dumps({"initial_prompts": initial_prompts()}, ensure_ascii=False),
    )
    db.add(sess)
    db.flush()
    return sess


def record_answer(
    db: Session,
    *,
    session_id: str,
    actor_user_id: str,
    answer_text: str,
    question_key: str | None,
    entry_mode: str,
    transcript_ref: str | None,
) -> DepartmentIntakeAnswer:
    sess = (
        db.query(DepartmentIntakeSession)
        .filter(DepartmentIntakeSession.id == session_id, DepartmentIntakeSession.actor_user_id == actor_user_id)
        .one_or_none()
    )
    if sess is None:
        raise ValueError("intake session not found")
    if sess.status != "open":
        raise ValueError("intake session is not open")

    parsed = parse_intake_answer(answer_text, question_key=question_key)
    patch = parsed.get("profile_patch") if isinstance(parsed.get("profile_patch"), dict) else {}

    state = state_from_json(sess.state_json)
    profile = state.setdefault("profile", {})
    if not isinstance(profile, dict):
        state["profile"] = default_state()["profile"]
        profile = state["profile"]
    _merge_profile(profile, patch)

    aid = gen_id()
    em = entry_mode if entry_mode in ("text", "voice_transcript") else "text"
    tr = transcript_ref
    if em == "voice_transcript" and not tr:
        tr = build_transcript_ref(session_id=sess.id, answer_id=aid, text_sample=answer_text)
    ans = DepartmentIntakeAnswer(
        id=aid,
        intake_session_id=sess.id,
        question_key=question_key,
        prompt_snapshot=None,
        answer_text=answer_text.strip()[:120_000],
        entry_mode=em,
        transcript_ref=tr,
        parser_output_json=dumps_parser_output(parsed),
    )

    db.add(ans)
    sess.state_json = json.dumps(state, ensure_ascii=False, default=str)
    db.add(sess)
    db.flush()
    return ans


def get_session_detail(db: Session, *, session_id: str, actor_user_id: str | None, is_admin: bool) -> dict[str, Any]:
    if not is_admin and not actor_user_id:
        raise ValueError("intake session not found")
    q = db.query(DepartmentIntakeSession).filter(DepartmentIntakeSession.id == session_id)
    if not is_admin:
        q = q.filter(DepartmentIntakeSession.actor_user_id == actor_user_id)
    sess = q.one_or_none()
    if sess is None:
        raise ValueError("intake session not found")

    state = state_from_json(sess.state_json)
    followups = compute_followup_questions(state)
    dept = db.query(OperationsDepartment).filter(OperationsDepartment.id == sess.operations_department_id).one()

    answers = (
        db.query(DepartmentIntakeAnswer)
        .filter(DepartmentIntakeAnswer.intake_session_id == sess.id)
        .order_by(DepartmentIntakeAnswer.created_at.asc())
        .all()
    )

    return {
        "session": {
            "id": sess.id,
            "status": sess.status,
            "operations_department_id": sess.operations_department_id,
            "proposal_id": sess.proposal_id,
            "scenario_memory_id": sess.scenario_memory_id,
            "created_at": str(sess.created_at),
            "updated_at": str(sess.updated_at),
        },
        "department": {"id": dept.id, "stable_key": dept.stable_key, "name": dept.name, "description": dept.description},
        "state": state,
        "followup_questions": followups,
        "answers": [
            {
                "id": a.id,
                "question_key": a.question_key,
                "entry_mode": a.entry_mode,
                "transcript_ref": a.transcript_ref,
                "created_at": str(a.created_at),
                "answer_excerpt": (a.answer_text or "")[:400],
            }
            for a in answers
        ],
        "read_only": False,
        "governance_note": "Intake answers are provisional; source-grounded evidence still takes precedence.",
    }
