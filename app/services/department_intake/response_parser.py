"""Lightweight deterministic parsing of free-text answers into profile patches."""

from __future__ import annotations

import json
import re
from typing import Any


def _split_listish(text: str) -> list[str]:
    parts = re.split(r"[,;\n]+", text)
    return [p.strip() for p in parts if p.strip()]


def parse_intake_answer(text: str, *, question_key: str | None) -> dict[str, Any]:
    """
    Return a patch dict merged into profile (keys align with followup_generator / map_builder).
    """
    t = (text or "").strip()
    if not t:
        return {}
    low = t.lower()
    patch: dict[str, Any] = {}

    key = (question_key or "").strip().lower()
    if key == "mission":
        patch["mission"] = t
    elif key in ("responsibilities",):
        patch["responsibilities"] = _split_listish(t)
    elif key in ("roles",):
        patch["roles"] = _split_listish(t)
    elif key in ("workflows",):
        patch["workflows"] = _split_listish(t)
    elif key in ("systems",):
        patch["systems"] = _split_listish(t)
    elif key in ("inputs_outputs", "inputs_outputs_combined"):
        if "output" in low or "deliver" in low:
            patch["outputs"] = t
        if "input" in low or not patch:
            patch["inputs"] = t
        if "input" in low and "output" in low:
            patch["inputs"] = t
            patch["outputs"] = t
    elif key in ("dependencies",):
        if "depend on" in low or "upstream" in low:
            patch["depends_on"] = _split_listish(t)
        if "depend" in low and "us" in low:
            patch["dependents"] = _split_listish(t)
        if not patch:
            patch["depends_on"] = _split_listish(t)
    elif key in ("handoffs",):
        patch["handoffs"] = _split_listish(t)
    elif key in ("escalation",):
        patch["escalation"] = t
    elif key in ("blockers",):
        patch["blockers"] = _split_listish(t)
    elif key in ("sop_refs",):
        patch["sop_refs"] = _split_listish(t)
    elif key in ("metrics",):
        patch["metrics"] = t
    else:
        # Heuristic fallback
        if "escalat" in low:
            patch["escalation"] = t
        if "depend" in low or "rely" in low:
            patch["depends_on"] = _split_listish(t)
        if any(s in low for s in ("epic", "cerner", "excel", "email", "teams", "software", "system")):
            patch["systems"] = _split_listish(t)
        if not patch:
            patch["mission"] = t

    return {"profile_patch": patch}


def dumps_parser_output(patch: dict[str, Any]) -> str:
    return json.dumps(patch, ensure_ascii=False, default=str)
