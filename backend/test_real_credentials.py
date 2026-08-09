import sys
import os
import httpx
from dotenv import load_dotenv

# Load local .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

print("=" * 60)
print("🔍 TESTING REAL CREDENTIALS FROM YOUR LOCAL .env FILE")
print("=" * 60)

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_KEY", "")
groq_key = os.getenv("GROQ_API_KEY", "")
gemini_key = os.getenv("GEMINI_API_KEY", "")
whatsapp_token = os.getenv("WHATSAPP_TOKEN", "")
whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
verify_token = os.getenv("VERIFY_TOKEN", "")

print(f"1. SUPABASE_URL:          {supabase_url}")
print(f"2. SUPABASE_KEY:          {supabase_key[:10]}..." if supabase_key else "Missing")
print(f"3. GROQ_API_KEY:          {groq_key[:10]}..." if groq_key else "Missing")
print(f"4. GEMINI_API_KEY:        {gemini_key[:10]}..." if gemini_key else "Missing")
print(f"5. WHATSAPP_TOKEN:        {whatsapp_token[:10]}..." if whatsapp_token else "Missing")
print(f"6. WHATSAPP_PHONE_ID:     {whatsapp_phone_id}")
print(f"7. VERIFY_TOKEN:          {verify_token}\n")

# ----------------------------------------------------
# TEST 1: TEST SUPABASE CONNECTION
# ----------------------------------------------------
print("--- [TEST 1/3] Testing Supabase Connection ---")
if "mock" in supabase_url or not supabase_url:
    print("⚠️ SUPABASE_URL is mock or missing in .env. Skipping live Supabase check.")
else:
    try:
        url = f"{supabase_url}/rest/v1/users?select=count"
        headers = {"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}
        res = httpx.get(url, headers=headers, timeout=5.0)
        if res.status_code == 200:
            print("✅ Supabase REST Connection Successful!")
        else:
            print(f"❌ Supabase Error ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")

# ----------------------------------------------------
# TEST 2A: TEST GROQ API INTENT PARSING
# ----------------------------------------------------
print("\n--- [TEST 2A] Testing Groq API (LLaMA 3.3 70B) ---")
if "mock" in groq_key or not groq_key:
    print("⚠️ GROQ_API_KEY is mock or missing in .env. Skipping live Groq check.")
else:
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "Return JSON: {\"status\": \"ok\", \"parsed\": \"Add maid Sunita\"}"}],
            "response_format": {"type": "json_object"},
        }
        res = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        if res.status_code == 200:
            print("✅ Groq API Connection Successful (Using model llama-3.3-70b-versatile)!")
            print(f"Groq Response: {res.json()['choices'][0]['message']['content']}")
        else:
            print(f"❌ Groq API Error ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ Groq connection failed: {e}")
# ----------------------------------------------------
# TEST 3: TEST META WHATSAPP CLOUD API SENDING
# ----------------------------------------------------
print("\n--- [TEST 3/3] Testing Meta WhatsApp Cloud API Outgoing Message ---")
if "mock" in whatsapp_token or not whatsapp_token or "mock" in whatsapp_phone_id or not whatsapp_phone_id:
    print("⚠️ WHATSAPP_TOKEN or WHATSAPP_PHONE_NUMBER_ID is mock/missing in .env. Skipping live WhatsApp send check.")
else:
    test_recipient = "919503642976"  # User's phone number
    url = f"https://graph.facebook.com/v18.0/{whatsapp_phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": test_recipient,
        "type": "text",
        "text": {"preview_url": False, "body": "👋 Live Test Message from HomeHelp AI Local Test Script!"},
    }

    try:
        res = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        if res.status_code == 200:
            print(f"🎉 SUCCESS! Meta WhatsApp API sent live message to +{test_recipient}!")
            print(f"Meta Response: {res.json()}")
        else:
            print(f"❌ Meta WhatsApp API Error ({res.status_code}):")
            print(res.text)
    except Exception as e:
        print(f"❌ Meta WhatsApp API Connection Failed: {e}")

print("=" * 60)
