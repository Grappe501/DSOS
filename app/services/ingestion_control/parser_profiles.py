"""
Parser profile registry (code-first).

Profiles describe how structure, chunking, metadata, anchors, and validation
expectations differ by source class. Execution still routes to concrete
pipelines (e.g. Arkansas lawbook) or generic segment writers (policy manual).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

PROFILE_LEGAL_HANDBOOK = "legal_handbook"
PROFILE_POLICY_MANUAL = "policy_manual"
PROFILE_SOP_WORKFLOW = "sop_workflow"
PROFILE_TRAINING_MODULE = "training_module"
PROFILE_CONTRACT_RULES = "contract_rules"
PROFILE_MEETING_MEMORY = "meeting_memory"
PROFILE_GENERAL_REFERENCE = "general_reference"


@dataclass(frozen=True)
class ParserProfile:
    key: str
    default_source_type: str
    structure_rules: str
    chunking_rules: str
    metadata_rules: str
    citation_anchor_rules: str
    validation_expectations: str
    extra: Mapping[str, Any] = field(default_factory=dict)


PARSER_PROFILES: dict[str, ParserProfile] = {
    PROFILE_LEGAL_HANDBOOK: ParserProfile(
        key=PROFILE_LEGAL_HANDBOOK,
        default_source_type="legal_handbook",
        structure_rules="TOC family map (A–H) → legal_document_families → legal_units tree.",
        chunking_rules="Subsection-aware legal_unit_chunks scoped to legal_source_version_id; page grounding when PDF map exists.",
        metadata_rules="Cover metadata, edition label, embedded family revision labels, ingest_profile on legal source version meta.",
        citation_anchor_rules="Deterministic citation_key per chunk; anchor_json with family, citation, pages.",
        validation_expectations="Families present; chunk/citation counts > 0; optional retrieval probes scoped to version.",
        extra={"executor": "legal_ingestion.arkansas_pipeline.ingest_arkansas_handbook_pdf"},
    ),
    PROFILE_POLICY_MANUAL: ParserProfile(
        key=PROFILE_POLICY_MANUAL,
        default_source_type="policy_manual",
        structure_rules="Markdown or plain-text headings; split into ingestion_segments with optional anchor_key slug.",
        chunking_rules="One segment per H1/H2 block (lines starting with #); fallback single body if no headings.",
        metadata_rules="Title and checksum on ingestion_source_versions; steward/domain on ingestion_sources.",
        citation_anchor_rules="Optional anchor_key per segment; no legal citation spine unless cross-linked manually.",
        validation_expectations="At least one segment; checksum present; retrieval_ready flags set when promotion allows.",
        extra={"executor": "ingestion_control.ingest_runner.ingest_generic_text_profile"},
    ),
    PROFILE_SOP_WORKFLOW: ParserProfile(
        key=PROFILE_SOP_WORKFLOW,
        default_source_type="sop_workflow",
        structure_rules="Numbered steps and roles; future: explicit step graph in meta_json.",
        chunking_rules="Segment per major step or section (scaffold; shares policy manual splitter initially).",
        metadata_rules="Role and action_type tags recommended on ingest.",
        citation_anchor_rules="Anchor by SOP id + step ordinal.",
        validation_expectations="Minimum segment count; required metadata keys in profile-specific checklist (scaffold).",
        extra={"executor": "ingestion_control.ingest_runner.ingest_generic_text_profile"},
    ),
    PROFILE_TRAINING_MODULE: ParserProfile(
        key=PROFILE_TRAINING_MODULE,
        default_source_type="training_module",
        structure_rules="Module/lesson headings; optional quiz blocks in meta (deferred).",
        chunking_rules="Segment per lesson section.",
        metadata_rules="topic + role tags.",
        citation_anchor_rules="Lesson slug anchors.",
        validation_expectations="Non-empty content; scaffold only until dedicated parser exists.",
        extra={"executor": "ingestion_control.ingest_runner.ingest_generic_text_profile"},
    ),
    PROFILE_CONTRACT_RULES: ParserProfile(
        key=PROFILE_CONTRACT_RULES,
        default_source_type="contract_rules",
        structure_rules="Clause-oriented segments; deferred deep parsing.",
        chunking_rules="Heading-based segments; large clauses may split by paragraph later.",
        metadata_rules="contractual authority tier; payer/vendor identifiers in meta.",
        citation_anchor_rules="Clause ids when present in text.",
        validation_expectations="Checksum + segment presence; human review_state often required.",
        extra={"executor": "ingestion_control.ingest_runner.ingest_generic_text_profile"},
    ),
    PROFILE_MEETING_MEMORY: ParserProfile(
        key=PROFILE_MEETING_MEMORY,
        default_source_type="meeting_memory",
        structure_rules="Decision log entries; optional dated sections.",
        chunking_rules="Segment per dated section or bullet block.",
        metadata_rules="decision vs note tagging via document_type dimension.",
        citation_anchor_rules="Date + short slug.",
        validation_expectations="Non-empty; low authority tier by default.",
        extra={"executor": "ingestion_control.ingest_runner.ingest_generic_text_profile"},
    ),
    PROFILE_GENERAL_REFERENCE: ParserProfile(
        key=PROFILE_GENERAL_REFERENCE,
        default_source_type="general_reference",
        structure_rules="Loose headings or paragraphs.",
        chunking_rules="Heading-based or single blob.",
        metadata_rules="Minimal.",
        citation_anchor_rules="Optional slug from filename + ordinal.",
        validation_expectations="File readable; at least one segment.",
        extra={"executor": "ingestion_control.ingest_runner.ingest_generic_text_profile"},
    ),
}


def get_profile(key: str) -> ParserProfile:
    if key not in PARSER_PROFILES:
        raise KeyError(f"Unknown parser profile: {key}")
    return PARSER_PROFILES[key]


def list_profile_keys() -> tuple[str, ...]:
    return tuple(sorted(PARSER_PROFILES.keys()))
