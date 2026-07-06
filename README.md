# QuensultingAI Dental Clinic — AI Receptionist Backend

Production-ready FastAPI backend for an AI Receptionist Voice Agent integrated with **RetellAI Conversational Flow**. Handles appointment booking webhooks, validates patient data, persists records to **Google Sheets**, and sends confirmation emails via **Gmail SMTP**.

---

## Project Overview

This service acts as the backend layer between a RetellAI voice agent and clinic operations. When a caller books an appointment through the voice agent, RetellAI sends a webhook POST request to this API. The backend:

1. Validates all input fields (phone, email, date, time, service)
2. Enforces clinic business rules (MonΓÇôSat, 9 AMΓÇô6 PM, no Sundays)
3. Saves the appointment to Google Sheets
4. Sends a confirmation email to the patient
5. Returns a structured JSON response to RetellAI

**Clinic:** QuensultingAI Dental Clinic  
**Hours:** Monday ΓÇô Saturday, 9:00 AM ΓÇô 6:00 PM

### Services Offered

- Dental Cleaning
- Root Canal Treatment
- Teeth Whitening
- Braces Consultation
- Tooth Extraction
- General Dental Consultation

---

## Architecture

```
RetellAI Voice Agent
        Γöé
        Γû╝  POST /book-appointment (webhook)
ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ
Γöé           FastAPI Application          Γöé
Γöé  ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ  ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ Γöé
Γöé  Γöé Middleware  Γöé  Γöé Exception       Γöé Γöé
Γöé  Γöé Request ID  Γöé  Γöé Handlers        Γöé Γöé
Γöé  Γöé Response    Γöé  ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ Γöé
Γöé  Γöé Time        Γöé                       Γöé
Γöé  ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ                       Γöé
Γöé        Γöé                               Γöé
Γöé  ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓû╝ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ   Γöé
Γöé  Γöé     Appointment Route           Γöé   Γöé
Γöé  ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓö¼ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ   Γöé
Γöé        Γöé                               Γöé
Γöé  ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓû╝ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ   Γöé
Γöé  Γöé   Appointment Service           Γöé   Γöé
Γöé  Γöé   (orchestration layer)         Γöé   Γöé
Γöé  ΓööΓöÇΓöÇΓö¼ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓö¼ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ   Γöé
Γöé     Γöé              Γöé                   Γöé
Γöé  ΓöîΓöÇΓöÇΓû╝ΓöÇΓöÇΓöÇΓöÉ    ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓû╝ΓöÇΓöÇΓöÇΓöÇΓöÉ   ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ Γöé
Γöé  ΓöéValid-Γöé    Γöé Google   Γöé   Γöé Email  Γöé Γöé
Γöé  Γöéators Γöé    Γöé Sheets   Γöé   Γöé SMTP   Γöé Γöé
Γöé  ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ    ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ   ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ Γöé
ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ
        Γöé              Γöé
        Γû╝              Γû╝
  Google Sheets    Gmail SMTP
```

### Design Principles

- **Clean Architecture** ΓÇö Routes ΓåÆ Services ΓåÆ External integrations
- **Dependency Injection** ΓÇö FastAPI `Depends()` for settings and services
- **Separation of Concerns** ΓÇö Validation, persistence, and email are isolated
- **Structured Logging** ΓÇö Request ID correlation across all log entries
- **Fail-Safe Error Handling** ΓÇö Typed exceptions with appropriate HTTP status codes

---

## Folder Structure

```
dental-ai-agent/
Γö£ΓöÇΓöÇ app/
Γöé   Γö£ΓöÇΓöÇ __init__.py
Γöé   Γö£ΓöÇΓöÇ main.py                  # FastAPI app, middleware, exception handlers
Γöé   Γö£ΓöÇΓöÇ config.py                # Environment-based settings (Pydantic)
Γöé   Γö£ΓöÇΓöÇ models/
Γöé   Γöé   ΓööΓöÇΓöÇ appointment.py       # Request/response Pydantic models
Γöé   Γö£ΓöÇΓöÇ routes/
Γöé   Γöé   Γö£ΓöÇΓöÇ appointment.py       # POST /book-appointment
Γöé   Γöé   ΓööΓöÇΓöÇ health.py            # GET /api/health
Γöé   Γö£ΓöÇΓöÇ services/
Γöé   Γöé   Γö£ΓöÇΓöÇ appointment_service.py
Γöé   Γöé   Γö£ΓöÇΓöÇ google_sheet_service.py
Γöé   Γöé   ΓööΓöÇΓöÇ email_service.py
Γöé   ΓööΓöÇΓöÇ utils/
Γöé       Γö£ΓöÇΓöÇ validators.py        # Business rule validation
Γöé       ΓööΓöÇΓöÇ logger.py            # Logging configuration
Γö£ΓöÇΓöÇ tests/
Γöé   Γö£ΓöÇΓöÇ test_validators.py
Γöé   ΓööΓöÇΓöÇ test_api.py
Γö£ΓöÇΓöÇ requirements.txt
Γö£ΓöÇΓöÇ Dockerfile
Γö£ΓöÇΓöÇ .env.example
Γö£ΓöÇΓöÇ .gitignore
Γö£ΓöÇΓöÇ pytest.ini
ΓööΓöÇΓöÇ README.md
```

---

## Installation

### Prerequisites

- Python 3.11+
- Google Cloud service account with Sheets API enabled
- Gmail account with App Password enabled

### Local Setup

