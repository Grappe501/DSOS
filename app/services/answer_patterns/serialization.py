"""JSON-safe trace payloads for truth packet / audit logs."""

from __future__ import annotations

import json
from typing import Any


def pattern_trace_to_dict(trace: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(trace, default=str))
