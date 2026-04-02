from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TaskCreateRequest(BaseModel):
    type: str
    assigned_to: str


class TaskCreateResponse(BaseModel):
    task_id: str
    status: str


class ScheduleCreateRequest(BaseModel):
    title: str = Field(..., description="Title for the schedule item")
    assigned_to: str = Field(..., description="Assigned user/resource")
    start_time: datetime
    end_time: datetime
    sync_to_office365: bool = False
    recurrence_rule: str | None = None


class ScheduleUpdateRequest(BaseModel):
    title: str | None = None
    assigned_to: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    recurrence_rule: str | None = None


class ScheduleResponse(BaseModel):
    schedule_id: str
    status: str
    conflict_detected: bool


class CancelResponse(BaseModel):
    schedule_id: str
    status: str


class ConflictResolutionRequest(BaseModel):
    strategy: str = Field(..., description="mark_conflict | auto_shift_30m | cancel_new")


class QueueMessageRequest(BaseModel):
    channel: str = "in_app"
    recipient: str
    content: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class MeResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None = None
    role: str
    department: str | None = None
