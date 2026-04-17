"""Canonical source type and lifecycle strings for the business ingestion registry."""

from __future__ import annotations

# High-level kinds aligned with business knowledge categories (extensible).
LEGAL_HANDBOOK = "legal_handbook"
POLICY_MANUAL = "policy_manual"
SOP_WORKFLOW = "sop_workflow"
TRAINING_MODULE = "training_module"
CONTRACT_RULES = "contract_rules"
MEETING_MEMORY = "meeting_memory"
GENERAL_REFERENCE = "general_reference"
FORM_TEMPLATE = "form_template"

SOURCE_TYPES = frozenset(
    {
        LEGAL_HANDBOOK,
        POLICY_MANUAL,
        SOP_WORKFLOW,
        TRAINING_MODULE,
        CONTRACT_RULES,
        MEETING_MEMORY,
        GENERAL_REFERENCE,
        FORM_TEMPLATE,
    }
)

# Source registry lifecycle (business-facing).
LIFECYCLE_REGISTERED = "registered"
LIFECYCLE_ACTIVE = "active"
LIFECYCLE_ARCHIVED = "archived"
LIFECYCLE_SUPERSEDED = "superseded"

# Trust / authority when selecting evidence weight (not legal advice).
AUTHORITY_STATUTORY = "statutory"
AUTHORITY_REGULATORY = "regulatory"
AUTHORITY_CONTRACTUAL = "contractual"
AUTHORITY_INTERNAL = "internal"
AUTHORITY_ADVISORY = "advisory"

AUTHORITY_TIERS = frozenset(
    {
        AUTHORITY_STATUTORY,
        AUTHORITY_REGULATORY,
        AUTHORITY_CONTRACTUAL,
        AUTHORITY_INTERNAL,
        AUTHORITY_ADVISORY,
    }
)

# Per-version ingest state (orthogonal to legal draft/active on legal_source_versions).
VERSION_DRAFT = "draft"
VERSION_VALIDATED = "validated"
VERSION_PROMOTED_ACTIVE = "promoted_active"
VERSION_SUPERSEDED = "superseded"
VERSION_ARCHIVED = "archived"
