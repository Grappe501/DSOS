
from app.utils.logger import log

class Office365CalendarAdapter:
    def create_event(self, schedule: dict) -> dict:
        log(f"[Office365 Stub] create_event called for schedule {schedule['id']}")
        return {"success": True, "office365_event_id": f"o365-{schedule['id']}"}

    def update_event(self, office365_event_id: str, schedule: dict) -> dict:
        log(f"[Office365 Stub] update_event called for {office365_event_id}")
        return {"success": True}

    def cancel_event(self, office365_event_id: str) -> dict:
        log(f"[Office365 Stub] cancel_event called for {office365_event_id}")
        return {"success": True}

office365_adapter = Office365CalendarAdapter()
