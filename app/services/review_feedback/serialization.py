"""JSON-safe payloads for review APIs."""

from __future__ import annotations

import json
from typing import Any


def json_safe(obj: Any) -> Any:
    return json.loads(json.dumps(obj, default=str))
