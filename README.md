# HomeHelp AI (V1)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg?style=flat&logo=supabase&logoColor=white)](https://supabase.com)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5-4285F4.svg?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![WhatsApp](https://img.shields.io/badge/Messaging-WhatsApp%20Cloud%20API-25D366.svg?style=flat&logo=whatsapp&logoColor=white)](https://developers.facebook.com/docs/whatsapp/cloud-api)

**HomeHelp AI** is a WhatsApp-first AI assistant designed for urban homeowners to track domestic worker attendance, record salary-impacting exceptions (absences, half days, planned leave, advances, bonuses), and generate forwarding-ready salary payment summaries without requiring any mobile app or complex software.

---

## 📌 Product Philosophy

- **Zero-friction tracking**: Urban homeowners track domestic worker salaries across memory, notes, paper diaries, and WhatsApp chats. At month-end, reconstructing exceptions causes stress and disputes.
- **Record Exceptions ONLY**: HomeHelp AI assumes every scheduled working day = **PRESENT**. Users only record exceptions (`ABSENT`, `HALF_DAY`, `PLANNED_LEAVE`, `ADVANCE`, `BONUS`, `PAYMENT`).
- **Deterministic Calculation Engine**: Gemini is strictly used for intent extraction from natural language or voice notes. Gemini **NEVER** calculates salary or writes directly to the database. All financial computations are 100% deterministic Python code.
- **WhatsApp Native**: No app download, no employee login, no calendar UI. Clean, text-only summaries formatted for instant WhatsApp forwarding to workers.

---

## 🏗️ Architecture

```
WhatsApp User (Text / Voice Note)
             │
             ▼
Meta WhatsApp Cloud API Webhook
             │
             ▼
FastAPI Webhook Controller (/webhook)
             │
  ┌──────────┴──────────┐
  ▼                     ▼
Text Message       Voice Note Media
  │                     │
  └──────────┬──────────┘
             ▼
   Gemini 2.5 Flash Parser
   (Structured JSON Output)
             │
             ▼
   Business Logic Layer
   (Worker / Event Services)
             │
             ▼
    Supabase PostgreSQL
    (Users, Workers, Events)
             │
             ▼
 Deterministic Salary Engine
             │
             ▼
  WhatsApp Reply Formatter
             │
             ▼
  Meta WhatsApp Cloud API (Response)
```

---

## 📂 Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   └── controllers/       # Webhook, Workers, Events, Payment, Analytics endpoints
│   ├── ai/                    # Gemini intent parser & Multimodal voice handler
│   ├── config/                # Pydantic settings and environment config
│   ├── database/              # Supabase client & SQL migration schema
│   ├── models/                # Pydantic domain models (User, Worker, Event, Analytics)
│   ├── repositories/          # Data access layer with Supabase / In-Memory fallback
│   ├── salary/                # 100% Deterministic salary engine & calculations
│   ├── schemas/               # Structured Pydantic intent schemas
│   ├── services/              # Business logic (Worker, Event, Reply, WhatsApp, Analytics)
│   └── utils/                 # Logging & helper utilities
├── tests/                     # Pytest suite (Salary engine, Intent parser, Webhook, CRUD)
├── Dockerfile                 # Production Docker container image
├── railway.json               # Railway cloud deployment configuration
├── main.py                    # FastAPI application entrypoint
├── requirements.txt           # Python package dependencies
└── .env.example               # Environment variables template
```

---

## 🚀 Quick Start & Local Development

### 1. Prerequisites
- Python 3.10+
- `git`
- (Optional) `ngrok` for testing live WhatsApp webhooks locally

### 2. Clone & Setup Virtual Environment
```bash
git clone https://github.com/your-username/HomeHelpAI.git
cd HomeHelpAI/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and populate your credentials:
```bash
cp .env.example .env
```

```ini
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
GEMINI_API_KEY=your-gemini-api-key
WHATSAPP_TOKEN=your-whatsapp-access-token
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-phone-number-id
VERIFY_TOKEN=homehelp-verify-token
PORT=8000
ENVIRONMENT=development
```

### 4. Database Setup (Supabase)
1. Open your Supabase Dashboard project.
2. Go to **SQL Editor** -> **New Query**.
3. Copy and paste the contents of `backend/app/database/schema.sql`.
4. Click **Run** to create tables (`users`, `workers`, `events`, `analytics_events`), indexes, and constraints.

