# 📧 Email Parser API

A fast, lightweight **FastAPI-based** email parsing service that extracts structured JSON data from raw emails and `.eml` file uploads.

---

## ✨ Features

- 📨 **Header Extraction** — From, To, CC, BCC, Subject, Date, Message-ID, Reply-To
- 📅 **Smart Date Parsing** — Raw, ISO 8601, and Unix timestamp formats
- 📝 **Body Extraction** — Both plain text and HTML content
- 📎 **Attachment Detection** — Filename, content type, and file size
- 🔤 **Base64 Support** — Decode base64-encoded email content
- 📂 **File Upload** — Upload `.eml` files directly
- 🌐 **CORS Enabled** — Ready for cross-origin requests (RapidAPI compatible)
- 📖 **Interactive Docs** — Built-in Swagger UI and ReDoc
- 🐳 **Docker Ready** — Dockerfile and Docker Compose included

---

## 🛠️ Tech Stack

| Technology        | Version  | Purpose                    |
| ----------------- | -------- | -------------------------- |
| Python            | 3.11+    | Runtime                    |
| FastAPI           | 0.115.0  | Web framework              |
| Uvicorn           | 0.32.0   | ASGI server                |
| Pydantic          | 2.9.2    | Data validation            |
| python-multipart  | 0.0.9    | File upload support        |
| email-validator   | 2.2.0    | Email address validation   |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd email-parser-api
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
python main.py
```

Or with uvicorn directly (with hot reload):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at **http://localhost:8000**.

### 5. Access API Documentation

| Documentation | URL                            |
| ------------- | ------------------------------ |
| Swagger UI    | http://localhost:8000/docs     |
| ReDoc         | http://localhost:8000/redoc    |

---

## 🐳 Docker

### Build and Run with Docker

```bash
docker build -t email-parser-api .
docker run -p 8000:8000 email-parser-api
```

### Using Docker Compose

```bash
docker-compose up -d
```

This mounts a `./logs` directory and configures automatic restart.

---

## 📡 API Endpoints

### `GET /` — Health Check

Returns service info and available endpoints.

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "service": "Email Parser API",
  "status": "healthy",
  "version": "1.0.0",
  "endpoints": {
    "parse": "/parse (POST)",
    "docs": "/docs",
    "health": "/"
  }
}
```

---

### `GET /health` — Health Status

Lightweight health check for monitoring and load balancers.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### `POST /parse` — Parse Raw Email Content

Parse an email from raw RFC 822 content.

**Parameters (form-data):**

| Field           | Type    | Required | Description                                   |
| --------------- | ------- | -------- | --------------------------------------------- |
| `email_content` | string  | ✅ Yes   | Raw email content (RFC 822 format)             |
| `is_base64`     | boolean | ❌ No    | Set to `true` if content is base64 encoded     |

**Example:**

```bash
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: multipart/form-data" \
  -F 'email_content=From: sender@example.com
To: recipient@example.com
Subject: Test Email

This is the email body.'
```

---

### `POST /parse/file` — Parse Email File Upload

Parse an email by uploading a `.eml` file.

**Parameters (form-data):**

| Field  | Type | Required | Description                    |
| ------ | ---- | -------- | ------------------------------ |
| `file` | file | ✅ Yes   | Email file (`.eml` format)     |

**Example:**

```bash
curl -X POST "http://localhost:8000/parse/file" \
  -F "file=@test_email.eml"
```

---

## 📦 Response Format

All parsing endpoints return a consistent JSON response:

```json
{
  "success": true,
  "data": {
    "headers": {
      "from": "sender@example.com",
      "to": "recipient@example.com",
      "cc": "cc@example.com",
      "subject": "Test Email with Attachments",
      "date": {
        "raw": "Mon, 02 Mar 2026 11:20:00 +0530",
        "parsed": "2026-03-02T11:20:00+05:30",
        "unix_timestamp": 1740891000
      },
      "message-id": "<test123@example.com>"
    },
    "body": {
      "text": "This is a test email with both text and HTML content.",
      "html": "<html><body><h1>Test Email</h1><p>This is <b>HTML content</b>.</p></body></html>"
    },
    "attachments": [
      {
        "filename": "document.pdf",
        "content_type": "application/pdf",
        "size": 42
      }
    ],
    "is_multipart": true,
    "parts_count": 4
  },
  "message": "Email parsed successfully"
}
```

### Error Response

```json
{
  "success": false,
  "data": {},
  "message": "Error: Failed to parse email: <error details>"
}
```

---

## 🧪 Testing

### Using the Sample Email File

A test email file (`test_email.eml`) is included in the repository:

```bash
curl -X POST "http://localhost:8000/parse/file" \
  -F "file=@test_email.eml"
```

### Using Raw Email Content

```bash
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: multipart/form-data" \
  -F 'email_content=From: test@example.com
To: user@example.com
Subject: Hello World
Date: Mon, 02 Mar 2026 11:00:00 +0530

This is a test email body.'
```

### Using Base64-Encoded Content

```bash
# Encode your email content first
ENCODED=$(echo -n "From: test@example.com\nTo: user@example.com\nSubject: Test\n\nBody" | base64)

curl -X POST "http://localhost:8000/parse" \
  -F "email_content=$ENCODED" \
  -F "is_base64=true"
```

---

## 📁 Project Structure

```
email-parser-api/
├── main.py              # FastAPI application & email parsing logic
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image configuration
├── docker-compose.yml   # Docker Compose setup
├── test_email.eml       # Sample email file for testing
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

---

## 🌍 Deployment

### Deploy to Cloud Platforms

This API can be deployed to any platform that supports Python or Docker:

| Platform          | Docker Support | Free Tier |
| ----------------- | -------------- | --------- |
| Render.com        | ✅             | ✅        |
| Railway.app       | ✅             | ✅        |
| Fly.io            | ✅             | ✅        |
| DigitalOcean      | ✅             | ❌        |
| AWS (ECS/Lambda)  | ✅             | ❌        |

### Publish on RapidAPI

1. **Host your API** on one of the platforms above
2. **Create a [RapidAPI](https://rapidapi.com) account** and click "Add your API"
3. **Configure API settings:**
   - Name: `Email Parser API`
   - Category: `Data`
   - Base URL: Your deployed API URL
4. **Add endpoints:**
   - `POST /parse` — Parse raw email content
   - `POST /parse/file` — Parse email file upload
5. **Set pricing tiers:**

   | Plan              | Price     | Requests/Day |
   | ----------------- | --------- | ------------ |
   | Free              | $0/mo     | 100          |
   | Basic             | $10/mo    | 1,000        |
   | Pro               | $50/mo    | 10,000       |

---

## 📄 License

MIT License