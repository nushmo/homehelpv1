import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.domain import Worker
from app.database.client import get_supabase_client, db_store

logger = logging.getLogger("homehelp.worker_repo")


class WorkerRepository:
    def __init__(self):
        self.supabase = get_supabase_client()

    def create(
        self,
        user_id: str,
        name: str,
        monthly_salary: float,
        role: str = "Domestic Worker",
        working_days_per_month: int = 26,
        weekly_off: str = "Sunday",
    ) -> Worker:
        worker_id = str(uuid.uuid4())
        now = datetime.now()

        worker_data = {
            "id": worker_id,
            "user_id": user_id,
            "name": name.strip(),
            "role": role.strip() if role else "Domestic Worker",
            "monthly_salary": float(monthly_salary),
            "working_days_per_month": int(working_days_per_month),
            "weekly_off": weekly_off.strip() if weekly_off else "Sunday",
            "active": True,
            "created_at": now.isoformat(),
        }

        if self.supabase:
            try:
                res = self.supabase.table("workers").insert(worker_data).execute()
                if res.data:
                    return Worker(**res.data[0])
            except Exception as e:
                logger.error(f"Error creating worker in Supabase: {e}")

        db_store.workers[worker_id] = worker_data
        return Worker(**worker_data)

    def get_by_id(self, worker_id: str) -> Optional[Worker]:
        if self.supabase:
            try:
                res = (
                    self.supabase.table("workers")
                    .select("*")
                    .eq("id", worker_id)
                    .execute()
                )
                if res.data and len(res.data) > 0:
                    return Worker(**res.data[0])
            except Exception as e:
                logger.error(f"Error fetching worker by ID from Supabase: {e}")

        if worker_id in db_store.workers:
            return Worker(**db_store.workers[worker_id])
        return None

    def get_all_by_user(
        self, user_id: str, active_only: bool = True
    ) -> List[Worker]:
        if self.supabase:
            try:
                query = (
                    self.supabase.table("workers")
                    .select("*")
                    .eq("user_id", user_id)
                )
                if active_only:
                    query = query.eq("active", True)
                res = query.execute()
                if res.data:
                    return [Worker(**row) for row in res.data]
            except Exception as e:
                logger.error(f"Error listing workers from Supabase: {e}")

        results = []
        for w in db_store.workers.values():
            if w["user_id"] == user_id:
                if not active_only or w.get("active", True):
                    results.append(Worker(**w))
        return results

    def find_by_name(self, user_id: str, name: str) -> Optional[Worker]:
        clean_name = name.strip().lower()
        workers = self.get_all_by_user(user_id, active_only=True)
        # Exact match first
        for w in workers:
            if w.name.lower() == clean_name:
                return w
        # Substring / partial match second
        for w in workers:
            if clean_name in w.name.lower() or w.name.lower() in clean_name:
                return w
        return None

    def update(self, worker_id: str, updates: Dict[str, Any]) -> Optional[Worker]:
        if self.supabase:
            try:
                res = (
                    self.supabase.table("workers")
                    .update(updates)
                    .eq("id", worker_id)
                    .execute()
                )
                if res.data:
                    return Worker(**res.data[0])
            except Exception as e:
                logger.error(f"Error updating worker in Supabase: {e}")

        if worker_id in db_store.workers:
            db_store.workers[worker_id].update(updates)
            return Worker(**db_store.workers[worker_id])
        return None

    def deactivate(self, worker_id: str) -> Optional[Worker]:
        return self.update(worker_id, {"active": False})
