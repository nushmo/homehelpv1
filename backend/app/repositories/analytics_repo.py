import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.domain import AnalyticsEvent, AnalyticsEventType
from app.database.client import get_supabase_client, db_store

logger = logging.getLogger("homehelp.analytics_repo")


class AnalyticsRepository:
    def __init__(self):
        self.supabase = get_supabase_client()

    def log(
        self,
        event_name: AnalyticsEventType,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AnalyticsEvent:
        event_id = str(uuid.uuid4())
        now = datetime.now()
        event_str = (
            event_name.value
            if isinstance(event_name, AnalyticsEventType)
            else str(event_name)
        )

        data = {
            "id": event_id,
            "user_id": user_id,
            "event_name": event_str,
            "metadata": metadata or {},
            "created_at": now.isoformat(),
        }

        if self.supabase:
            try:
                res = self.supabase.table("analytics_events").insert(data).execute()
                if res.data:
                    return AnalyticsEvent(**res.data[0])
            except Exception as e:
                logger.error(f"Error inserting analytics event to Supabase: {e}")

        db_store.analytics_events.append(data)
        return AnalyticsEvent(**data)

    def list_all(self) -> List[AnalyticsEvent]:
        if self.supabase:
            try:
                res = self.supabase.table("analytics_events").select("*").execute()
                if res.data:
                    return [AnalyticsEvent(**row) for row in res.data]
            except Exception as e:
                logger.error(f"Error listing analytics events from Supabase: {e}")

        return [AnalyticsEvent(**row) for row in db_store.analytics_events]
