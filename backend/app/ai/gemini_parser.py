import re
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import httpx
from app.config import settings
from app.schemas.intent import ParsedIntent, IntentType

logger = logging.getLogger("homehelp.ai.parser")


SYSTEM_PROMPT = """
You are HomeHelp AI, an intent parser for domestic worker salary and attendance tracking.
Your single job is to convert user natural language messages into structured JSON conforming strictly to the requested schema.

Supported Intents:
- REGISTER_WORKER: Adding a new worker (e.g. "Add maid Sunita Salary 9000 Sunday off")
- REMOVE_WORKER: Deactivating/deleting a worker (e.g. "Remove Sunita", "Delete Ramesh")
- UPDATE_WORKER: Updating worker salary or settings (e.g. "Sunita salary is now 9500")
- ABSENT: Recording full day absence (e.g. "Sunita absent today", "Sunita absent yesterday")
- HALF_DAY: Recording half day work (e.g. "Sunita half day", "Cook half day today")
- PLANNED_LEAVE: Recording planned leave (e.g. "Sunita leave tomorrow", "Leave for Ramesh on Monday")
- ADVANCE: Recording advance money taken (e.g. "Sunita took 500 advance", "Gave 1000 advance to Ramesh")
- BONUS: Recording bonus money given (e.g. "Bonus 1000 for Sunita", "Diwali bonus 1500 Ramesh")
- PAYMENT: Recording partial or full payment made (e.g. "Paid Sunita 7500", "Gave 8000 to Sunita")
- GENERATE_PAYMENT: Asking for salary calculation or payment summary (e.g. "Generate payment", "Generate payment for Sunita")
- HELP: Greeting or help query (e.g. "Hi", "Help", "What can you do?")
- UNKNOWN: Anything else not clear or missing essential details.

Important Rules:
1. NEVER calculate salary or dates yourself. ONLY extract entities: worker_name, role, monthly_salary, weekly_off, working_days_per_month, amount, date, notes, clarification_needed.
2. date entity: default to "today" unless mentioned otherwise ("yesterday", "tomorrow", or "YYYY-MM-DD").
3. Return clean JSON matching ParsedIntent schema.
"""


