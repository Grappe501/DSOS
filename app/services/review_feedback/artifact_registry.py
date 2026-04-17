"""Supported artifact types for human review (generic id + type references)."""

from __future__ import annotations

ARTIFACT_NORMALIZED_UNIT = "normalized_unit"
ARTIFACT_SCENARIO_MEMORY = "scenario_memory"
ARTIFACT_DECISION_TRACE = "decision_trace"
ARTIFACT_OPERATING_COPILOT = "operating_copilot_snapshot"
ARTIFACT_WEBSITE_PACK_ENTRY = "website_pack_entry"
ARTIFACT_INGESTION_SOURCE_VERSION = "ingestion_source_version"

ARTIFACT_TYPES = frozenset(
    {
        ARTIFACT_NORMALIZED_UNIT,
        ARTIFACT_SCENARIO_MEMORY,
        ARTIFACT_DECISION_TRACE,
        ARTIFACT_OPERATING_COPILOT,
        ARTIFACT_WEBSITE_PACK_ENTRY,
        ARTIFACT_INGESTION_SOURCE_VERSION,
    }
)


def assert_known_artifact(artifact_type: str) -> None:
    if artifact_type not in ARTIFACT_TYPES:
        raise ValueError(f"unknown artifact_type: {artifact_type}")