### 5. Run Local Server
```bash
uvicorn main:app --reload --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 6. Run Test Suite
```bash
pytest -v
```

---

## 💬 WhatsApp Commands & Voice Examples

| Action | WhatsApp Command Example |
| :--- | :--- |
| **Register Worker** | `Add maid Sunita Salary 9000 Sunday off` |
| **Remove Worker** | `Remove Sunita` |
| **Update Salary** | `Sunita salary is now 9500` |
| **Record Absent** | `Sunita absent today` |
| **Record Half Day** | `Sunita half day` |
| **Record Leave** | `Sunita leave tomorrow` |
| **Record Advance** | `Sunita took 500 advance` |
| **Record Bonus** | `Bonus 1000 for Sunita` |
| **Record Payment** | `Paid Sunita 7500` |
| **Generate Payment**| `Generate payment for Sunita` |
| **Help / Menu** | `Hi` / `Help` |
| **Voice Note** | Send a voice note saying any of the commands above! 🎙️ |

---

## 📊 Payment Summary Output Example

When a user requests `"Generate payment for Sunita"`, HomeHelp AI returns:

```text
📋 *SALARY PAYMENT SUMMARY*
━━━━━━━━━━━━━━━━━━
🗓️ *Month:* August 2026
👤 *Worker:* Sunita (Domestic Worker)
💰 *Monthly Salary:* ₹9,000.00
📅 *Working Days:* 26 days
🧮 *Daily Rate:* ₹346.15/day

❌ *Absent Days:* 1
🌗 *Half Days:* 1
🏖️ *Planned Leave:* 0

📉 *Deduction:* ₹519.22
💸 *Advance Paid:* ₹500.00
🎁 *Bonus:* ₹1,000.00
💵 *Already Paid:* ₹0.00
━━━━━━━━━━━━━━━━━━
✅ *NET PAYABLE:* ₹8,980.78
📌 *Status:* PENDING

📝 *Recent Events:*
• 2026-08-05: Absent (-₹346.15)
• 2026-08-10: Half Day (-₹173.07)
• 2026-08-15: Advance ₹500.00
• 2026-08-20: Bonus +₹1000.00

_Generated by HomeHelp AI Assistant_
```

---

## 📈 REST & Analytics API Reference

### Health & Webhooks
- `GET /health`: Server health check.
- `GET /webhook`: Meta WhatsApp Cloud API verification challenge handler.
- `POST /webhook`: WhatsApp Cloud API webhook receiver (Text & Voice Notes).

### Workers API
- `GET /workers?user_id={id}`: List all active workers for a homeowner.
- `POST /workers`: Register a new worker.
- `PUT /workers/{id}`: Update worker salary or properties.
- `DELETE /workers/{id}?user_id={id}`: Deactivate a worker.

### Events & Payments API
- `POST /events`: Manually log an attendance or money event.
- `POST /generate-payment`: Generate structured salary summary JSON and formatted text.

### Product Analytics API
- `GET /analytics/overview`: Operational metrics (total households, workers, event counts, voice vs text ratio).
- `GET /analytics/funnel`: Product adoption lifecycle funnel metrics (`STARTED_CHAT` ➔ `REGISTERED_FIRST_WORKER` ➔ `LOGGED_FIRST_EVENT` ➔ `GENERATED_FIRST_PAYMENT` ➔ `RETURNING_USER`).

---

## 🚂 Production Deployment (Railway & Meta Cloud API)

1. **Deploy to Railway**:
   - Link your GitHub repository to Railway.
   - Select `Dockerfile` mode or automatic detection.
   - Set environment variables (`SUPABASE_URL`, `SUPABASE_KEY`, `GEMINI_API_KEY`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `VERIFY_TOKEN`).
2. **Configure WhatsApp Cloud API Webhook**:
   - In Meta Developer Portal -> WhatsApp -> Configuration -> Webhook:
   - Set Callback URL: `https://your-railway-url.up.railway.app/webhook`
   - Set Verify Token: matching your `VERIFY_TOKEN` env var.
   - Subscribe to `messages`.

---

## 🗺️ Roadmap & Future Enhancements
- Multi-language support (Hindi, Marathi, Kannada, Tamil, Telugu).
- Scheduled WhatsApp reminders on month-end for salary generation.
- Automated UPI payment links / QR code inclusion in payment summaries.
