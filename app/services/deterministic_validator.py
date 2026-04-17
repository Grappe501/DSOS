from __future__ import annotations

from typing import Any

from app.services.deterministic_registry import get_action


def _normalize_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_actor(actor: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(actor, dict):
        return {}

    return {
        "id": _normalize_str(actor.get("id")),
        "email": _normalize_str(actor.get("email")),
        "role": _normalize_str(actor.get("role")),
        "department": _normalize_str(actor.get("department")),
    }


def _resolve_role(actor: dict[str, Any], role_name: str | None) -> str | None:
    return _normalize_str(role_name) or actor.get("role")


def _normalize_string_list(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        return []

    normalized: list[str] = []
    seen: set[str] = set()

    for value in values:
        text = _normalize_str(value)
        if not text or text in seen:
            continue
        normalized.append(text)
        seen.add(text)

    return normalized


def _default_clarification_prompt(
    *,
    action_key: str | None,
    clarification_fields: list[str],
) -> str | None:
    if not clarification_fields:
        return None

    field_text = ", ".join(clarification_fields)

    if action_key:
        return (
            f"Additional clarification is required before '{action_key}' can run: "
            f"{field_text}."
        )

    return f"Please clarify the following before execution can continue: {field_text}."


def _normalize_required_role(required_role: Any, *, requires_approval: bool) -> str | None:
    normalized = _normalize_str(required_role)
    if requires_approval and not normalized:
        return "admin"
    return normalized


def validate_action(
    *,
    action_key: str,
    actor: dict[str, Any] | None,
    role_name: str | None = None,
) -> dict[str, Any]:
    """
    Deterministic validation contract.

    This return shape is intentionally stable and should be treated as
    a system contract for:
    - Malone orchestration
    - workflow engine decisions
    - approval gating
    - clarification gating

    Do not remove keys without coordinating all downstream consumers.
    """

    reasons: list[str] = []

    normalized_action_key = _normalize_str(action_key)
    normalized_actor = _normalize_actor(actor)
    resolved_role = _resolve_role(normalized_actor, role_name)

    action = get_action(normalized_action_key) if normalized_action_key else None

    if not normalized_action_key:
        reasons.append("missing_action_key")

    if not action:
        reasons.append("action_not_registered")

    actor_id = normalized_actor.get("id")
    if not actor_id:
        reasons.append("missing_actor_id")

    if not resolved_role:
        reasons.append("missing_actor_role")

    read_only = bool(getattr(action, "read_only", False)) if action else False
    requires_approval = bool(getattr(action, "requires_approval", False)) if action else False
    required_role = _normalize_required_role(
        getattr(action, "required_role", None) if action else None,
        requires_approval=requires_approval,
    )
    entity_type = _normalize_str(getattr(action, "entity_type", None) if action else None)
    target = _normalize_str(getattr(action, "target", None) if action else None)

    clarification_fields = _normalize_string_list(
        getattr(action, "clarification_fields", None) if action else None
    )
    requires_clarification = bool(
        getattr(action, "requires_clarification", False) if action else False
    )

    if clarification_fields and not requires_clarification:
        requires_clarification = True

    clarification_prompt = _normalize_str(
        getattr(action, "clarification_prompt", None) if action else None
    )

    if requires_clarification and not clarification_prompt:
        clarification_prompt = _default_clarification_prompt(
            action_key=normalized_action_key,
            clarification_fields=clarification_fields,
        )

    is_enabled = bool(getattr(action, "is_enabled", True)) if action else False
    if action and not is_enabled:
        reasons.append("action_disabled")

    tags = _normalize_string_list(getattr(action, "tags", None) if action else None)

    is_valid = len(reasons) == 0

    return {
        "is_valid": is_valid,
        "reasons": reasons,
        "action_key": normalized_action_key,
        "read_only": read_only,
        "requires_approval": requires_approval,
        "required_role": required_role,
        "entity_type": entity_type,
        "target": target,
        "actor_id": actor_id,
        "role_name": resolved_role,
        "department": normalized_actor.get("department"),
        "requires_clarification": requires_clarification,
        "clarification_fields": clarification_fields,
        "clarification_prompt": clarification_prompt,
        "is_enabled": is_enabled,
        "tags": tags,
    }