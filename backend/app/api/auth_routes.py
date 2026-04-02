from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.schemas import LoginRequest, LoginResponse, MeResponse
from app.services.auth_service import authenticate_user, create_access_token

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user, role_name = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user, role_name or "viewer")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": role_name or "viewer",
            "department": user.department,
        },
    }


@auth_router.get("/me", response_model=MeResponse)
def me(current=Depends(get_current_user)):
    user, role_name = current
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": role_name,
        "department": user.department,
    }
