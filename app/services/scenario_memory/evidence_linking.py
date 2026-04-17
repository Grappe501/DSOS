"""Extract stable source version and normalized unit references from bundles."""

from __future__ import annotations

from typing import Any


def source_version_snapshot(
    *,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if legal_bundle and legal_bundle.get("enabled"):
        out["legal_handbook"] = {"legal_source_version_id": legal_bundle.get("legal_source_version_id")}
    if policy_bundle and policy_bundle.get("enabled"):
        out["policy_manual"] = {"ingestion_source_version_id": policy_bundle.get("ingestion_source_version_id")}
    if sop_bundle and sop_bundle.get("enabled"):
        out["sop_workflow"] = {"ingestion_source_version_id": sop_bundle.get("ingestion_source_version_id")}
    return {k: v for k, v in out.items() if isinstance(v, dict) and any(x is not None for x in v.values())}


def source_types_present(
    *,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
) -> list[str]:
    types: list[str] = []
    for label, b in (
        ("legal_handbook", legal_bundle),
        ("policy_manual", policy_bundle),
        ("sop_workflow", sop_bundle),
    ):
        if b and b.get("enabled") and len(b.get("items") or []) > 0:
            types.append(label)
    return types


def normalized_unit_refs_from_decision_workflow(decision_workflow: dict[str, Any] | None) -> list[str]:
    dw = decision_workflow or {}
    sem = dw.get("source_evidence_map") or {}
    out: list[str] = []
    if isinstance(sem, dict):
        for uid in sem.keys():
            s = str(uid).strip()
            if s:
                out.append(s)
    return sorted(set(out))[:500]
