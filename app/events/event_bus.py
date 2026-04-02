
import json
from typing import Callable, Dict, List
from app.utils.logger import log
from app.db.session import SessionLocal
from app.models.models import EventLog

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[dict], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[dict], None]) -> None:
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        log(f"Subscribed handler to {event_type}")

    def emit(self, event_type: str, payload: dict) -> None:
        log(f"EVENT {event_type}: {payload}")
        db = SessionLocal()
        try:
            db.add(EventLog(event_type=event_type, payload=json.dumps(payload, default=str)))
            db.commit()
        finally:
            db.close()
        for handler in self.subscribers.get(event_type, []):
            handler(payload)

event_bus = EventBus()
