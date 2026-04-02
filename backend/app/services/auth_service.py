from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy.orm import Session

from app.models.models import Role, User
from app.utils.logger import log

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXP_HOURS = 12


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def create_access_token(user: User, role_name: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": role_name,
        "department": user.department,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXP_HOURS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def get_user_with_role(db: Session, email: str) -> tuple[User | None, str | None]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None, None

    role_name = "viewer"
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            role_name = role.name
    return user, role_name


def authenticate_user(db: Session, email: str, password: str) -> tuple[User | None, str | None]:
    user, role_name = get_user_with_role(db, email)
    if not user:
        return None, None
    if not user.is_active:
        return None, None
    if not verify_password(password, user.password_hash):
        return None, None
    return user, role_name


def ensure_seed_data(db: Session) -> None:
    role_names = {
        "owner": "Full system control",
        "admin": "Administrative control",
        "scheduler": "Scheduling operations",
        "viewer": "Read-only access",
    }

    existing_roles = {r.name: r for r in db.query(Role).all()}
    for name, description in role_names.items():
        if name not in existing_roles:
            db.add(Role(name=name, description=description))
    db.commit()

    roles = {r.name: r for r in db.query(Role).all()}
    if not db.query(User).filter(User.email == "owner@local.test").first():
        db.add(
            User(
                email="owner@local.test",
                password_hash=hash_password("ChangeMe123!"),
                full_name="Owner",
                role_id=roles["owner"].id,
                is_active=True,
                department="executive",
            )
        )
        db.commit()
        log("Seeded default owner user: owner@local.test / ChangeMe123!")