```bash
# Clone the repository
git clone <repository-url>
cd dental-ai-agent

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see below)
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in all values:

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_NAME` | Application display name | `QuensultingAI Dental Clinic API` |
| `APP_VERSION` | API version | `1.0.0` |
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | Server bind host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CLINIC_NAME` | Clinic name for emails | `QuensultingAI Dental Clinic` |
| `GOOGLE_CREDENTIALS_PATH` | Path to service account JSON | `credentials.json` |
| `GOOGLE_SHEET_ID` | Google Spreadsheet ID | `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms` |
| `GOOGLE_SHEET_NAME` | Worksheet tab name | `Appointments` |
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USERNAME` | Gmail address | `your@gmail.com` |
| `SMTP_PASSWORD` | Gmail App Password | `xxxx xxxx xxxx xxxx` |
| `SMTP_FROM_EMAIL` | Sender email address | `your@gmail.com` |
| `SMTP_USE_TLS` | Enable TLS | `true` |

> **Never commit `.env` or `credentials.json` to version control.**

---

## Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Google Sheets API**
4. Create a **Service Account** under IAM & Admin ΓåÆ Service Accounts
5. Download the JSON key file and save it as `credentials.json` in the project root
6. Create a new Google Spreadsheet
7. Copy the Spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit
   ```
8. Share the spreadsheet with the service account email (found in `credentials.json` under `client_email`) with **Editor** access
9. Set `GOOGLE_SHEET_ID` and `GOOGLE_CREDENTIALS_PATH` in your `.env`

The API automatically creates these column headers on first write:

| Appointment ID | Timestamp | Name | Phone | Email | Treatment | Appointment Date | Appointment Time |

---

## SMTP Setup (Gmail)

1. Enable **2-Factor Authentication** on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an App Password for "Mail"
4. Set `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM_EMAIL` in `.env`

---

## Run Server

### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
# Build image
docker build -t dental-ai-agent .

# Run container (mount credentials and env)
docker run -d \
  --name dental-ai-agent \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  dental-ai-agent
```

**Windows (PowerShell):**

```powershell
docker build -t dental-ai-agent .
docker run -d --name dental-ai-agent -p 8000:8000 --env-file .env -v ${PWD}/credentials.json:/app/credentials.json:ro dental-ai-agent
```

---

## API Documentation

Interactive Swagger UI is available at:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### Endpoints

#### `GET /api/health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "service": "QuensultingAI Dental Clinic API",
  "version": "1.0.0",
  "timestamp": "2026-07-06T05:21:00.000000+00:00"
}
```

#### `POST /book-appointment`

Book a new appointment. Supports both direct API field names and RetellAI aliases.

**Request:**

```json
{
  "name": "Harsh Maniya",
  "phone": "9876543210",
  "email": "harsh@gmail.com",
  "service": "Dental Cleaning",
  "date": "2026-07-10",
  "time": "11:00 AM"
}
```

**RetellAI aliases (also accepted):**

| RetellAI Field | API Field |
|----------------|-----------|
| `customer_name` | `name` |
| `treatment` | `service` |
| `appointment_date` | `date` |
| `appointment_time` | `time` |

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Appointment booked successfully.",
  "appointment_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-07-06T05:21:00.123456Z"
}
```

**Error Response:**

```json
{
  "status": "error",
  "message": "Invalid phone number. Phone must be exactly 10 digits."
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Appointment booked successfully |
| `400` | Business validation failed |
| `422` | Request payload validation failed |
| `502` | Email delivery failed (appointment saved) |
| `503` | Google Sheets API failed |
| `500` | Unexpected server error |

### Validation Rules

| Field | Rule |
|-------|------|
| Phone | Exactly 10 digits |
| Email | Valid email format |
| Date | `YYYY-MM-DD`, not in the past, not Sunday |
| Time | Between 9:00 AM and 6:00 PM |
| Service | Must match one of the clinic services |

### Response Headers

Every response includes:

- `X-Request-ID` ΓÇö Unique correlation ID for tracing
- `X-Response-Time-Ms` ΓÇö Server processing time in milliseconds

---

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run validator tests only
pytest tests/test_validators.py -v
```

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Book appointment
curl -X POST http://localhost:8000/book-appointment \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Harsh Maniya",
    "phone": "9876543210",
    "email": "harsh@gmail.com",
    "service": "Dental Cleaning",
    "date": "2026-07-10",
    "time": "11:00 AM"
  }'
```

---

## Logging

All requests are logged with structured output:

```
2026-07-06 10:30:00 | INFO     | dental_ai_agent.main | request_id=abc-123 | Request Started | method=POST path=/book-appointment
2026-07-06 10:30:00 | INFO     | dental_ai_agent.appointment.abc-123 | request_id=- | Appointment Received | name=Harsh Maniya service=Dental Cleaning
2026-07-06 10:30:00 | INFO     | dental_ai_agent.appointment.abc-123 | request_id=- | Validation Passed | phone=9876543210 email=harsh@gmail.com
2026-07-06 10:30:01 | INFO     | dental_ai_agent.google_sheets | request_id=- | Google Sheet Updated | appointment_id=...
2026-07-06 10:30:02 | INFO     | dental_ai_agent.email | request_id=- | Email Sent | appointment_id=...
2026-07-06 10:30:02 | INFO     | dental_ai_agent.main | request_id=abc-123 | Request Completed | status=200 duration_ms=2100.45
```

---

## RetellAI Integration

Configure your RetellAI Conversational Flow webhook to POST to:

```
https://your-domain.com/book-appointment
```

Map RetellAI collected variables to the request body fields. The API accepts both naming conventions (`name` / `customer_name`, etc.).

---

## License

This project was built as an internship assignment for QuensultingAI Dental Clinic.
