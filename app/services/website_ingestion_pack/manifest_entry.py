"""Build a single ingestion-ready manifest entry for an inventoried URL or asset."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from app.services.ingestion_control.tagging import (
    ACTION_TYPE,
    DOCUMENT_TYPE,
    DOMAIN,
    REVIEW_STATE,
    ROLE,
    TOPIC,
)
from app.services.website_ingestion_pack.allcare_rules import (
    classify_item,
    map_to_malone_ingestion,
    suggest_priority_tier,
)


def stable_key_from_url(url: str) -> str:
    norm = re.sub(r"[^a-zA-Z0-9]+", "_", (url or "").lower()).strip("_")
    h = hashlib.sha256((url or "").encode("utf-8")).hexdigest()[:12]
    base = (norm[:48] or "item") + "_" + h
    return f"allcare_web_{base}"


def _suggested_tags(website_type: str, path_segments: list[str]) -> dict[str, str]:
    topic = path_segments[0] if path_segments else "general"
    doc_type = "web_page"
    if website_type == "form_template":
        doc_type = "form"
    elif website_type == "training_module":
        doc_type = "training"
    elif website_type == "policy_manual":
        doc_type = "policy"
    return {
        DOMAIN: "AllCare",
        TOPIC: topic[:80],
        DOCUMENT_TYPE: doc_type,
        ROLE: "mixed",
        ACTION_TYPE: "reference",
        REVIEW_STATE: "pending_human_review",
    }


def build_manifest_entry(
    *,
    url: str,
    title: str,
    snippet: str,
    content_kind: str,
    crawl_category: str | None = None,
    asset_filename: str | None = None,
) -> dict[str, Any]:
    cl = classify_item(url=url, title=title, snippet=snippet, asset_filename=asset_filename)
    wst = cl["website_source_type"]
    mm = map_to_malone_ingestion(wst)
    tier = suggest_priority_tier(wst)
    tags = _suggested_tags(wst, cl.get("path_segments") or [])

    authority = "internal"
    if wst == "compliance_notice":
        authority = "regulatory"

    review_rec = "recommended_before_activation"
    if tier == "P3":
        review_rec = "optional_review"

    active_candidate = tier in ("P1", "P2")

    return {
        "proposed_stable_key": stable_key_from_url(url),
        "source_title": title or url,
        "source_url": url,
        "website_source_type": wst,
        "malone_source_type": mm["malone_source_type"],
        "parser_profile": mm["parser_profile"],
        "crawl_category": crawl_category or wst,
        "business_domain": "Pharmacy_operations",
        "content_kind": content_kind,
        "summary_text": (snippet or "")[:1200],
        "suggested_tags": tags,
        "authority_hint": authority,
        "trust_tier_suggestion": authority,
        "review_recommendation": review_rec,
        "ingestion_priority": tier,
        "promotion_priority_suggestion": tier,
        "active_candidate": "yes" if active_candidate else "no",
        "classification_reasons": cl.get("classification_reasons"),
        "notes": "Website-derived manifest; ingest downloaded or mirrored content via run_business_ingest after review.",
    }
