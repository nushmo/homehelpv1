import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def send_simulated_whatsapp_message(text: str, phone: str = "919503642976"):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "entry-1",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "1288347221022677"},
                            "contacts": [{"profile": {"name": "Vikas Test"}, "wa_id": phone}],
                            "messages": [
                                {
                                    "from": phone,
                                    "id": f"wmid-{int(time.time())}",
                                    "timestamp": str(int(time.time())),
                                    "text": {"body": text},
                                    "type": "text",
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    print(f"\n==================================================")
    print(f"📱 USER SENDS: \"{text}\"")
    print(f"==================================================")

    try:
        res = httpx.post(f"{BASE_URL}/webhook", json=payload, timeout=10.0)
        print(f"HTTP Status: {res.status_code}")
        print(f"Response Body: {res.json()}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Make sure local uvicorn server is running: uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    print("🚀 Running Local HomeHelp AI Webhook Simulations...\n")
    
    # 1. Greeting / Help
    send_simulated_whatsapp_message("Hi")
    time.sleep(1)

    # 2. Register worker
    send_simulated_whatsapp_message("Add maid Sunita Salary 9000 Sunday off")
    time.sleep(1)

    # 3. Record attendance exception
    send_simulated_whatsapp_message("Sunita absent today")
    time.sleep(1)

    # 4. Record Advance
    send_simulated_whatsapp_message("Sunita took 500 advance")
    time.sleep(1)

    # 5. Generate Payment
    send_simulated_whatsapp_message("Generate payment for Sunita")
    time.sleep(1)

    # 6. Check Analytics Overview
    try:
        res = httpx.get(f"{BASE_URL}/analytics/overview")
        print("\n==================================================")
        print("📊 ANALYTICS OVERVIEW:")
        print(json.dumps(res.json(), indent=2))
        print("==================================================")
    except Exception:
        pass
