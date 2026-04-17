"""JSON-safe workflow extraction payloads."""

from __future__ import annotations

import json
from typing import Any


def dumps_extraction(obj: Any) -> dict[str, Any]:
    return json.loads(json.dumps(obj, default=str, ensure_ascii=False))
