"""
Normalized retrieval: attach structured knowledge units to Malone evidence bundles.

Does not replace chunk/segment evidence; augments the same truth packet path.
"""

from __future__ import annotations

from app.services.normalized_retrieval.bundle_builder import (
    attach_normalized_to_legal_bundle,
    build_policy_evidence_bundle_with_normalized,
    build_sop_evidence_bundle_with_normalized,
    merge_normalized_into_item,
)
from app.services.normalized_retrieval.legal_selector import fetch_normalized_units_for_legal_chunks
from app.services.normalized_retrieval.policy_selector import (
    resolve_default_policy_source_version_id,
    resolve_default_segment_source_version_id,
    resolve_default_sop_source_version_id,
)

__all__ = [
    "attach_normalized_to_legal_bundle",
    "build_policy_evidence_bundle_with_normalized",
    "build_sop_evidence_bundle_with_normalized",
    "merge_normalized_into_item",
    "fetch_normalized_units_for_legal_chunks",
    "resolve_default_policy_source_version_id",
    "resolve_default_segment_source_version_id",
    "resolve_default_sop_source_version_id",
]
