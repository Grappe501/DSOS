"""Materialize normalized rows from intake session state (idempotent rebuild per department)."""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.models import gen_id
from app.models.operations_map import (
    DepartmentIntakeSession,
    OperationsArtifactRef,
    OperationsBlocker,
    OperationsDependency,
    OperationsDepartment,
    OperationsEscalation,
    OperationsHandoff,
    OperationsRole,
    OperationsSystemTool,
    OperationsWorkflow,
)
from app.services.department_intake.followup_generator import state_from_json


def _clear_department_children(db: Session, department_id: str) -> None:
    for model, col in (
        (OperationsArtifactRef, OperationsArtifactRef.operations_department_id),
        (OperationsBlocker, OperationsBlocker.operations_department_id),
        (OperationsEscalation, OperationsEscalation.operations_department_id),
        (OperationsHandoff, OperationsHandoff.operations_department_id),
        (OperationsDependency, OperationsDependency.operations_department_id),
        (OperationsSystemTool, OperationsSystemTool.operations_department_id),
        (OperationsWorkflow, OperationsWorkflow.operations_department_id),
        (OperationsRole, OperationsRole.operations_department_id),
    ):
        db.query(model).filter(col == department_id).delete()


def materialize_operations_map(db: Session, *, intake_session_id: str, actor_user_id: str, is_admin: bool) -> dict[str, Any]:
    sess = db.query(DepartmentIntakeSession).filter(DepartmentIntakeSession.id == intake_session_id).one_or_none()
    if sess is None:
        raise ValueError("intake session not found")
    if not is_admin and sess.actor_user_id != actor_user_id:
        raise ValueError("not authorized")

    state = state_from_json(sess.state_json)
    profile = state.get("profile") if isinstance(state.get("profile"), dict) else {}
    dept = db.query(OperationsDepartment).filter(OperationsDepartment.id == sess.operations_department_id).one()

    mission = (profile.get("mission") or "").strip()
    if mission:
        dept.description = mission[:12000]
    dept.meta_json = json.dumps(
        {
            **json.loads(dept.meta_json or "{}"),
            "last_materialized_from_intake_session": sess.id,
            "materialization_note": "Rebuilt from intake profile; review before trusting.",
        },
        ensure_ascii=False,
    )

    _clear_department_children(db, dept.id)

    role_ids: dict[str, str] = {}

    def add_role(title: str) -> str:
        t = title.strip()[:500]
        if not t:
            return ""
        if t in role_ids:
            return role_ids[t]
        rid = gen_id()
        db.add(
            OperationsRole(
                id=rid,
                operations_department_id=dept.id,
                title=t,
                description=None,
                meta_json=json.dumps({"from_intake": True}, ensure_ascii=False),
            )
        )
        role_ids[t] = rid
        return rid

    for r in profile.get("roles") or []:
        if isinstance(r, str):
            add_role(r)
        elif isinstance(r, dict) and r.get("title"):
            add_role(str(r["title"]))

    wf_map: dict[str, str] = {}
    ordinal = 0
    for w in profile.get("workflows") or []:
        if not isinstance(w, str):
            continue
        name = w.strip()[:500]
        if not name:
            continue
        wid = gen_id()
        wf_map[name] = wid
        db.add(
            OperationsWorkflow(
                id=wid,
                operations_department_id=dept.id,
                name=name,
                description=None,
                owner_role_id=None,
                inputs_summary=(profile.get("inputs") or "")[:8000] if ordinal == 0 else None,
                outputs_summary=(profile.get("outputs") or "")[:8000] if ordinal == 0 else None,
                ordinal=ordinal,
                meta_json=json.dumps({"from_intake": True}, ensure_ascii=False),
            )
        )
        ordinal += 1

    first_wid = next(iter(wf_map.values()), None)

    for s in profile.get("systems") or []:
        if not isinstance(s, str):
            continue
        nm = s.strip()[:500]
        if not nm:
            continue
        db.add(
            OperationsSystemTool(
                id=gen_id(),
                operations_department_id=dept.id,
                operations_workflow_id=first_wid,
                name=nm,
                category="tool",
                meta_json=json.dumps({"from_intake": True}, ensure_ascii=False),
            )
        )

    for line in profile.get("depends_on") or []:
        if not isinstance(line, str) or not line.strip():
            continue
        db.add(
            OperationsDependency(
                id=gen_id(),
                operations_department_id=dept.id,
                from_ref=dept.name,
                to_ref=line.strip()[:500],
                dependency_type="upstream",
                description="from intake",
                meta_json="{}",
            )
        )

    for line in profile.get("dependents") or []:
        if not isinstance(line, str) or not line.strip():
            continue
        db.add(
            OperationsDependency(
                id=gen_id(),
                operations_department_id=dept.id,
                from_ref=line.strip()[:500],
                to_ref=dept.name,
                dependency_type="downstream",
                description="from intake",
                meta_json="{}",
            )
        )

    for line in profile.get("handoffs") or []:
        if not isinstance(line, str) or not line.strip():
            continue
        db.add(
            OperationsHandoff(
                id=gen_id(),
                operations_department_id=dept.id,
                operations_workflow_id=first_wid,
                to_counterparty=line.strip()[:500],
                description=None,
                meta_json=json.dumps({"from_intake": True}, ensure_ascii=False),
            )
        )

    esc = (profile.get("escalation") or "").strip()
    if esc:
        db.add(
            OperationsEscalation(
                id=gen_id(),
                operations_department_id=dept.id,
                operations_workflow_id=first_wid,
                trigger_summary=esc[:8000],
                path_summary=None,
                meta_json=json.dumps({"from_intake": True}, ensure_ascii=False),
            )
        )

    for line in profile.get("blockers") or []:
        if not isinstance(line, str) or not line.strip():
            continue
        db.add(
            OperationsBlocker(
                id=gen_id(),
                operations_department_id=dept.id,
                operations_workflow_id=first_wid,
                description=line.strip()[:12000],
                meta_json=json.dumps({"from_intake": True}, ensure_ascii=False),
            )
        )

    for line in profile.get("sop_refs") or []:
        if not isinstance(line, str) or not line.strip():
            continue
        db.add(
            OperationsArtifactRef(
                id=gen_id(),
                operations_department_id=dept.id,
                label=line.strip()[:500],
                ref_kind="mentioned",
                meta_json=json.dumps({"from_intake": True}, ensure_ascii=False),
            )
        )

    db.flush()
    return {"operations_department_id": dept.id, "rows_written": True}
