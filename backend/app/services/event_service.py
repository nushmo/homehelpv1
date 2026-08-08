import logging
from datetime import date, timedelta, datetime
from typing import Optional, Tuple, List
from app.models.domain import Event, EventType, ActivationStep, AnalyticsEventType
from app.repositories.event_repo import EventRepository
from app.repositories.worker_repo import WorkerRepository
from app.repositories.user_repo import UserRepository
from app.repositories.analytics_repo import AnalyticsRepository

logger = logging.getLogger("homehelp.service.event")


class EventService:
    def __init__(self):
        self.event_repo = EventRepository()
        self.worker_repo = WorkerRepository()
        self.user_repo = UserRepository()
        self.analytics_repo = AnalyticsRepository()

    def _parse_date(self, date_str: str) -> date:
        clean = (date_str or "today").strip().lower()
        today = date.today()

        if clean == "today":
            return today
        elif clean == "yesterday":
            return today - timedelta(days=1)
        elif clean == "tomorrow":
            return today + timedelta(days=1)
        else:
            try:
                return date.fromisoformat(clean)
            except ValueError:
                return today

    def record_event(
        self,
        user_id: str,
        event_type: EventType,
        worker_name: Optional[str] = None,
        date_str: str = "today",
        amount: float = 0.0,
        notes: Optional[str] = None,
    ) -> Tuple[Optional[Event], str]:
        workers = self.worker_repo.get_all_by_user(user_id, active_only=True)
        if not workers:
            return None, "⚠️ You don't have any registered workers yet. Please add a worker first (e.g. *Add maid Sunita Salary 9000*)."

        target_worker = None
        if worker_name:
            target_worker = self.worker_repo.find_by_name(user_id, worker_name)

        if not target_worker:
            if len(workers) == 1:
                target_worker = workers[0]
            else:
                names = ", ".join([w.name for w in workers])
                return None, f"⚠️ Please specify which worker: {names}."

        ev_date = self._parse_date(date_str)
        event = self.event_repo.create(
            worker_id=target_worker.id,
            event_type=event_type,
            event_date=ev_date,
            amount=float(amount),
            notes=notes,
        )

        # Update activation step
        user = self.user_repo.get_by_id(user_id)
        if user and user.activation_step in [
            ActivationStep.STARTED_CHAT.value,
            ActivationStep.REGISTERED_FIRST_WORKER.value,
        ]:
            self.user_repo.update_activation(user_id, ActivationStep.LOGGED_FIRST_EVENT)

        self.analytics_repo.log(
            AnalyticsEventType.EVENT_LOGGED,
            user_id=user_id,
            metadata={"event_type": event_type.value, "worker_id": target_worker.id, "amount": amount},
        )

        # Build response message
        formatted_date = ev_date.strftime("%d %b %Y")
        if event_type == EventType.ABSENT:
            msg = f"📝 Recorded *ABSENT* for *{target_worker.name}* on {formatted_date}."
        elif event_type == EventType.HALF_DAY:
            msg = f"📝 Recorded *HALF DAY* for *{target_worker.name}* on {formatted_date}."
        elif event_type == EventType.PLANNED_LEAVE:
            msg = f"📝 Recorded *PLANNED LEAVE* for *{target_worker.name}* on {formatted_date}."
        elif event_type == EventType.ADVANCE:
            msg = f"💸 Recorded advance of *₹{amount:,.0f}* for *{target_worker.name}* on {formatted_date}."
        elif event_type == EventType.BONUS:
            msg = f"🎁 Recorded bonus of *₹{amount:,.0f}* for *{target_worker.name}* on {formatted_date}."
        elif event_type == EventType.PAYMENT:
            msg = f"💵 Recorded payment of *₹{amount:,.0f}* for *{target_worker.name}* on {formatted_date}."
        else:
            msg = f"✅ Event logged for *{target_worker.name}*."

        return event, msg
