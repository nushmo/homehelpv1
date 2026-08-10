import httpx

RAILWAY_URL = "https://homehelpv1-production.up.railway.app/webhook"

# Real Meta Webhook Payload sent when user texts 'Hi'
payload = {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "2577466126057451",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15556641680",
              "phone_number_id": "1288347221022677"
            },
            "contacts": [
              {
                "profile": {
                  "name": "vicks"
                },
                "wa_id": "919503642976",
                "user_id": "IN.2213661742806900",
                "country_code": "IN"
              }
            ],
            "messages": [
              {
                "from": "919503642976",
                "from_user_id": "IN.2213661742806900",
                "id": "wamid.HBgMOTE9NTAzNjQyOTc2FQIAEhggQUNDM0ZDMDMxQkU1ODU5MThCMjVFMjg2MkEzN0FDNUQA",
                "timestamp": "1786284750",
                "text": {
                  "body": "Hi"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

print("=" * 60)
print(f"🚀 POSTING EXACT META PAYLOAD FOR 'Hi' TO LIVE RAILWAY: {RAILWAY_URL}")
print("=" * 60)

try:
    res = httpx.post(RAILWAY_URL, json=payload, timeout=15.0)
    print(f"HTTP Status Code: {res.status_code}")
    print(f"Response Body: {res.json()}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("=" * 60)
