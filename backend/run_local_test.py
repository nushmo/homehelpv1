import json
import time
from fastapi.testclient import TestClient
from main import app
from app.database.client import db_store

client = TestClient(app)

def simulate_chat(text: str, phone: str = "919503642976"):
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

    print(f"\n📲 USER MSG ──> \"{text}\"")
    res = client.post("/webhook", json=payload)
    assert res.status_code == 200

if __name__ == "__main__":
    db_store.clear()
    print("=" * 60)
    print("🚀 RUNNING LOCAL HOMEHELP AI WEBHOOK SIMULATION")
    print("=" * 60)

    # 1. Greeting
    simulate_chat("Hi")

    # 2. Register worker
    simulate_chat("Add maid Sunita Salary 9000 Sunday off")

    # 3. Record attendance exception
    simulate_chat("Sunita absent today")

    # 4. Record advance
    simulate_chat("Sunita took 500 advance")

    # 5. Generate Payment Summary
    simulate_chat("Generate payment for Sunita")

    # 6. Fetch Analytics
    print("\n" + "=" * 60)
    print("📊 LOCAL ANALYTICS OVERVIEW:")
    res_overview = client.get("/analytics/overview")
    print(json.dumps(res_overview.json(), indent=2))

    print("\n📈 LOCAL PRODUCT ADOPTION FUNNEL:")
    res_funnel = client.get("/analytics/funnel")
    print(json.dumps(res_funnel.json(), indent=2))
    print("=" * 60)
