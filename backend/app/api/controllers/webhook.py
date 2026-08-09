import logging
from datetime import date
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, Query, Response
from app.config import settings
from app.repositories.user_repo import UserRepository
from app.repositories.worker_repo import WorkerRepository
from app.repositories.event_repo import EventRepository
from app.repositories.analytics_repo import AnalyticsRepository
from app.ai.gemini_parser import GeminiIntentParser
from app.ai.voice_handler import VoiceHandler
from app.services.worker_service import WorkerService
from app.services.event_service import EventService
from app.services.reply_service import ReplyService
from app.services.whatsapp_service import WhatsAppService
from app.salary.engine import SalaryEngine
from app.schemas.intent import IntentType, ParsedIntent
from app.models.domain import EventType, AnalyticsEventType, ActivationStep, UserStatus

logger = logging.getLogger("homehelp.controller.webhook")

router = APIRouter(tags=["Webhook"])

user_repo = UserRepository()
worker_repo = WorkerRepository()
event_repo = EventRepository()
analytics_repo = AnalyticsRepository()

intent_parser = GeminiIntentParser()
voice_handler = VoiceHandler()
worker_service = WorkerService()
event_service = EventService()
whatsapp_service = WhatsAppService()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """WhatsApp Cloud API Webhook Verification GET Endpoint."""
    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully.")
        return Response(content=hub_challenge, media_type="text/plain")
    logger.warning("WhatsApp webhook verification failed. Token mismatch.")
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@router.post("/webhook")
async def handle_whatsapp_webhook(request: Request):
    """WhatsApp Cloud API Webhook POST Receiver."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    print(f"📥 [WHATSAPP WEBHOOK RECEIVED]: {body}", flush=True)
    logger.info(f"Incoming WhatsApp webhook payload: {body}")

    # Extract entry data
    entries = body.get("entry", [])
    if not entries:
        return {"status": "ignored", "reason": "no entries"}

    for entry in entries:
        for change in entry.get("changes", []):
            val = change.get("value", {})
            messages = val.get("messages", [])
            contacts = val.get("contacts", [])

            if not messages:
                continue

            for msg in messages:
                sender_phone = msg.get("from")
                if not sender_phone:
                    continue

                display_name = None
                if contacts:
                    profile = contacts[0].get("profile", {})
                    display_name = profile.get("name")

                process_user_message(sender_phone, display_name, msg)

    return {"status": "ok"}


def process_user_message(phone_number: str, display_name: Optional[str], msg: Dict[str, Any]):
    """Processes a single incoming message from a WhatsApp user."""
    # 1. Fetch or register homeowner user
    user = user_repo.get_by_phone(phone_number)
    if not user:
        user = user_repo.create(phone_number, display_name=display_name)
        analytics_repo.log(AnalyticsEventType.USER_STARTED_CHAT, user_id=user.id)
    else:
        user_repo.update_last_seen(user.id)

    msg_type = msg.get("type", "text")
    parsed_intent: ParsedIntent

    # 2. Extract Intent from text or audio
    if msg_type == "text":
        text_body = msg.get("text", {}).get("body", "")
        analytics_repo.log(
            AnalyticsEventType.TEXT_MESSAGE_RECEIVED,
            user_id=user.id,
            metadata={"text": text_body},
        )
        parsed_intent = intent_parser.parse(text_body)

    elif msg_type == "audio":
        media_id = msg.get("audio", {}).get("id")
        mime_type = msg.get("audio", {}).get("mime_type", "audio/ogg")
        analytics_repo.log(
            AnalyticsEventType.VOICE_MESSAGE_RECEIVED,
            user_id=user.id,
            metadata={"media_id": media_id},
        )
        parsed_intent = voice_handler.process_voice_media(media_id, mime_type)

    else:
        parsed_intent = ParsedIntent(intent=IntentType.UNKNOWN)

    # 3. Route parsed intent to Business Logic
    reply_text = route_intent_to_business_logic(user, parsed_intent)

    # 4. Send outgoing WhatsApp response
    whatsapp_service.send_text_message(user.phone_number, reply_text)


def route_intent_to_business_logic(user: Any, parsed: ParsedIntent) -> str:
    intent = parsed.intent

    if intent == IntentType.REGISTER_WORKER:
        if not parsed.worker_name or not parsed.monthly_salary:
            return parsed.clarification_needed or "⚠️ Please provide worker name and monthly salary (e.g. *Add maid Sunita Salary 9000*)."
        _, msg = worker_service.register_worker(
            user_id=user.id,
            name=parsed.worker_name,
            monthly_salary=parsed.monthly_salary,
            role=parsed.role or "Domestic Worker",
            working_days_per_month=parsed.working_days_per_month or 26,
            weekly_off=parsed.weekly_off or "Sunday",
        )
        return msg

    elif intent == IntentType.REMOVE_WORKER:
        if not parsed.worker_name:
            return "⚠️ Please specify which worker to remove (e.g. *Remove Sunita*)."
        _, msg = worker_service.remove_worker(user.id, parsed.worker_name)
        return msg

    elif intent == IntentType.UPDATE_WORKER:
        if not parsed.worker_name or not parsed.monthly_salary:
            return "⚠️ Please specify worker name and updated salary (e.g. *Sunita salary is now 9500*)."
        _, msg = worker_service.update_salary(user.id, parsed.worker_name, parsed.monthly_salary)
        return msg

    elif intent in [
        IntentType.ABSENT,
        IntentType.HALF_DAY,
        IntentType.PLANNED_LEAVE,
        IntentType.ADVANCE,
        IntentType.BONUS,
        IntentType.PAYMENT,
    ]:
        ev_map = {
            IntentType.ABSENT: EventType.ABSENT,
            IntentType.HALF_DAY: EventType.HALF_DAY,
            IntentType.PLANNED_LEAVE: EventType.PLANNED_LEAVE,
            IntentType.ADVANCE: EventType.ADVANCE,
            IntentType.BONUS: EventType.BONUS,
            IntentType.PAYMENT: EventType.PAYMENT,
        }
        _, msg = event_service.record_event(
            user_id=user.id,
            event_type=ev_map[intent],
            worker_name=parsed.worker_name,
            date_str=parsed.date or "today",
            amount=parsed.amount or 0.0,
            notes=parsed.notes,
        )
        return msg

    elif intent == IntentType.GENERATE_PAYMENT:
        workers = worker_service.list_workers(user.id)
        if not workers:
            return "⚠️ You have no registered workers. Please add a worker first (e.g. *Add maid Sunita Salary 9000*)."

        target_worker = None
        if parsed.worker_name:
            target_worker = worker_service.get_worker(user.id, parsed.worker_name)

        if not target_worker:
            if len(workers) == 1:
                target_worker = workers[0]
            else:
                names = ", ".join([w.name for w in workers])
                return f"⚠️ Please specify which worker: {names} (e.g. *Generate payment for Sunita*)."

        today = date.today()
        events = event_repo.get_events_for_month(target_worker.id, today.year, today.month)
        summary = SalaryEngine.generate_summary(target_worker, events, today.year, today.month)

        # Update activation step
        if user.activation_step in [
            ActivationStep.STARTED_CHAT.value,
            ActivationStep.REGISTERED_FIRST_WORKER.value,
            ActivationStep.LOGGED_FIRST_EVENT.value,
        ]:
            user_repo.update_activation(user.id, ActivationStep.GENERATED_FIRST_PAYMENT, status=UserStatus.ACTIVE)
        elif user.activation_step == ActivationStep.GENERATED_FIRST_PAYMENT.value:
            user_repo.update_activation(user.id, ActivationStep.RETURNING_USER)

        analytics_repo.log(
            AnalyticsEventType.PAYMENT_GENERATED,
            user_id=user.id,
            metadata={"worker_id": target_worker.id, "net_payable": summary.net_payable},
        )

        return ReplyService.format_payment_summary(summary)

    elif intent == IntentType.HELP:
        return ReplyService.format_help()

    else:
        analytics_repo.log(AnalyticsEventType.UNKNOWN_INTENT, user_id=user.id)
        return (
            "❓ Sorry, I didn't quite catch that. You can record attendance, advances, bonuses, or generate salary summary.\n\n"
            "Reply *HELP* to see all supported commands."
        )
