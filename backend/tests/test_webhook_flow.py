from fastapi.testclient import TestClient
from main import app
from app.database.client import db_store

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_full_whatsapp_chat_lifecycle():
    db_store.clear()
    phone = "919999999999"

    def make_payload(text: str):
        return {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry-1",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {"phone_number_id": "phone-123"},
                                "contacts": [{"profile": {"name": "Test User"}, "wa_id": phone}],
                                "messages": [
                                    {
                                        "from": phone,
                                        "id": "wmid-123",
                                        "timestamp": "1700000000",
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

    # 1. Start Chat with greeting
    r1 = client.post("/webhook", json=make_payload("Hi"))
    assert r1.status_code == 200

    # 2. Register worker Sunita
    r2 = client.post("/webhook", json=make_payload("Add maid Sunita Salary 9000 Sunday off"))
    assert r2.status_code == 200

    # 3. Record attendance exception (Absent)
    r3 = client.post("/webhook", json=make_payload("Sunita absent today"))
    assert r3.status_code == 200

    # 4. Record Advance
    r4 = client.post("/webhook", json=make_payload("Sunita took 500 advance"))
    assert r4.status_code == 200

    # 5. Generate Payment Summary
    r5 = client.post("/webhook", json=make_payload("Generate payment for Sunita"))
    assert r5.status_code == 200

    # 6. Verify analytics metrics
    r_funnel = client.get("/analytics/funnel")
    assert r_funnel.status_code == 200
    data_funnel = r_funnel.json()
    assert data_funnel["total_households"] >= 1

    r_overview = client.get("/analytics/overview")
    assert r_overview.status_code == 200
    data_overview = r_overview.json()
    assert data_overview["total_workers"] == 1
    assert data_overview["total_salary_events_logged"] >= 2
    assert data_overview["total_payment_summaries_generated"] >= 1
