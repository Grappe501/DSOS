from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Role, User
from app.services.auth_service import decode_access_token

security = HTTPBearer(auto_error=False)


# ----------------------------
# DB
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Auth
# ----------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> tuple[User, str]:

    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")

    role_name = payload.get("role", "viewer")

    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            role_name = role.name

    return user, role_name


# ----------------------------
# Helpers
# ----------------------------
def is_global_role(role: str) -> bool:
    return role in {"owner", "admin"}


def get_actor_context(current=Depends(get_current_user)) -> dict:
    user, role = current
    return {
        "id": user.id,
        "email": user.email,
        "role": role,
        "department": getattr(user, "department", None),
    }


def require_roles(*allowed_roles: str):
    def _checker(current=Depends(get_current_user)):
        user, role_name = current
        if role_name not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user, role_name

    return _checker