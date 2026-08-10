import httpx

RAILWAY_URL = "https://homehelpv1-production.up.railway.app"

print("=" * 60)
print(f"🔍 TESTING LIVE RAILWAY BACKEND ENDPOINTS: {RAILWAY_URL}")
print("=" * 60)

# 1. Test GET /health
print("\n1. Testing GET /health ...")
try:
    res = httpx.get(f"{RAILWAY_URL}/health", timeout=10.0)
    print(f"HTTP Status: {res.status_code}")
    print(f"Body: {res.json()}")
except Exception as e:
    print(f"❌ /health check failed: {e}")

# 2. Test GET /webhook (Meta verification challenge)
print("\n2. Testing GET /webhook (Meta Challenge Verification) ...")
try:
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "homehelp_secret_verify_token_99",
        "hub.challenge": "123456789"
    }
    res = httpx.get(f"{RAILWAY_URL}/webhook", params=params, timeout=10.0)
    print(f"HTTP Status: {res.status_code}")
    print(f"Body: {res.text}")
    if res.status_code == 200 and res.text == "123456789":
        print("✅ Meta Webhook Verification challenge logic is 100% SUCCESSFUL!")
    else:
        print(f"⚠️ Unexpected challenge response: {res.text}")
except Exception as e:
    print(f"❌ /webhook verification check failed: {e}")

# 3. Test POST /webhook (Simulate Meta incoming message)
print("\n3. Testing POST /webhook (Simulate WhatsApp message from 919503642976) ...")
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
                        "contacts": [{"profile": {"name": "Vikas Live Test"}, "wa_id": "919503642976"}],
                        "messages": [
                            {
                                "from": "919503642976",
                                "id": "wmid-test-123",
                                "timestamp": "1700000000",
                                "text": {"body": "Sunita absent today"},
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

try:
    res = httpx.post(f"{RAILWAY_URL}/webhook", json=payload, timeout=15.0)
    print(f"HTTP Status: {res.status_code}")
    print(f"Body: {res.json()}")
except Exception as e:
    print(f"❌ POST /webhook test failed: {e}")

print("=" * 60)
