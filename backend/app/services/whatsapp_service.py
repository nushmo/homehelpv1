import logging
from typing import Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger("homehelp.service.whatsapp")


class WhatsAppService:
    @property
    def token(self) -> str:
        return settings.WHATSAPP_TOKEN

    @property
    def phone_number_id(self) -> str:
        return settings.WHATSAPP_PHONE_NUMBER_ID

    def send_text_message(
        self, recipient_phone: str, message_text: str, phone_id: Optional[str] = None
    ) -> bool:
        clean_phone = recipient_phone.replace("+", "").replace(" ", "").replace("-", "")

        token = self.token
        target_phone_id = phone_id or self.phone_number_id

        print(f"📡 [WHATSAPP SEND ATTEMPT] PhoneID={target_phone_id}, Recipient={clean_phone}, TokenPrefix={token[:10] if token else 'None'}", flush=True)

        if not token or "mock" in token or not target_phone_id or "mock" in target_phone_id:
            print(f"⚠️ [MOCK WHATSAPP SEND ENABLED] WHATSAPP_TOKEN or WHATSAPP_PHONE_NUMBER_ID contains 'mock' in environment variables! To: {clean_phone}", flush=True)
            logger.info(
                f"[MOCK WHATSAPP SEND] To: {clean_phone}\nMessage:\n{message_text}\n"
            )
            return True

        url = f"https://graph.facebook.com/v18.0/{target_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {"preview_url": False, "body": message_text},
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code >= 400:
                    logger.error(
                        f"Meta API Error ({res.status_code}) sending to {clean_phone}: {res.text}"
                    )
                    return False
                logger.info(f"Successfully sent WhatsApp message to {clean_phone}")
                return True
        except Exception as e:
            logger.error(f"Exception sending WhatsApp message to {clean_phone}: {e}")
            return False
