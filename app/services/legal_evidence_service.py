"""
Build legal evidence bundles for Malone's truth packet and guarded lookup path.

Purpose:
    Resolve default handbook version scope, run citation-first then lexical retrieval,
    dedupe chunks, and enrich the truth packet without bypassing Malone's main flow.

Integration:
    Called from ``malone_service.handle_malone_request`` when legal feature flags and
    ``legal_handbook`` intent target are active.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_handbook import LegalSourceVersion
from app.services.legal_assistant.guardrails import legal_handbook_forbidden_claims
from app.services.legal_retrieval.citation_lookup import find_chunks_by_citation_text
from app.services.legal_retrieval.lexical import search_legal_chunks_lexical
from app.services.truth_packet_service import _base_claim


def malone_legal_evidence_enabled() -> bool:
    v = os.environ.get("MALONE_LEGAL_EVIDENCE_ENABLED", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def malone_legal_lookup_enabled() -> bool:
    v = os.environ.get("MALONE_LEGAL_LOOKUP_ENABLED", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def malone_normalized_retrieval_enabled() -> bool:
    """Augment legal/policy bundles with normalized knowledge units when available."""
    v = os.environ.get("MALONE_NORMALIZED_RETRIEVAL_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return malone_legal_evidence_enabled()


def malone_policy_evidence_enabled() -> bool:
    v = os.environ.get("MALONE_POLICY_EVIDENCE_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return malone_legal_evidence_enabled()


def malone_policy_lookup_enabled() -> bool:
    """Deterministic policy manual answer path (like ``MALONE_LEGAL_LOOKUP_ENABLED``)."""
    v = os.environ.get("MALONE_POLICY_LOOKUP_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return malone_policy_evidence_enabled()


def malone_sop_evidence_enabled() -> bool:
    from app.services.decision_reasoning.fallback import malone_sop_evidence_enabled as _sop_ev

    return _sop_ev()


def malone_sop_lookup_enabled() -> bool:
    from app.services.decision_reasoning.fallback import malone_sop_lookup_enabled as _sop_lu

    return _sop_lu()


def malone_decision_reasoning_enabled() -> bool:
    from app.services.decision_reasoning.fallback import malone_decision_reasoning_enabled as _dr

    return _dr()


def malone_cross_source_decision_enabled() -> bool:
    from app.services.decision_reasoning.fallback import malone_cross_source_decision_enabled as _xc

    return _xc()


def resolve_default_legal_source_version_id(db: Session) -> str | None:
    """Latest ingested compilation (by row creation time)."""
    row = (
        db.query(LegalSourceVersion)
        .order_by(LegalSourceVersion.created_at.desc())
        .limit(1)
        .one_or_none()
    )
    return str(row.id) if row else None


_CITATION_LIKE = re.compile(r"^\s*(\d{1,3}-\d{1,3}-\d{1,4}|AC\.[A-Z]\.[0-9]+|Ark\.\s*Code)\b", re.I)


def _query_strategy(message: str) -> str:
    t = (message or "").strip()
    if len(t) < 80 and _CITATION_LIKE.search(t):
        return "citation_first"
    if re.search(r"\b\d{2,3}-\d{2,3}-\d{2,4}\b", t):
        return "citation_first"
    return "lexical"


def _dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for it in items:
        cid = str(it.get("legal_unit_chunk_id") or "")
        if not cid or cid in seen:
            continue
        seen.add(cid)
        out.append(it)
    return out


def build_legal_evidence_bundle(
    db: Session,
    message: str,
    *,
    limit: int = 8,
    legal_source_version_id: str | None = None,
) -> dict[str, Any]:
    """
    Returns structured evidence for truth-packet attachment.

    ``items`` are deduped chunk-level dicts compatible with ``answer_formatter``.
    """
    version_id = legal_source_version_id or resolve_default_legal_source_version_id(db)
    strategy = _query_strategy(message)
    raw = (message or "").strip()
    items: list[dict[str, Any]] = []
    warnings: list[str] = []

    if not version_id:
        warnings.append("no_legal_source_version_in_database")
        return {
            "enabled": True,
            "legal_source_version_id": None,
            "query_strategy": strategy,
            "items": [],
            "warnings": warnings,
        }

    if strategy == "citation_first":
        # Prefer statute-like and short citation queries
        cite_hits = find_chunks_by_citation_text(
            db, raw, legal_source_version_id=version_id
        )
        items.extend(cite_hits)
        if not items and len(raw) <= 120:
            items.extend(
                find_chunks_by_citation_text(
                    db, raw.split()[0] if raw.split() else raw,
                    legal_source_version_id=version_id,
                )
            )

    if not items:
        items.extend(
            search_legal_chunks_lexical(
                db,
                raw,
                limit=limit,
                legal_source_version_id=version_id,
                min_family_span_confidence=None,
            )
        )

    items = _dedupe_items(items)[:limit]
    if not items:
        warnings.append("no_lexical_or_citation_hits")

    out = {
        "enabled": True,
        "legal_source_version_id": version_id,
        "query_strategy": strategy,
        "items": items,
        "warnings": warnings,
    }
    if malone_normalized_retrieval_enabled():
        from app.services.normalized_retrieval.bundle_builder import attach_normalized_to_legal_bundle

        attach_normalized_to_legal_bundle(db, out, enabled=True)
    else:
        out["normalized"] = {"enabled": False, "reason": "MALONE_NORMALIZED_RETRIEVAL_DISABLED"}
    return out


def build_policy_evidence_bundle(
    db: Session,
    message: str,
    *,
    ingestion_source_version_id: str | None = None,
    limit: int = 8,
) -> dict[str, Any]:
    """Policy manual segment retrieval + normalized attachment (same additive pattern as legal)."""
    from app.services.normalized_retrieval.policy_selector import resolve_default_policy_source_version_id

    vid = ingestion_source_version_id or resolve_default_policy_source_version_id(db)
    from app.services.normalized_retrieval.bundle_builder import build_policy_evidence_bundle_with_normalized

    return build_policy_evidence_bundle_with_normalized(
        db,
        message,
        ingestion_source_version_id=vid,
        limit=limit,
        normalized_enabled=malone_normalized_retrieval_enabled(),
    )


def build_sop_evidence_bundle(
    db: Session,
    message: str,
    *,
    ingestion_source_version_id: str | None = None,
    limit: int = 8,
) -> dict[str, Any]:
    """SOP / workflow segment retrieval + normalized attachment."""
    from app.services.normalized_retrieval.policy_selector import resolve_default_sop_source_version_id
    from app.services.normalized_retrieval.bundle_builder import build_sop_evidence_bundle_with_normalized

    vid = ingestion_source_version_id or resolve_default_sop_source_version_id(db)
    return build_sop_evidence_bundle_with_normalized(
        db,
        message,
        ingestion_source_version_id=vid,
        limit=limit,
        normalized_enabled=malone_normalized_retrieval_enabled(),
    )


def enrich_truth_packet_with_legal(
    packet: dict[str, Any],
    *,
    intent: dict[str, Any],
    legal_evidence_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    """Attach legal evidence and extra claims; keep additive and inspectable."""
    target = intent.get("target")
    packet["legal_evidence"] = legal_evidence_bundle
    meta = packet.get("packet_meta") or {}
    bundle = legal_evidence_bundle or {}
    items = bundle.get("items") or []
    meta["legal_evidence_item_count"] = len(items)
    meta["legal_evidence_warnings"] = list(bundle.get("warnings") or [])
    meta["legal_query_strategy"] = bundle.get("query_strategy")
    norm = bundle.get("normalized") or {}
    meta["legal_normalized_enabled"] = bool(norm.get("enabled"))
    meta["legal_normalized_unit_groups"] = sum(
        len(v) for v in (norm.get("units_by_chunk_id") or {}).values()
    )
    packet["packet_meta"] = meta

    if target != "legal_handbook":
        return packet

    claims = packet.get("allowed_claims") or []
    for idx, it in enumerate(items[:25]):
        claims.append(
            _base_claim(
                f"legal_evidence_{idx}",
                "legal handbook excerpt",
                {
                    "legal_unit_chunk_id": it.get("legal_unit_chunk_id"),
                    "citation_key": it.get("citation_key"),
                    "legal_source_version_id": it.get("legal_source_version_id"),
                    "family_code": it.get("family_code"),
                    "subsection_path": it.get("subsection_path"),
                    "page_start": it.get("page_start"),
                    "page_end": it.get("page_end"),
                },
            )
        )
    packet["allowed_claims"] = claims[:50]

    forbid = list(packet.get("forbidden_claims") or [])
    forbid.extend(legal_handbook_forbidden_claims())
    packet["forbidden_claims"] = forbid
    return packet


def enrich_truth_packet_with_policy(
    packet: dict[str, Any],
    *,
    intent: dict[str, Any],
    policy_evidence_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    """Attach policy segment evidence + normalized meta to the truth packet."""
    target = intent.get("target")
    packet["policy_evidence"] = policy_evidence_bundle
    meta = packet.get("packet_meta") or {}
    bundle = policy_evidence_bundle or {}
    items = bundle.get("items") or []
    meta["policy_evidence_item_count"] = len(items)
    meta["policy_evidence_warnings"] = list(bundle.get("warnings") or [])
    norm = bundle.get("normalized") or {}
    meta["policy_normalized_enabled"] = bool(norm.get("enabled"))
    meta["policy_normalized_unit_groups"] = sum(
        len(v) for v in (norm.get("units_by_segment_id") or {}).values()
    )
    packet["packet_meta"] = meta

    if target != "policy_manual":
        return packet

    claims = packet.get("allowed_claims") or []
    for idx, it in enumerate(items[:25]):
        claims.append(
            _base_claim(
                f"policy_evidence_{idx}",
                "policy manual excerpt",
                {
                    "ingestion_segment_id": it.get("ingestion_segment_id"),
                    "heading": it.get("heading"),
                    "ordinal": it.get("ordinal"),
                },
            )
        )
    packet["allowed_claims"] = claims[:50]
    return packet


def enrich_truth_packet_with_sop(
    packet: dict[str, Any],
    *,
    intent: dict[str, Any],
    sop_evidence_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    """Attach SOP segment evidence + normalized meta."""
    target = intent.get("target")
    packet["sop_evidence"] = sop_evidence_bundle
    meta = packet.get("packet_meta") or {}
    bundle = sop_evidence_bundle or {}
    items = bundle.get("items") or []
    meta["sop_evidence_item_count"] = len(items)
    meta["sop_evidence_warnings"] = list(bundle.get("warnings") or [])
    norm = bundle.get("normalized") or {}
    meta["sop_normalized_enabled"] = bool(norm.get("enabled"))
    meta["sop_normalized_unit_groups"] = sum(
        len(v) for v in (norm.get("units_by_segment_id") or {}).values()
    )
    packet["packet_meta"] = meta

    if target != "sop_workflow":
        return packet

    claims = packet.get("allowed_claims") or []
    for idx, it in enumerate(items[:25]):
        claims.append(
            _base_claim(
                f"sop_evidence_{idx}",
                "sop workflow excerpt",
                {
                    "ingestion_segment_id": it.get("ingestion_segment_id"),
                    "heading": it.get("heading"),
                    "ordinal": it.get("ordinal"),
                },
            )
        )
    packet["allowed_claims"] = claims[:50]
    return packet


def enrich_truth_packet_with_decision_workflow(
    packet: dict[str, Any],
    decision_block: dict[str, Any] | None,
) -> dict[str, Any]:
    """Attach structured decision/workflow reasoning (additive audit metadata)."""
    from app.services.decision_reasoning.fallback import should_emit_structured_sections
    from app.services.legal_assistant.guardrails import (
        decision_workflow_supplementary_forbidden_claims,
        workflow_extraction_weak_signal_forbidden_claims,
    )

    meta = packet.get("packet_meta") or {}
    block = decision_block or {}
    meta["decision_workflow_enabled"] = bool(block.get("enabled"))
    meta["decision_workflow_fallback_reason"] = block.get("fallback_reason")
    if block.get("sources_present"):
        meta["decision_workflow_sources"] = list(block["sources_present"])
    if block.get("trust_tier"):
        meta["decision_workflow_trust_tier"] = block.get("trust_tier")
    packet["packet_meta"] = meta
    packet["decision_workflow"] = block
    if should_emit_structured_sections(block):
        forb = list(packet.get("forbidden_claims") or [])
        forb.extend(decision_workflow_supplementary_forbidden_claims())
        wfa = block.get("workflow_extraction_assessment") or {}
        if wfa.get("use_minimal_workflow_guidance"):
            forb.extend(workflow_extraction_weak_signal_forbidden_claims())
        packet["forbidden_claims"] = forb[:80]
    return packet


def enrich_truth_packet_with_operating_copilot(
    packet: dict[str, Any],
    copilot_block: dict[str, Any] | None,
) -> dict[str, Any]:
    """Attach business operating copilot block (additive)."""
    from app.services.legal_assistant.guardrails import operating_copilot_supplementary_forbidden_claims

    block = copilot_block or {}
    packet["operating_copilot"] = block
    meta = packet.get("packet_meta") or {}
    meta["operating_copilot_enabled"] = bool(block.get("enabled"))
    meta["operating_copilot_scenario"] = block.get("primary_scenario")
    meta["operating_copilot_fallback"] = block.get("fallback_reason")
    packet["packet_meta"] = meta
    if block.get("enabled") and (block.get("guidance") or block.get("emit_minimal_only")):
        forb = list(packet.get("forbidden_claims") or [])
        forb.extend(operating_copilot_supplementary_forbidden_claims())
        packet["forbidden_claims"] = forb[:80]
    return packet


def persist_legal_answer_trace(
    db: Session,
    *,
    proposal_id: str | None,
    bundle: dict[str, Any],
    query_fingerprint: str | None = None,
    verified: bool = False,
) -> None:
    """Best-effort audit row for the legal lookup path."""
    from app.models.legal_handbook import LegalAnswerTrace

    items = bundle.get("items") or []
    chunk_ids = [str(it.get("legal_unit_chunk_id")) for it in items if it.get("legal_unit_chunk_id")]
    cite_keys = [str(it.get("citation_key")) for it in items if it.get("citation_key")]
    row = LegalAnswerTrace(
        proposal_id=proposal_id,
        query_fingerprint=query_fingerprint,
        chunk_ids_json=json.dumps(chunk_ids[:200], ensure_ascii=False),
        citation_keys_json=json.dumps(cite_keys[:200], ensure_ascii=False),
        verified=verified,
        meta_json=json.dumps(
            {
                "warnings": bundle.get("warnings"),
                "strategy": bundle.get("query_strategy"),
                "legal_source_version_id": bundle.get("legal_source_version_id"),
            },
            ensure_ascii=False,
        ),
    )
    db.add(row)
    db.flush()
