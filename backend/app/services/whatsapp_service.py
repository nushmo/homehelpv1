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

    def send_text_message(self, recipient_phone: str, message_text: str) -> bool:
        clean_phone = recipient_phone.replace("+", "").replace(" ", "").replace("-", "")

        token = self.token
        phone_id = self.phone_number_id

        if not token or "mock" in token or not phone_id or "mock" in phone_id:
            logger.info(
                f"[MOCK WHATSAPP SEND] To: {clean_phone}\nMessage:\n{message_text}\n"
            )
            return True

        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
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
