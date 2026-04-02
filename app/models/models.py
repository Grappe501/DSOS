from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        server_default=func.now(),
    )


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    role_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("roles.id"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    department: Mapped[str | None] = mapped_column(String, nullable=True, index=True)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    assigned_to: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="pending", index=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        server_default=func.now(),
    )


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    task_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    schedule_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    trigger_time: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="scheduled", index=True
    )
    channel: Mapped[str] = mapped_column(
        String, nullable=False, default="in_app", index=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        server_default=func.now(),
    )


class Schedule(Base, TimestampMixin):
    __tablename__ = "schedules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    assigned_to: Mapped[str] = mapped_column(String, nullable=False, index=True)
    start_time: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, index=True
    )
    end_time: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="scheduled", index=True
    )
    source: Mapped[str] = mapped_column(String, nullable=False, default="local")
    synced_to_office365: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    office365_event_id: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    recurrence_rule: Mapped[str | None] = mapped_column(String, nullable=True)
    parent_schedule_id: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    created_by_user_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True, index=True
    )
    department: Mapped[str | None] = mapped_column(String, nullable=True, index=True)


class WorkflowState(Base, TimestampMixin):
    __tablename__ = "workflow_states"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    workflow_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    state: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="active", index=True
    )
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        server_default=func.now(),
        index=True,
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    actor_user_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True, index=True
    )
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        server_default=func.now(),
        index=True,
    )


class MessageQueue(Base, TimestampMixin):
    __tablename__ = "message_queue"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    channel: Mapped[str] = mapped_column(String, nullable=False, index=True)
    recipient: Mapped[str] = mapped_column(String, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="pending", index=True
    )
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)