class GeminiIntentParser:
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY

    def parse(self, text: str) -> ParsedIntent:
        text_clean = text.strip()
        if not text_clean:
            return ParsedIntent(intent=IntentType.UNKNOWN)

        # 1. Attempt Groq API call if key is present
        if self.groq_api_key and "mock" not in self.groq_api_key:
            try:
                parsed = self._call_groq_api(text_clean)
                if parsed:
                    return parsed
            except Exception as e:
                logger.warning(f"Groq API parsing failed ({e}). Falling back to Heuristics.")

        # 2. Fallback to rule-based heuristic parser
        return self._heuristic_parse(text_clean)

    def _call_groq_api(self, text: str) -> Optional[ParsedIntent]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }

        json_schema_prompt = (
            SYSTEM_PROMPT + "\n\n"
            "Respond ONLY with valid JSON matching this exact structure:\n"
            '{\n'
            '  "intent": "REGISTER_WORKER" | "REMOVE_WORKER" | "UPDATE_WORKER" | "ABSENT" | "HALF_DAY" | "PLANNED_LEAVE" | "ADVANCE" | "BONUS" | "PAYMENT" | "GENERATE_PAYMENT" | "HELP" | "UNKNOWN",\n'
            '  "worker_name": string or null,\n'
            '  "role": string or null,\n'
            '  "monthly_salary": number or null,\n'
            '  "weekly_off": string or null,\n'
            '  "working_days_per_month": number or 26,\n'
            '  "amount": number or null,\n'
            '  "date": "today" or "yesterday" or "tomorrow" or "YYYY-MM-DD",\n'
            '  "notes": string or null,\n'
            '  "clarification_needed": string or null\n'
            '}'
        )

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": json_schema_prompt},
                {"role": "user", "content": text},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    raw_text = res.json()["choices"][0]["message"]["content"]
                    json_obj = json.loads(raw_text)
                    logger.info("Successfully parsed intent using Groq LLaMA 3.3 70B.")
                    return ParsedIntent(**json_obj)
                else:
                    logger.warning(f"Groq API returned status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Groq API execution failed: {e}")

        return None

    def _call_gemini_api(self, text: str) -> Optional[ParsedIntent]:
        models = ["gemini-2.0-flash", "gemini-1.5-flash"]
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": SYSTEM_PROMPT},
                            {"text": f"User Input: {text}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "OBJECT",
                        "properties": {
                            "intent": {
                                "type": "STRING",
                                "enum": [e.value for e in IntentType]
                            },
                            "worker_name": {"type": "STRING"},
                            "role": {"type": "STRING"},
                            "monthly_salary": {"type": "NUMBER"},
                            "weekly_off": {"type": "STRING"},
                            "working_days_per_month": {"type": "INTEGER"},
                            "amount": {"type": "NUMBER"},
                            "date": {"type": "STRING"},
                            "notes": {"type": "STRING"},
                            "clarification_needed": {"type": "STRING"}
                        },
                        "required": ["intent"]
                    }
                }
            }

            try:
                with httpx.Client(timeout=10.0) as client:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        json_obj = json.loads(raw_text)
                        return ParsedIntent(**json_obj)
                    elif res.status_code == 404:
                        logger.warning(f"Gemini model {model} returned 404. Trying fallback model...")
                        continue
                    else:
                        logger.error(f"Gemini API Error ({res.status_code}): {res.text}")
            except Exception as e:
                logger.error(f"Gemini call error on model {model}: {e}")

        return None

    def _heuristic_parse(self, text: str) -> ParsedIntent:
        lower = text.lower()

        # Help / Greeting
        greeting_words = ["hi", "hii", "hiii", "hey", "heyy", "hello", "help", "start", "menu", "namaste", "options"]
        if lower in greeting_words or any(g in lower.split() for g in greeting_words):
            return ParsedIntent(intent=IntentType.HELP)

        # Generate Payment
        if "generate payment" in lower or "calculate salary" in lower or "salary summary" in lower:
            worker_match = re.search(r"for\s+([a-zA-Z]+)", lower)
            worker_name = worker_match.group(1).title() if worker_match else None
            return ParsedIntent(
                intent=IntentType.GENERATE_PAYMENT,
                worker_name=worker_name
            )

        # Register Worker (e.g., "Add maid Sunita Salary 9000 Sunday off")
        if re.search(r"\b(add|register|create)\b", lower):
            salary_match = re.search(r"(?:salary|sal|rs\.?|₹|\$)?\s*(\d{3,7})", lower)
            salary = float(salary_match.group(1)) if salary_match else None

            role_match = re.search(r"\b(maid|cook|driver|nanny|gardener|cleaner|worker|helper)\b", lower)
            role = role_match.group(1).title() if role_match else "Domestic Worker"

            # Name extraction
            words = text.split()
            name = None
            for idx, w in enumerate(words):
                if w.lower() in ["add", "register", "create", "maid", "cook", "driver", "nanny", "gardener", "cleaner"]:
                    continue
                if w.isdigit():
                    continue
                if w.lower() in ["salary", "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "off"]:
                    continue
                name = w.title()
                break

            weekly_off = "Sunday"
            off_match = re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+off\b", lower)
            if off_match:
                weekly_off = off_match.group(1).title()

            if name and salary:
                return ParsedIntent(
                    intent=IntentType.REGISTER_WORKER,
                    worker_name=name,
                    role=role,
                    monthly_salary=salary,
                    weekly_off=weekly_off,
                    working_days_per_month=26
                )
            elif name and not salary:
                return ParsedIntent(
                    intent=IntentType.REGISTER_WORKER,
                    worker_name=name,
                    role=role,
                    clarification_needed=f"Please specify monthly salary for {name}."
                )

        # Remove Worker (e.g. "Remove Sunita")
        if re.search(r"\b(remove|delete|fire)\b", lower):
            match = re.search(r"(?:remove|delete|fire)\s+(?:worker|maid|cook)?\s*([a-zA-Z]+)", lower)
            name = match.group(1).title() if match else None
            return ParsedIntent(
                intent=IntentType.REMOVE_WORKER,
                worker_name=name
            )

        # Update Salary (e.g. "Sunita salary is now 9500")
        if "salary" in lower and ("now" in lower or "update" in lower or "change" in lower or "is" in lower):
            salary_match = re.search(r"(\d{3,7})", lower)
            name_match = re.search(r"([a-zA-Z]+)\s+salary", lower)
            if salary_match and name_match:
                return ParsedIntent(
                    intent=IntentType.UPDATE_WORKER,
                    worker_name=name_match.group(1).title(),
                    monthly_salary=float(salary_match.group(1))
                )

        # Date helper
        event_date = "today"
        if "yesterday" in lower:
            event_date = "yesterday"
        elif "tomorrow" in lower:
            event_date = "tomorrow"

        def extract_name(text_str: str, exclude_words: List[str]) -> Optional[str]:
            words = re.findall(r"[a-zA-Z]+", text_str)
            for w in words:
                if w.lower() not in exclude_words:
                    return w.title()
            return None

        # Advance (e.g. "Sunita took 500 advance")
        if "advance" in lower:
            amount_match = re.search(r"(\d+)", lower)
            amount = float(amount_match.group(1)) if amount_match else None
            name = extract_name(text, ["advance", "took", "gave", "given", "rs", "rupees", "today", "yesterday", "tomorrow"])
            return ParsedIntent(
                intent=IntentType.ADVANCE,
                worker_name=name,
                amount=amount,
                date=event_date
            )

        # Bonus (e.g. "Bonus 1000 for Sunita")
        if "bonus" in lower:
            amount_match = re.search(r"(\d+)", lower)
            amount = float(amount_match.group(1)) if amount_match else None
            name = extract_name(text, ["bonus", "for", "to", "gave", "given", "rs", "rupees", "today", "yesterday", "tomorrow"])
            return ParsedIntent(
                intent=IntentType.BONUS,
                worker_name=name,
                amount=amount,
                date=event_date
            )

        # Payment (e.g. "Paid Sunita 7500")
        if "paid" in lower or "payment" in lower:
            amount_match = re.search(r"(\d+)", lower)
            amount = float(amount_match.group(1)) if amount_match else None
            name = extract_name(text, ["paid", "payment", "to", "for", "gave", "given", "rs", "rupees", "today", "yesterday", "tomorrow"])
            return ParsedIntent(
                intent=IntentType.PAYMENT,
                worker_name=name,
                amount=amount,
                date=event_date
            )

        # Half Day (e.g. "Sunita half day")
        if "half day" in lower or "halfday" in lower:
            name = extract_name(text, ["half", "day", "halfday", "today", "yesterday", "tomorrow"])
            return ParsedIntent(
                intent=IntentType.HALF_DAY,
                worker_name=name,
                date=event_date
            )

        # Planned Leave (e.g. "Sunita leave tomorrow")
        if "leave" in lower or "planned leave" in lower:
            name = extract_name(text, ["leave", "planned", "on", "today", "yesterday", "tomorrow"])
            return ParsedIntent(
                intent=IntentType.PLANNED_LEAVE,
                worker_name=name,
                date=event_date
            )

        # Absent (e.g. "Sunita absent today")
        if "absent" in lower or "chutti" in lower or "no show" in lower:
            name = extract_name(text, ["absent", "chutti", "no", "show", "today", "yesterday", "tomorrow"])
            return ParsedIntent(
                intent=IntentType.ABSENT,
                worker_name=name,
                date=event_date
            )

        return ParsedIntent(intent=IntentType.UNKNOWN)
