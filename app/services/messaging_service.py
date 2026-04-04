from __future__ import annotations

import datetime as dt

from app.db.session import SessionLocal
from app.models.models import MessageQueue
from app.services.audit_service import log_write_action
from app.utils.logger import log


def queue_message(
    recipient: str,
    content: str,
    channel: str = "in_app",
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

        log_write_action(
            db,
            action="message.queued",
            entity_type="message",
            entity_id=item.id,
            actor=None,
            meta_json={
                "recipient": recipient,
                "channel": channel,
                "status": item.status,
            },
        )

        return item

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def send_message(payload: dict) -> MessageQueue:
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
                before = {
                    "status": item.status,
                    "retry_count": item.retry_count,
                    "last_error": item.last_error,
                }

                # Stub transport success path.
                # Replace this block later with SendGrid/Twilio/channel adapters.
                item.status = "sent"
                item.last_error = None
                item.updated_at = dt.datetime.utcnow()
                db.commit()
                db.refresh(item)

                log_write_action(
                    db,
                    action="message.sent",
                    entity_type="message",
                    entity_id=item.id,
                    actor=None,
                    before_json=before,
                    after_json={
                        "status": item.status,
                        "retry_count": item.retry_count,
                        "last_error": item.last_error,
                    },
                    meta_json={
                        "recipient": item.recipient,
                        "channel": item.channel,
                    },
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
                db.refresh(item)

                log(f"Message send failed for {item.id}: {exc}")

        return processed

    finally:
        db.close()