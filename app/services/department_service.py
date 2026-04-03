"""Department service starter for v0.7.0."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import Session

try:
    from app.models.models import Department, User, UserDepartmentMembership
except Exception:  # pragma: no cover - starter template may precede model changes
    Department = object  # type: ignore
    User = object  # type: ignore
    UserDepartmentMembership = object  # type: ignore


@dataclass(slots=True)
class ScopeDecision:
    allowed: bool
    reason: str


def list_departments(db: Session):
    """Return active departments ordered for admin UIs."""
    return (
        db.query(Department)
        .filter(getattr(Department, "is_active", True) == True)  # noqa: E712
        .order_by(getattr(Department, "name", None))
        .all()
    )


def get_user_memberships(db: Session, user_id: str):
    """Return active department memberships for a user."""
    return (
        db.query(UserDepartmentMembership)
        .filter(
            UserDepartmentMembership.user_id == user_id,
            UserDepartmentMembership.is_active == True,  # noqa: E712
        )
        .all()
    )


def get_user_department_codes(db: Session, user_id: str) -> list[str]:
    memberships = get_user_memberships(db, user_id)
    codes: list[str] = []
    for membership in memberships:
        department = getattr(membership, "department", None)
        code = getattr(department, "code", None)
        if code:
            codes.append(code)
    return codes


def user_can_access_department(db: Session, user, department_code: str | None) -> ScopeDecision:
    """Owner is global; others require an active membership when a department is targeted."""
    role_name = getattr(user, "role_name", None) or getattr(user, "role", None) or ""
    if role_name in {"owner"}:
        return ScopeDecision(True, "owner-global")
    if not department_code:
        return ScopeDecision(True, "no-department-specified")
    allowed_codes = set(get_user_department_codes(db, getattr(user, "id")))
    if department_code in allowed_codes:
        return ScopeDecision(True, "membership-match")
    return ScopeDecision(False, f"user lacks scope for department={department_code}")


def user_can_approve_department(db: Session, user, department_code: str | None) -> ScopeDecision:
    role_name = getattr(user, "role_name", None) or getattr(user, "role", None) or ""
    if role_name == "owner":
        return ScopeDecision(True, "owner-global")
    memberships = get_user_memberships(db, getattr(user, "id"))
    for membership in memberships:
        department = getattr(membership, "department", None)
        if getattr(department, "code", None) == department_code and getattr(membership, "can_approve", False):
            return ScopeDecision(True, "membership-can-approve")
    if role_name == "admin" and department_code in set(get_user_department_codes(db, getattr(user, "id"))):
        return ScopeDecision(True, "admin-scoped")
    return ScopeDecision(False, f"user lacks approval scope for department={department_code}")
