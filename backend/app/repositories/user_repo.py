import uuid
import logging
from datetime import datetime
from typing import Optional, List
from app.models.domain import User, UserStatus, ActivationStep
from app.database.client import get_supabase_client, db_store

logger = logging.getLogger("homehelp.user_repo")


class UserRepository:
    def __init__(self):
        self.supabase = get_supabase_client()

    def get_by_phone(self, phone_number: str) -> Optional[User]:
        clean_phone = phone_number.strip().replace(" ", "").replace("-", "")
        if self.supabase:
            try:
                res = (
                    self.supabase.table("users")
                    .select("*")
                    .eq("phone_number", clean_phone)
                    .execute()
                )
                if res.data and len(res.data) > 0:
                    data = res.data[0]
                    return User(**data)
            except Exception as e:
                logger.error(f"Error fetching user by phone from Supabase: {e}")

        # Fallback to in-memory store
        for u in db_store.users.values():
            if u["phone_number"] == clean_phone:
                return User(**u)
        return None

    def get_by_id(self, user_id: str) -> Optional[User]:
        if self.supabase:
            try:
                res = (
                    self.supabase.table("users")
                    .select("*")
                    .eq("id", user_id)
                    .execute()
                )
                if res.data and len(res.data) > 0:
                    return User(**res.data[0])
            except Exception as e:
                logger.error(f"Error fetching user by ID from Supabase: {e}")

        if user_id in db_store.users:
            return User(**db_store.users[user_id])
        return None

    def create(
        self,
        phone_number: str,
        display_name: Optional[str] = None,
        source: str = "WHATSAPP",
    ) -> User:
        clean_phone = phone_number.strip().replace(" ", "").replace("-", "")
        user_id = str(uuid.uuid4())
        now = datetime.now()

        user_data = {
            "id": user_id,
            "phone_number": clean_phone,
            "display_name": display_name or clean_phone,
            "created_at": now.isoformat(),
            "last_seen": now.isoformat(),
            "status": UserStatus.NEW.value,
            "source": source,
            "activation_step": ActivationStep.STARTED_CHAT.value,
        }

        if self.supabase:
            try:
                res = self.supabase.table("users").insert(user_data).execute()
                if res.data:
                    return User(**res.data[0])
            except Exception as e:
                logger.error(f"Error creating user in Supabase: {e}")

        db_store.users[user_id] = user_data
        return User(**user_data)

    def update_activation(
        self, user_id: str, new_step: ActivationStep, status: Optional[UserStatus] = None
    ) -> Optional[User]:
        now = datetime.now()
        update_data = {
            "activation_step": new_step.value,
            "last_seen": now.isoformat(),
        }
        if status:
            update_data["status"] = status.value

        if self.supabase:
            try:
                res = (
                    self.supabase.table("users")
                    .update(update_data)
                    .eq("id", user_id)
                    .execute()
                )
                if res.data:
                    return User(**res.data[0])
            except Exception as e:
                logger.error(f"Error updating user activation in Supabase: {e}")

        if user_id in db_store.users:
            db_store.users[user_id].update(update_data)
            return User(**db_store.users[user_id])
        return None

    def update_last_seen(self, user_id: str) -> Optional[User]:
        now = datetime.now()
        update_data = {"last_seen": now.isoformat()}
        if self.supabase:
            try:
                res = (
                    self.supabase.table("users")
                    .update(update_data)
                    .eq("id", user_id)
                    .execute()
                )
                if res.data:
                    return User(**res.data[0])
            except Exception as e:
                logger.error(f"Error updating user last_seen in Supabase: {e}")

        if user_id in db_store.users:
            db_store.users[user_id].update(update_data)
            return User(**db_store.users[user_id])
        return None

    def list_all(self) -> List[User]:
        if self.supabase:
            try:
                res = self.supabase.table("users").select("*").execute()
                if res.data:
                    return [User(**row) for row in res.data]
            except Exception as e:
                logger.error(f"Error listing users from Supabase: {e}")

        return [User(**u) for u in db_store.users.values()]
