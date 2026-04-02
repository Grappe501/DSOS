
import threading
import time
from app.utils.logger import log
from app.services.reminder_service import process_due_reminders
from app.services.messaging_service import process_message_queue

_scheduler_started = False

def _run_scheduler() -> None:
    log("Background scheduler loop started")
    while True:
        try:
            reminders = process_due_reminders()
            messages = process_message_queue()
            if reminders:
                log(f"Processed {reminders} due reminder(s)")
            if messages:
                log(f"Processed {messages} queued message(s)")
        except Exception as exc:
            log(f"Scheduler error: {exc}")
        time.sleep(2)

def start_scheduler() -> None:
    global _scheduler_started
    if _scheduler_started:
        return
    thread = threading.Thread(target=_run_scheduler, daemon=True)
    thread.start()
    _scheduler_started = True
