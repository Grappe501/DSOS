"""
Deterministic, explainable classification for AllCare public website artifacts.

Maps website-facing categories to Malone ingestion_control source_type + parser_profile.
"""

from __future__ import annotations

import re
from typing import Any

WEBSITE_SOURCE_TYPES = (
    "company_profile",
    "policy_manual",
    "sop_workflow",
    "training_module",
    "form_template",
    "compliance_notice",
    "reference_sheet",
    "billing_reference",
    "vendor_or_product_reference",
    "general_reference",
)

from app.services.ingestion_control.parser_profiles import (
    PROFILE_GENERAL_REFERENCE,
    PROFILE_POLICY_MANUAL,
    PROFILE_SOP_WORKFLOW,
    PROFILE_TRAINING_MODULE,
)
from app.services.ingestion_control.source_types import (
    FORM_TEMPLATE,
    GENERAL_REFERENCE,
    POLICY_MANUAL,
    SOP_WORKFLOW,
    TRAINING_MODULE,
)


def _lower(s: str) -> str:
    return (s or "").strip().lower()


def _path_segments(url: str) -> list[str]:
    try:
        from urllib.parse import urlparse

        p = urlparse(url)
        return [x for x in p.path.strip("/").split("/") if x]
    except Exception:
        return []


def _score_rules(url: str, title: str, snippet: str) -> tuple[str, list[str]]:
    u = _lower(url)
    t = _lower(title)
    s = _lower(snippet)
    blob = f"{u} {t} {s}"
    reasons: list[str] = []

    # Compliance: URL must anchor privacy (shared nav text would otherwise label every page).
    if "privacypractices" in u or "/privacy" in u:
        return "compliance_notice", ["url_privacy_anchor"]

    if ("policy" in blob and ("procedure" in blob or "manual" in blob or "policies" in blob)) or "/policy" in u or "/policies" in u or "policy-and-procedure" in u:
        return "policy_manual", ["keyword_or_url_policy_procedure"]

    if re.search(r"\b(form|intake|enrollment form|fax back)\b", blob) and "specialty" not in blob:
        if "nursing" in blob or "med pass" in blob or "/nursing" in u or "/forms" in u or "/form-" in u:
            return "form_template", ["keyword_match_form_or_nursing"]

    if "/forms" in u or "/form-" in u:
        return "form_template", ["url_path_forms"]

    if re.search(r"\b(training|in-?service|in service|presentation|slide|ce|continuing education)\b", blob):
        return "training_module", ["keyword_match_training"]
    if "/training" in u or "/in-service" in u or "inservice" in u:
        return "training_module", ["url_path_training"]

    if re.search(r"\b(billing|invoice|reimbursement|medicare part d|copay)\b", blob) or "/billing" in u:
        return "billing_reference", ["keyword_or_url_billing"]

    if re.search(r"\b(do not crush|insulin storage|quick reference|reference sheet|med pass)\b", blob):
        return "reference_sheet", ["keyword_match_reference"]

    # ExactMed/iMAR appear in boilerplate on many pages — anchor on URL or non-boilerplate product terms.
    if "exactmed" in u or "imar" in u or re.search(
        r"\b(vendor catalog|manufacturer|med cart|device user|blister packaging system)\b", blob[:700]
    ):
        return "vendor_or_product_reference", ["url_or_focused_vendor_terms"]

    if "specialty" in blob and ("enrollment" in blob or "patient" in blob):
        return "vendor_or_product_reference", ["keyword_match_specialty_enrollment"]

    if re.search(r"\b(sop|standard operating|workflow|checklist|procedure steps)\b", blob):
        return "sop_workflow", ["keyword_match_sop_workflow"]

    if u.rstrip("/").endswith("allcarepharmacy.com") or u == "https://www.allcarepharmacy.com" or u == "http://www.allcarepharmacy.com":
        return "company_profile", ["url_likely_homepage"]

    if re.search(
        r"\b(about us|our team|locations|contact|corporate|service line|longterm care|assisted living|correctional)\b",
        blob,
    ):
        return "company_profile", ["keyword_match_company_service"]
    if "/contact" in u or "/about" in u or "/locations" in u:
        return "company_profile", ["url_path_company"]

    if "facility" in blob or "/facility" in u or "/resources" in u:
        return "company_profile", ["keyword_match_facility_resources"]

    return "general_reference", ["default_general_reference"]


def classify_item(
    *,
    url: str,
    title: str = "",
    snippet: str = "",
    asset_filename: str | None = None,
) -> dict[str, Any]:
    fn = _lower(asset_filename or "")
    blob_extra = f"{url} {fn}"
    wtype, reasons = _score_rules(url, title, f"{snippet} {blob_extra}")

    if fn.endswith((".ppt", ".pptx")):
        wtype = "training_module"
        reasons = ["file_extension_presentation"] + reasons
    elif fn.endswith((".xlsx", ".xls")) and "billing" in fn:
        wtype = "billing_reference"
        reasons = ["file_extension_spreadsheet_billing_hint"] + reasons
    elif fn.endswith(".pdf") and "privacy" in fn:
        wtype = "compliance_notice"
        reasons = ["file_extension_pdf_privacy"] + reasons
    elif fn.endswith(".pdf") and "form" in fn:
        wtype = "form_template"
        reasons = ["file_extension_pdf_form_hint"] + reasons

    if wtype not in WEBSITE_SOURCE_TYPES:
        wtype = "general_reference"
        reasons.append("coerce_invalid_to_general_reference")

    return {
        "website_source_type": wtype,
        "classification_reasons": reasons,
        "path_segments": _path_segments(url),
    }


def map_to_malone_ingestion(website_source_type: str) -> dict[str, str]:
    w = website_source_type
    if w in ("policy_manual", "compliance_notice"):
        return {"malone_source_type": POLICY_MANUAL, "parser_profile": PROFILE_POLICY_MANUAL}
    if w == "sop_workflow":
        return {"malone_source_type": SOP_WORKFLOW, "parser_profile": PROFILE_SOP_WORKFLOW}
    if w == "training_module":
        return {"malone_source_type": TRAINING_MODULE, "parser_profile": PROFILE_TRAINING_MODULE}
    if w == "form_template":
        return {"malone_source_type": FORM_TEMPLATE, "parser_profile": PROFILE_GENERAL_REFERENCE}
    return {"malone_source_type": GENERAL_REFERENCE, "parser_profile": PROFILE_GENERAL_REFERENCE}


def suggest_priority_tier(website_source_type: str) -> str:
    if website_source_type in ("company_profile", "policy_manual", "compliance_notice"):
        return "P1"
    if website_source_type in ("sop_workflow", "form_template", "billing_reference"):
        return "P2"
    return "P3"
