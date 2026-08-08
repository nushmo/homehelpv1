import logging
from typing import Optional, Dict, Any, List
from app.config import settings

logger = logging.getLogger("homehelp.database")

_supabase_client = None


class InMemoryDB:
    """In-memory database fallback for development/testing without real Supabase connection."""

    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}  # id -> user_dict
        self.workers: Dict[str, Dict[str, Any]] = {}  # id -> worker_dict
        self.events: Dict[str, Dict[str, Any]] = {}  # id -> event_dict
        self.analytics_events: List[Dict[str, Any]] = []

    def clear(self):
        self.users.clear()
        self.workers.clear()
        self.events.clear()
        self.analytics_events.clear()


db_store = InMemoryDB()


def get_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if (
        settings.SUPABASE_URL
        and "mock" not in settings.SUPABASE_URL
        and settings.SUPABASE_KEY
        and "mock" not in settings.SUPABASE_KEY
    ):
        try:
            from supabase import create_client

            _supabase_client = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_KEY
            )
            logger.info("Successfully connected to Supabase client.")
            return _supabase_client
        except Exception as e:
            logger.warning(
                f"Failed to initialize Supabase client ({e}). Falling back to in-memory store."
            )
            return None
    else:
        logger.info("Using in-memory store fallback (mock credentials or test mode).")
        return None
