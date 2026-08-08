import uuid
import logging
from datetime import datetime, date
from typing import Optional, List
from app.models.domain import Event, EventType
from app.database.client import get_supabase_client, db_store

logger = logging.getLogger("homehelp.event_repo")


class EventRepository:
    def __init__(self):
        self.supabase = get_supabase_client()

    def create(
        self,
        worker_id: str,
        event_type: EventType,
        event_date: date,
        amount: float = 0.0,
        notes: Optional[str] = None,
    ) -> Event:
        event_id = str(uuid.uuid4())
        now = datetime.now()

        event_data = {
            "id": event_id,
            "worker_id": worker_id,
            "event_type": event_type.value if isinstance(event_type, EventType) else str(event_type),
            "event_date": event_date.isoformat(),
            "amount": float(amount),
            "notes": notes,
            "created_at": now.isoformat(),
        }

        if self.supabase:
            try:
                res = self.supabase.table("events").insert(event_data).execute()
                if res.data:
                    return Event(**res.data[0])
            except Exception as e:
                logger.error(f"Error creating event in Supabase: {e}")

        db_store.events[event_id] = event_data
        return Event(**event_data)

    def get_events_for_month(
        self, worker_id: str, year: int, month: int
    ) -> List[Event]:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        if self.supabase:
            try:
                res = (
                    self.supabase.table("events")
                    .select("*")
                    .eq("worker_id", worker_id)
                    .gte("event_date", start_date.isoformat())
                    .lt("event_date", end_date.isoformat())
                    .execute()
                )
                if res.data:
                    return [Event(**row) for row in res.data]
            except Exception as e:
                logger.error(f"Error fetching events from Supabase: {e}")

        results = []
        for e in db_store.events.values():
            if e["worker_id"] == worker_id:
                e_date = date.fromisoformat(e["event_date"])
                if start_date <= e_date < end_date:
                    results.append(Event(**e))
        return results

    def get_all_by_worker(self, worker_id: str) -> List[Event]:
        if self.supabase:
            try:
                res = (
                    self.supabase.table("events")
                    .select("*")
                    .eq("worker_id", worker_id)
                    .order("event_date", desc=True)
                    .execute()
                )
                if res.data:
                    return [Event(**row) for row in res.data]
            except Exception as e:
                logger.error(f"Error listing events from Supabase: {e}")

        results = []
        for e in db_store.events.values():
            if e["worker_id"] == worker_id:
                results.append(Event(**e))
        results.sort(key=lambda x: x.event_date, reverse=True)
        return results
