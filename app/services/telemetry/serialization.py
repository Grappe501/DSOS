"""JSON-safe telemetry payloads for HTTP responses."""

from __future__ import annotations

import json
from typing import Any


def telemetry_json_safe(obj: Any) -> dict[str, Any]:
    """Return a plain dict/list structure safe for JSON (no ORM objects)."""
    return json.loads(json.dumps(obj, default=str))
