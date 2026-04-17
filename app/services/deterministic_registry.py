from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


ExecutorFn = Callable[..., dict[str, Any]]


@dataclass(slots=True)
class DeterministicAction:
    action_key: str
    description: str
    entity_type: str
    target: str
    read_only: bool
    requires_approval: bool
    executor: ExecutorFn
    required_role: str | None = None
    requires_clarification: bool = False
    clarification_fields: list[str] = field(default_factory=list)
    clarification_prompt: str | None = None
    tags: list[str] = field(default_factory=list)
    is_enabled: bool = True

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "action_key": self.action_key,
            "description": self.description,
            "entity_type": self.entity_type,
            "target": self.target,
            "read_only": self.read_only,
            "requires_approval": self.requires_approval,
            "required_role": self.required_role,
            "requires_clarification": self.requires_clarification,
            "clarification_fields": list(self.clarification_fields),
            "clarification_prompt": self.clarification_prompt,
            "tags": list(self.tags),
            "is_enabled": self.is_enabled,
        }


_REGISTRY: dict[str, DeterministicAction] = {}


def _normalize_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_str_required(value: Any, *, field_name: str) -> str:
    text = _normalize_str(value)
    if not text:
        raise ValueError(f"{field_name} is required")
    return text


def _normalize_bool(value: Any) -> bool:
    return bool(value)


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


def _validate_executor(executor: Any) -> ExecutorFn:
    if not callable(executor):
        raise ValueError("executor must be callable")
    return executor


def _normalize_action(action: DeterministicAction) -> DeterministicAction:
    normalized = DeterministicAction(
        action_key=_normalize_str_required(action.action_key, field_name="action_key"),
        description=_normalize_str_required(action.description, field_name="description"),
        entity_type=_normalize_str_required(action.entity_type, field_name="entity_type"),
        target=_normalize_str_required(action.target, field_name="target"),
        read_only=_normalize_bool(action.read_only),
        requires_approval=_normalize_bool(action.requires_approval),
        executor=_validate_executor(action.executor),
        required_role=_normalize_str(action.required_role),
        requires_clarification=_normalize_bool(action.requires_clarification),
        clarification_fields=_normalize_string_list(action.clarification_fields),
        clarification_prompt=_normalize_str(action.clarification_prompt),
        tags=_normalize_string_list(action.tags),
        is_enabled=_normalize_bool(action.is_enabled),
    )

    if normalized.requires_approval and not normalized.required_role:
        normalized.required_role = "admin"

    if normalized.clarification_fields and not normalized.requires_clarification:
        normalized.requires_clarification = True

    if normalized.requires_clarification and not normalized.clarification_prompt:
        if normalized.clarification_fields:
            normalized.clarification_prompt = (
                f"Please clarify the following before '{normalized.action_key}' can run: "
                + ", ".join(normalized.clarification_fields)
                + "."
            )
        else:
            normalized.clarification_prompt = (
                f"Please clarify your request before '{normalized.action_key}' can run."
            )

    return normalized


def register_action(
    action: DeterministicAction,
    *,
    allow_overwrite: bool = False,
) -> None:
    normalized = _normalize_action(action)

    existing = _REGISTRY.get(normalized.action_key)
    if existing is not None and not allow_overwrite:
        raise ValueError(
            f"deterministic action already registered for action_key '{normalized.action_key}'"
        )

    _REGISTRY[normalized.action_key] = normalized


def register_action_from_parts(
    *,
    action_key: str,
    description: str,
    entity_type: str,
    target: str,
    read_only: bool,
    requires_approval: bool,
    executor: ExecutorFn,
    required_role: str | None = None,
    requires_clarification: bool = False,
    clarification_fields: list[str] | None = None,
    clarification_prompt: str | None = None,
    tags: list[str] | None = None,
    is_enabled: bool = True,
    allow_overwrite: bool = False,
) -> DeterministicAction:
    action = DeterministicAction(
        action_key=action_key,
        description=description,
        entity_type=entity_type,
        target=target,
        read_only=read_only,
        requires_approval=requires_approval,
        executor=executor,
        required_role=required_role,
        requires_clarification=requires_clarification,
        clarification_fields=clarification_fields or [],
        clarification_prompt=clarification_prompt,
        tags=tags or [],
        is_enabled=is_enabled,
    )
    register_action(action, allow_overwrite=allow_overwrite)
    return _REGISTRY[action.action_key]


def unregister_action(action_key: str) -> bool:
    normalized_key = _normalize_str(action_key)
    if not normalized_key:
        return False

    if normalized_key in _REGISTRY:
        del _REGISTRY[normalized_key]
        return True
    return False


def clear_actions() -> None:
    _REGISTRY.clear()


def get_action(action_key: str) -> DeterministicAction | None:
    normalized_key = _normalize_str(action_key)
    if not normalized_key:
        return None
    return _REGISTRY.get(normalized_key)


def has_action(action_key: str) -> bool:
    normalized_key = _normalize_str(action_key)
    if not normalized_key:
        return False
    return normalized_key in _REGISTRY


def list_action_keys() -> list[str]:
    return sorted(_REGISTRY.keys())


def list_actions(
    *,
    include_disabled: bool = True,
) -> list[dict[str, Any]]:
    actions = sorted(_REGISTRY.values(), key=lambda item: item.action_key)

    if not include_disabled:
        actions = [action for action in actions if action.is_enabled]

    return [action.to_public_dict() for action in actions]


def get_registry_snapshot() -> dict[str, Any]:
    actions = sorted(_REGISTRY.values(), key=lambda item: item.action_key)
    return {
        "count": len(actions),
        "action_keys": [action.action_key for action in actions],
        "actions": [action.to_public_dict() for action in actions],
    }