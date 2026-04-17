"""Unit tests for AllCare website → ingestion pack (no network)."""

from __future__ import annotations

from app.services.website_ingestion_pack.allcare_rules import classify_item, map_to_malone_ingestion
from app.services.website_ingestion_pack.manifest_entry import build_manifest_entry, stable_key_from_url
from app.services.website_ingestion_pack.validate_crawl import validate_crawl_run


def test_classify_policy_url():
    r = classify_item(
        url="https://www.allcarepharmacy.com/resources/policy-and-procedures/",
        title="Policy",
        snippet="Our policy and procedure manual for facilities",
    )
    assert r["website_source_type"] == "policy_manual"


def test_classify_company_contact():
    r = classify_item(
        url="https://www.allcarepharmacy.com/contact/",
        title="Contact",
        snippet="Reach our corporate office",
    )
    assert r["website_source_type"] == "company_profile"


def test_classify_compliance():
    r = classify_item(
        url="https://www.allcarepharmacy.com/privacypractices.html",
        title="Privacy",
        snippet="Notice of privacy practices",
    )
    assert r["website_source_type"] == "compliance_notice"


def test_map_to_malone():
    m = map_to_malone_ingestion("compliance_notice")
    assert m["malone_source_type"] == "policy_manual"
    assert m["parser_profile"] == "policy_manual"


def test_stable_key_deterministic():
    a = stable_key_from_url("https://www.allcarepharmacy.com/foo")
    b = stable_key_from_url("https://www.allcarepharmacy.com/foo")
    assert a == b
    assert a.startswith("allcare_web_")


def test_manifest_entry_shape():
    e = build_manifest_entry(
        url="https://www.allcarepharmacy.com/training/slides.pptx",
        title="slides.pptx",
        snippet="",
        content_kind="download",
        asset_filename="slides.pptx",
    )
    assert e["website_source_type"] == "training_module"
    assert "suggested_tags" in e
    assert e["ingestion_priority"] in ("P1", "P2", "P3")


def test_validate_pass_with_warnings():
    v = validate_crawl_run(
        target_reachable=True,
        inventory_count=20,
        manifests_written=True,
        entries_by_type={"company_profile": 5, "general_reference": 15},
        weak_unclassified_ratio=0.2,
    )
    # Warnings present (e.g. weak classification) force non-PASS branch when rules tighten.
    assert v["overall_status"] in ("PASS", "PASS_WITH_WARNINGS")


def test_validate_fail_unreachable():
    v = validate_crawl_run(
        target_reachable=False,
        inventory_count=0,
        manifests_written=False,
        entries_by_type={},
        weak_unclassified_ratio=0.0,
    )
    assert v["overall_status"] == "FAIL"
