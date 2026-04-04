from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


ORM_CONFIG = ConfigDict(from_attributes=True, populate_by_name=True)


# ----------------------------
# Auth schemas
# ----------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    model_config = ORM_CONFIG

    id: UUID | int | str
    email: EmailStr
    full_name: str | None = None
    role: str
    department: str | None = None
    department_id: UUID | int | str | None = None
    is_active: bool = True


class MeResponse(UserResponse):
    pass


class LoginResponse(BaseModel):
    model_config = ORM_CONFIG

    access_token: str
    token_type: str = "bearer"
    user: MeResponse


# ----------------------------
# Generic API helpers
# ----------------------------

class HealthResponse(BaseModel):
    status: str = "ok"


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str | list[dict[str, Any]] | dict[str, Any]


# ----------------------------
# Schedule schemas
# ----------------------------

class ScheduleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime
    department: str | None = None
    notes: str | None = None
    recurrence_rule: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class ScheduleCreate(ScheduleBase):
    # Current runtime persists assigned_to as a required non-null string.
    assigned_to: str = Field(..., min_length=1, max_length=255)

    # Backward compatibility for older callers / future migration.
    assigned_user_id: UUID | int | str | None = None


class ScheduleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    assigned_to: str | None = Field(default=None, min_length=1, max_length=255)
    assigned_user_id: UUID | int | str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    department: str | None = None
    notes: str | None = None
    recurrence_rule: str | None = None
    status: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class ScheduleResponse(BaseModel):
    model_config = ORM_CONFIG

    id: UUID | int | str
    title: str
    assigned_to: str
    start_time: datetime
    end_time: datetime
    department: str | None = None
    notes: str | None = None
    status: str | None = None
    assigned_user_id: UUID | int | str | None = None
    created_by_user_id: UUID | int | str | None = None
    cancelled_by_user_id: UUID | int | str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    submitted_at: datetime | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None
    cancelled_at: datetime | None = None
    rejection_reason: str | None = None
    recurrence_rule: str | None = None


# ----------------------------
# Audit schemas
# ----------------------------

class AuditLogResponse(BaseModel):
    model_config = ORM_CONFIG

    id: UUID | int | str
    action: str
    entity_type: str
    entity_id: UUID | int | str | None = None
    actor_user_id: UUID | int | str | None = None
    created_at: datetime | None = None
    meta_json: dict[str, Any] | str | None = None


# ----------------------------
# Department / ops schemas
# ----------------------------

class DepartmentResponse(BaseModel):
    model_config = ORM_CONFIG

    id: UUID | int | str
    code: str
    name: str
    description: str | None = None
    is_active: bool = True


class OperationalSummaryResponse(BaseModel):
    totals: dict[str, Any] = Field(default_factory=dict)
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)


class PaginatedResponse(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0