"""
Deterministic folder → control-plane mapping (no ML).

Maps intake subfolders to existing ``source_type`` + ``parser_profile_key`` pairs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.ingestion_control.parser_profiles import (
    PROFILE_CONTRACT_RULES,
    PROFILE_GENERAL_REFERENCE,
    PROFILE_MEETING_MEMORY,
    PROFILE_POLICY_MANUAL,
    PROFILE_SOP_WORKFLOW,
    PROFILE_TRAINING_MODULE,
)
from app.services.ingestion_control.source_types import (
    AUTHORITY_ADVISORY,
    AUTHORITY_CONTRACTUAL,
    AUTHORITY_INTERNAL,
    AUTHORITY_REGULATORY,
    CONTRACT_RULES,
    FORM_TEMPLATE,
    GENERAL_REFERENCE,
    MEETING_MEMORY,
    POLICY_MANUAL,
    SOP_WORKFLOW,
    TRAINING_MODULE,
)


@dataclass(frozen=True)
class ClassificationResult:
    source_type: str
    parser_profile_key: str
    business_domain: str
    authority_tier: str
    internal_category: str
    classification_reason: str
    normalization_profile: str | None  # "policy_manual_v1" or None
    review_recommendation: str
    ingestion_priority: str  # high | medium | low
    active_candidate: bool
    notes: str


# Folder name (under intake root) → mapping. Extend without breaking existing keys.
FOLDER_MAP: dict[str, tuple[str, str, str, str]] = {
    "policy_manual": (POLICY_MANUAL, PROFILE_POLICY_MANUAL, "internal_policy", AUTHORITY_INTERNAL),
    "sop_workflow": (SOP_WORKFLOW, PROFILE_SOP_WORKFLOW, "internal_ops", AUTHORITY_INTERNAL),
    "training_module": (TRAINING_MODULE, PROFILE_TRAINING_MODULE, "training", AUTHORITY_INTERNAL),
    "form_template": (FORM_TEMPLATE, PROFILE_GENERAL_REFERENCE, "forms", AUTHORITY_INTERNAL),
    "reference_sheet": (GENERAL_REFERENCE, PROFILE_GENERAL_REFERENCE, "quick_ref", AUTHORITY_INTERNAL),
    "billing_reference": (CONTRACT_RULES, PROFILE_CONTRACT_RULES, "revenue_cycle", AUTHORITY_CONTRACTUAL),
    "meeting_memory": (MEETING_MEMORY, PROFILE_MEETING_MEMORY, "governance", AUTHORITY_INTERNAL),
    "compliance_notice": (POLICY_MANUAL, PROFILE_POLICY_MANUAL, "compliance", AUTHORITY_REGULATORY),
    "vendor_or_product_reference": (GENERAL_REFERENCE, PROFILE_GENERAL_REFERENCE, "operations", AUTHORITY_ADVISORY),
    "company_profile": (GENERAL_REFERENCE, PROFILE_GENERAL_REFERENCE, "company", AUTHORITY_INTERNAL),
}

TEXT_EXTENSIONS = frozenset({".md", ".txt", ".markdown"})
RISK_EXTENSIONS = frozenset({".pdf", ".docx"})


def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s.strip()).strip("_").lower()
    return s[:80] or "doc"


def content_hint_adjustment(folder: str, filename: str, snippet: str) -> str:
    """Optional tie-break note from filename + first bytes (deterministic)."""
    low = f"{filename} {snippet[:400]}".lower()
    hints: list[str] = []
    if "sop" in low or "runbook" in low:
        hints.append("filename_or_body_suggests_sop_language")
    if "policy" in low or "compliance" in low:
        hints.append("filename_or_body_suggests_policy_language")
    if not hints:
        return "folder_mapping_only"
    return ";".join(hints)


def classify_intake_file(
    *,
    relative_folder: str,
    filename: str,
    file_path: str,
    content_preview: str = "",
) -> ClassificationResult:
    """
    ``relative_folder`` is the first path segment under the intake root (e.g. ``policy_manual``).
    """
    folder = (relative_folder or "unknown").strip().lower().replace("\\", "/").split("/")[0]
    base = FOLDER_MAP.get(folder)
    if not base:
        st, prof, dom, auth = GENERAL_REFERENCE, PROFILE_GENERAL_REFERENCE, "general", "internal"
        reason = f"unknown_folder_default_general_reference:{folder}"
        notes = "Unmapped folder; ingested as general_reference with warnings."
        review_rec = "review_required"
        priority = "low"
        active = True
        norm = None
    else:
        st, prof, dom, auth = base
        reason = f"folder_map:{folder}"
        notes = ""
        review_rec = "ready_for_review" if folder in ("policy_manual", "sop_workflow", "compliance_notice") else "ready_for_ingest_then_review"
        priority = "high" if folder in ("policy_manual", "sop_workflow") else "medium"
        active = True
        norm = "policy_manual_v1" if st in (POLICY_MANUAL, SOP_WORKFLOW) else None

    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower()
    if ext in RISK_EXTENSIONS:
        active = False
        notes = (
            (notes + "; " if notes else "")
            + f"Extension {ext} uses binary/office format; generic text ingest does not extract PDF/DOCX. "
            "Convert to .md/.txt or use a dedicated pipeline."
        )
        review_rec = "blocked_pending_conversion"
        priority = "low"
    elif ext and ext not in TEXT_EXTENSIONS:
        notes = (notes + "; " if notes else "") + f"Non-preferred extension {ext}; may still attempt utf-8 read."
        review_rec = "review_recommended"

    hint = content_hint_adjustment(folder, filename, content_preview)
    full_notes = f"{notes} content_hint={hint}".strip()

    return ClassificationResult(
        source_type=st,
        parser_profile_key=prof,
        business_domain=dom,
        authority_tier=auth,
        internal_category=folder,
        classification_reason=reason,
        normalization_profile=norm,
        review_recommendation=review_rec,
        ingestion_priority=priority,
        active_candidate=active,
        notes=full_notes,
    )


def stable_key_for(folder: str, filename: str, path_checksum8: str) -> str:
    return f"internal_company__{_slug(folder)}__{_slug(filename.rsplit('.', 1)[0])}__{path_checksum8}"
