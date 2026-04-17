"""Read operations departments and serialized map."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.operations_map import (
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


def list_departments(db: Session, *, limit: int = 50) -> list[dict[str, Any]]:
    rows = db.query(OperationsDepartment).order_by(OperationsDepartment.updated_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "stable_key": r.stable_key,
            "name": r.name,
            "description": r.description,
            "updated_at": str(r.updated_at),
        }
        for r in rows
    ]


def get_department_map(db: Session, *, department_id: str) -> dict[str, Any]:
    d = db.query(OperationsDepartment).filter(OperationsDepartment.id == department_id).one_or_none()
    if d is None:
        raise ValueError("department not found")

    roles = db.query(OperationsRole).filter(OperationsRole.operations_department_id == d.id).all()
    workflows = db.query(OperationsWorkflow).filter(OperationsWorkflow.operations_department_id == d.id).order_by(OperationsWorkflow.ordinal.asc()).all()
    systems = db.query(OperationsSystemTool).filter(OperationsSystemTool.operations_department_id == d.id).all()
    deps = db.query(OperationsDependency).filter(OperationsDependency.operations_department_id == d.id).all()
    handoffs = db.query(OperationsHandoff).filter(OperationsHandoff.operations_department_id == d.id).all()
    esc = db.query(OperationsEscalation).filter(OperationsEscalation.operations_department_id == d.id).all()
    blocks = db.query(OperationsBlocker).filter(OperationsBlocker.operations_department_id == d.id).all()
    arts = db.query(OperationsArtifactRef).filter(OperationsArtifactRef.operations_department_id == d.id).all()

    return {
        "read_only": True,
        "governance_note": "Operations map is steward knowledge; does not override legal/policy citations.",
        "department": {
            "id": d.id,
            "stable_key": d.stable_key,
            "name": d.name,
            "description": d.description,
            "meta": json.loads(d.meta_json or "{}"),
        },
        "roles": [
            {"id": r.id, "title": r.title, "description": r.description, "meta": json.loads(r.meta_json or "{}")}
            for r in roles
        ],
        "workflows": [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "owner_role_id": w.owner_role_id,
                "inputs_summary": w.inputs_summary,
                "outputs_summary": w.outputs_summary,
                "ordinal": w.ordinal,
                "meta": json.loads(w.meta_json or "{}"),
            }
            for w in workflows
        ],
        "systems": [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "workflow_id": s.operations_workflow_id,
                "meta": json.loads(s.meta_json or "{}"),
            }
            for s in systems
        ],
        "dependencies": [
            {
                "id": x.id,
                "from_ref": x.from_ref,
                "to_ref": x.to_ref,
                "dependency_type": x.dependency_type,
                "description": x.description,
                "meta": json.loads(x.meta_json or "{}"),
            }
            for x in deps
        ],
        "handoffs": [
            {
                "id": h.id,
                "workflow_id": h.operations_workflow_id,
                "to_counterparty": h.to_counterparty,
                "description": h.description,
                "meta": json.loads(h.meta_json or "{}"),
            }
            for h in handoffs
        ],
        "escalations": [
            {
                "id": e.id,
                "workflow_id": e.operations_workflow_id,
                "trigger_summary": e.trigger_summary,
                "path_summary": e.path_summary,
                "meta": json.loads(e.meta_json or "{}"),
            }
            for e in esc
        ],
        "blockers": [
            {
                "id": b.id,
                "workflow_id": b.operations_workflow_id,
                "description": b.description,
                "meta": json.loads(b.meta_json or "{}"),
            }
            for b in blocks
        ],
        "artifact_refs": [
            {"id": a.id, "label": a.label, "ref_kind": a.ref_kind, "meta": json.loads(a.meta_json or "{}")}
            for a in arts
        ],
    }
