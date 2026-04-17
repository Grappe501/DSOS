"""JSON-safe copilot payloads."""

from __future__ import annotations

import json
from typing import Any


def serialize_copilot_block(block: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(block, default=str))
