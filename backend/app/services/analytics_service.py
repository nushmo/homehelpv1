import logging
from typing import Dict, Any, List
from app.repositories.user_repo import UserRepository
from app.repositories.worker_repo import WorkerRepository
from app.repositories.event_repo import EventRepository
from app.repositories.analytics_repo import AnalyticsRepository
from app.models.domain import ActivationStep, AnalyticsEventType

logger = logging.getLogger("homehelp.service.analytics")


class AnalyticsService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.worker_repo = WorkerRepository()
        self.event_repo = EventRepository()
        self.analytics_repo = AnalyticsRepository()

    def get_funnel_metrics(self) -> Dict[str, Any]:
        users = self.user_repo.list_all()
        total_households = len(users)

        started_chat = 0
        registered_first_worker = 0
        logged_first_event = 0
        generated_first_payment = 0
        returning_users = 0

        for u in users:
            step = u.activation_step
            if step == ActivationStep.STARTED_CHAT.value:
                started_chat += 1
            elif step == ActivationStep.REGISTERED_FIRST_WORKER.value:
                registered_first_worker += 1
            elif step == ActivationStep.LOGGED_FIRST_EVENT.value:
                logged_first_event += 1
            elif step == ActivationStep.GENERATED_FIRST_PAYMENT.value:
                generated_first_payment += 1
            elif step == ActivationStep.RETURNING_USER.value:
                returning_users += 1

        # Cumulative funnel counts
        c_started = total_households
        c_activated = registered_first_worker + logged_first_event + generated_first_payment + returning_users
        c_events = logged_first_event + generated_first_payment + returning_users
        c_payment = generated_first_payment + returning_users
        c_returning = returning_users

        return {
            "total_households": total_households,
            "funnel_stages": {
                "STARTED_CHAT": c_started,
                "REGISTERED_FIRST_WORKER": c_activated,
                "LOGGED_FIRST_EVENT": c_events,
                "GENERATED_FIRST_PAYMENT": c_payment,
                "RETURNING_USER": c_returning,
            },
            "conversion_rates": {
                "activation_rate": round(c_activated / c_started * 100, 2) if c_started > 0 else 0.0,
                "event_logging_rate": round(c_events / c_activated * 100, 2) if c_activated > 0 else 0.0,
                "payment_generation_rate": round(c_payment / c_events * 100, 2) if c_events > 0 else 0.0,
                "retention_rate": round(c_returning / c_payment * 100, 2) if c_payment > 0 else 0.0,
            },
        }

    def get_overview_metrics(self) -> Dict[str, Any]:
        users = self.user_repo.list_all()
        total_households = len(users)

        total_workers = 0
        for u in users:
            workers = self.worker_repo.get_all_by_user(u.id, active_only=True)
            total_workers += len(workers)

        avg_workers_per_household = (
            round(total_workers / total_households, 2) if total_households > 0 else 0.0
        )

        analytics_logs = self.analytics_repo.list_all()

        text_messages = 0
        voice_messages = 0
        unknown_intents = 0
        payment_summaries = 0
        total_salary_events = 0

        for log in analytics_logs:
            e_name = log.event_name
            if e_name == AnalyticsEventType.TEXT_MESSAGE_RECEIVED.value:
                text_messages += 1
            elif e_name == AnalyticsEventType.VOICE_MESSAGE_RECEIVED.value:
                voice_messages += 1
            elif e_name == AnalyticsEventType.UNKNOWN_INTENT.value:
                unknown_intents += 1
            elif e_name == AnalyticsEventType.PAYMENT_GENERATED.value:
                payment_summaries += 1
            elif e_name == AnalyticsEventType.EVENT_LOGGED.value:
                total_salary_events += 1

        total_messages = text_messages + voice_messages
        unknown_intent_rate = (
            round(unknown_intents / total_messages * 100, 2) if total_messages > 0 else 0.0
        )

        return {
            "total_households": total_households,
            "total_workers": total_workers,
            "avg_workers_per_household": avg_workers_per_household,
            "total_salary_events_logged": total_salary_events,
            "total_payment_summaries_generated": payment_summaries,
            "message_channel_breakdown": {
                "text_messages": text_messages,
                "voice_messages": voice_messages,
                "total_messages": total_messages,
            },
            "unknown_intent_count": unknown_intents,
            "unknown_intent_rate_percentage": unknown_intent_rate,
        }
