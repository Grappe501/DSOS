"""Map source types / profile keys to concrete normalizers."""

from __future__ import annotations

PROFILE_LEGAL_HANDBOOK_NORM = "legal_handbook_v1"
PROFILE_POLICY_MANUAL_NORM = "policy_manual_v1"

DEFAULT_PROFILE_BY_SOURCE_TYPE: dict[str, str] = {
    "legal_handbook": PROFILE_LEGAL_HANDBOOK_NORM,
    "policy_manual": PROFILE_POLICY_MANUAL_NORM,
}
