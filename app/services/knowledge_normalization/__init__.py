"""
Knowledge normalization layer: structured units above ingestion evidence.

Public entrypoint: ``normalization_runner.run_normalization``.
"""

from __future__ import annotations

from app.services.knowledge_normalization.normalization_runner import run_normalization
from app.services.knowledge_normalization.normalizer_registry import (
    PROFILE_LEGAL_HANDBOOK_NORM,
    PROFILE_POLICY_MANUAL_NORM,
)

__all__ = [
    "run_normalization",
    "PROFILE_LEGAL_HANDBOOK_NORM",
    "PROFILE_POLICY_MANUAL_NORM",
]
