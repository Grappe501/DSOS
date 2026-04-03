from __future__ import annotations

import datetime as dt
from typing import Any

from app.db.session import SessionLocal
from app.models.models import MessageQueue
from app.services.audit_service import write_audit
from app.utils.logger import log


def queue_message(
    recipient: str,
    content: str,
    channel: str = "in_app",
    *,
    actor_user_id: str | None = None,
    actor_email: str | None = None,
    actor_role: str | None = None,
    actor_department: str | None = None,
    department: str | None = None,
) -> MessageQueue:
    db = SessionLocal()
    try:
        item = MessageQueue(
            channel=channel,
            recipient=recipient,
            content=content,
            status="pending",
            retry_count=0,
            max_retries=3,
            last_error=None,
            updated_at=dt.datetime.utcnow(),
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        write_audit(
            "message.queued",
            "message_queue",
            item.id,
            {"recipient": recipient, "channel": channel, "department": department},
            actor_user_id=actor_user_id,
            actor_email=actor_email,
            actor_role=actor_role,
            actor_department=actor_department or department,
        )
        return item

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def send_message(payload: dict[str, Any]) -> MessageQueue:
    """
    Event-facing wrapper expected by app.core.wiring.

    Accepts an event payload, normalizes it, and queues it for delivery.
    Actual transport is handled later by process_message_queue().
    """
    recipient = payload.get("recipient", "system")
    content = payload.get("message", str(payload))
    channel = payload.get("channel", "in_app")

    item = queue_message(
        recipient=recipient,
        content=content,
        channel=channel,
        actor_user_id=payload.get("actor_user_id"),
        actor_email=payload.get("actor_email"),
        actor_role=payload.get("actor_role"),
        actor_department=payload.get("actor_department"),
        department=payload.get("department"),
    )

    log(f"Queued message {item.id} for recipient={recipient} channel={channel}")
    return item


def process_message_queue() -> int:
    """
    Process pending/failed messages up to max_retries.
    Currently uses a stub success path for transport.
    """
    db = SessionLocal()
    processed = 0

    try:
        pending = (
            db.query(MessageQueue)
            .filter(
                MessageQueue.status.in_(["pending", "failed"]),
                MessageQueue.retry_count < MessageQueue.max_retries,
            )
            .all()
        )

        for item in pending:
            try:
                item.status = "sent"
                item.last_error = None
                item.updated_at = dt.datetime.utcnow()
                db.commit()

                write_audit(
                    "message.sent",
                    "message_queue",
                    item.id,
                    {"recipient": item.recipient, "channel": item.channel},
                )
                processed += 1

            except Exception as exc:
                db.rollback()

                item.retry_count += 1
                item.status = "failed"
                item.last_error = str(exc)
                item.updated_at = dt.datetime.utcnow()
                db.add(item)
                db.commit()

                log(f"Message send failed for {item.id}: {exc}")

        return processed

    finally:
        db.close()
