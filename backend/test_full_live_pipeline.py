import os
import sys
import logging
from dotenv import load_dotenv

# Load local .env
load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("homehelp.live_test")

from app.repositories.user_repo import UserRepository
from app.repositories.worker_repo import WorkerRepository
from app.repositories.event_repo import EventRepository
from app.repositories.analytics_repo import AnalyticsRepository
from app.ai.gemini_parser import GeminiIntentParser
from app.services.worker_service import WorkerService
from app.services.event_service import EventService
from app.services.whatsapp_service import WhatsAppService
from app.api.controllers.webhook import route_intent_to_business_logic

def run_live_pipeline_test():
    print("=" * 60)
    print("🚀 STEP-BY-STEP LIVE PIPELINE DIAGNOSTIC (GENERATE PAYMENT)")
    print("=" * 60)

    phone = "919503642976"
    test_message = "Generate payment for Sunita"

    user_repo = UserRepository()
    worker_repo = WorkerRepository()
    whatsapp_service = WhatsAppService()
    parser = GeminiIntentParser()

    print(f"\n1. Fetching user for phone: {phone}...")
    user = user_repo.get_by_phone(phone)
    if not user:
        user = user_repo.create(phone, display_name="Vikas Live Test")
        print(f"✅ User created in DB: {user.id}")
    else:
        print(f"✅ Existing User found in DB: {user.id} (step: {user.activation_step})")

    print(f"\n2. Parsing Intent for message: '{test_message}'...")
    parsed = parser.parse(test_message)
    print(f"✅ Parsed Intent: {parsed.intent} (Worker: {parsed.worker_name})")

    print(f"\n3. Routing Intent to Business Logic...")
    reply_text = route_intent_to_business_logic(user, parsed)
    print(f"✅ Generated Reply Text:\n{reply_text}")

    print(f"\n4. Sending Outgoing WhatsApp Message via Meta API to {phone}...")
    success = whatsapp_service.send_text_message(phone, reply_text)
    if success:
        print(f"🎉 SUCCESS! Payment Summary delivered to WhatsApp!")
    else:
        print(f"❌ Meta API failed to send WhatsApp message.")

    print("=" * 60)

if __name__ == "__main__":
    run_live_pipeline_test()
