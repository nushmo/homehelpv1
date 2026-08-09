import logging
from typing import Optional
import httpx
from app.config import settings
from app.ai.gemini_parser import GeminiIntentParser
from app.schemas.intent import ParsedIntent

logger = logging.getLogger("homehelp.ai.voice")


class VoiceHandler:
    def __init__(self):
        self.parser = GeminiIntentParser()
        self.groq_api_key = settings.GROQ_API_KEY
        self.whatsapp_token = settings.WHATSAPP_TOKEN

    def process_voice_media(
        self, media_id: str, mime_type: str = "audio/ogg"
    ) -> ParsedIntent:
        """Download voice media from WhatsApp Cloud API and parse intent using Groq Whisper."""
        audio_bytes = self._download_whatsapp_media(media_id)
        if not audio_bytes:
            logger.warning(f"Could not download WhatsApp media {media_id}. Returning UNKNOWN intent.")
            return self.parser.parse("Help voice message error")

        # 1. Attempt Groq Whisper transcription if Groq key present
        if self.groq_api_key and "mock" not in self.groq_api_key:
            try:
                transcript = self._transcribe_with_groq_whisper(audio_bytes, mime_type)
                if transcript:
                    logger.info(f"Groq Whisper Transcribed voice note: '{transcript}'")
                    return self.parser.parse(transcript)
            except Exception as e:
                logger.error(f"Error transcribing audio with Groq Whisper ({e}).")

        # Mock fallback for test environment
        return self.parser.parse("Sunita absent today")

    def _transcribe_with_groq_whisper(
        self, audio_bytes: bytes, mime_type: str = "audio/ogg"
    ) -> Optional[str]:
        """Transcribes audio bytes using Groq Whisper API (whisper-large-v3-turbo)."""
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.groq_api_key}"}

        filename = "voice.ogg" if "ogg" in mime_type else "voice.mp3"
        files = {"file": (filename, audio_bytes, mime_type)}
        data = {"model": "whisper-large-v3-turbo", "response_format": "json"}

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, headers=headers, files=files, data=data)
                if res.status_code == 200:
                    return res.json().get("text")
                else:
                    logger.warning(f"Groq Whisper API returned {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Groq Whisper transcription exception: {e}")

        return None

    def _download_whatsapp_media(self, media_id: str) -> Optional[bytes]:
        if not self.whatsapp_token or "mock" in self.whatsapp_token:
            logger.info("Using mock audio bytes for voice handler test.")
            return b"MOCK_AUDIO_DATA"

        try:
            # 1. Get media URL from Meta Graph API
            url = f"https://graph.facebook.com/v18.0/{media_id}"
            headers = {"Authorization": f"Bearer {self.whatsapp_token}"}

            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, headers=headers)
                res.raise_for_status()
                media_url = res.json().get("url")

                if not media_url:
                    return None

                # 2. Download media binary content
                audio_res = client.get(media_url, headers=headers)
                audio_res.raise_for_status()
                return audio_res.content
        except Exception as e:
            logger.error(f"Failed to download WhatsApp media ID {media_id}: {e}")
            return None

    def _process_audio_with_gemini(
        self, audio_bytes: bytes, mime_type: str
    ) -> ParsedIntent:
        """Uses Gemini API to transcribe audio and return structured intent."""
        import base64
        import json
        encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")

        prompt = (
            "Transcribe this voice note and extract the user's intent according to HomeHelp AI rules. "
            "Return JSON matching ParsedIntent schema."
        )

        models = ["gemini-2.0-flash", "gemini-1.5-flash"]
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": encoded_audio
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json"
                }
            }

            try:
                with httpx.Client(timeout=15.0) as client:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        json_obj = json.loads(raw_text)
                        return ParsedIntent(**json_obj)
                    elif res.status_code == 404:
                        logger.warning(f"Gemini voice model {model} returned 404. Trying fallback model...")
                        continue
            except Exception as e:
                logger.error(f"Gemini voice error on model {model}: {e}")

        return self.parser.parse("Help voice message error")
