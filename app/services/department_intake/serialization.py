"""JSON helpers for intake API responses."""

from __future__ import annotations

import json
from typing import Any


def loads_json(raw: str | None, default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default


def dumps_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)
