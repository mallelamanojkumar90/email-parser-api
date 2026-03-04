"""
Email Parser API
Parse emails and extract structured data as JSON.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import email
import base64

app = FastAPI(
    title="Email Parser API",
    description="Parse emails and extract structured data including headers, body, and attachments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for RapidAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class ParseResponse(BaseModel):
    success: bool
    data: dict
    message: str


class EmailRequest(BaseModel):
    email_content: str
    is_base64: bool = False


def parse_email_content(email_content: str, is_base64: bool = False) -> dict:
    """
    Parse email content and extract structured data.
    """
    try:
        # Decode if base64
        if is_base64:
            email_content = base64.b64decode(email_content).decode('utf-8', errors='ignore')

        # Parse the email
        msg = email.message_from_string(email_content)

        # Extract headers
        headers = {}
        for key in ['from', 'to', 'cc', 'bcc', 'subject', 'date', 'message-id', 'reply-to']:
            value = msg.get(key)
            if value:
                headers[key] = value

        # Parse date if available
        if 'date' in headers:
            try:
                parsed_date = email.utils.parsedate_to_datetime(headers['date'])
                headers['date'] = {
                    'raw': headers['date'],
                    'parsed': parsed_date.isoformat(),
                    'unix_timestamp': int(parsed_date.timestamp())
                }
            except:
                pass

        # Extract body (text and HTML)
        body = {'text': None, 'html': None}

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body['text'] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        body['html'] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                try:
                    body['text'] = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
            elif content_type == "text/html":
                try:
                    body['html'] = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass

        # Extract attachments
        attachments = []
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    attachments.append({
                        'filename': filename,
                        'content_type': part.get_content_type(),
                        'size': len(part.get_payload(decode=True)) if part.get_payload() else 0
                    })

        return {
            'headers': headers,
            'body': body,
            'attachments': attachments,
            'is_multipart': msg.is_multipart(),
            'parts_count': len(list(msg.walk())) if msg.is_multipart() else 1
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse email: {str(e)}")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "Email Parser API",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "parse": "/parse (POST)",
            "docs": "/docs",
            "health": "/"
        }
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


@app.post("/parse", response_model=ParseResponse, tags=["Email Parsing"])
async def parse_email(request: EmailRequest):
    """
    Parse an email and return structured JSON data.

    Accepts JSON containing raw email content (RFC 822 format) and extracts:
    - Headers (from, to, subject, date, etc.)
    - Body (both text and HTML)
    - Attachments (list of files with metadata)
    """
    try:
        parsed_data = parse_email_content(request.email_content, request.is_base64)
        return ParseResponse(
            success=True,
            data=parsed_data,
            message="Email parsed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return ParseResponse(
            success=False,
            data={},
            message=f"Error: {str(e)}"
        )


@app.post("/parse/file", response_model=ParseResponse, tags=["Email Parsing"])
async def parse_email_file(
    file: UploadFile = File(..., description="Upload email file (.eml, .msg)")
):
    """
    Parse an email file upload.

    Supports .eml and other text-based email formats.
    """
    try:
        content = await file.read()
        email_content = content.decode('utf-8', errors='ignore')
        parsed_data = parse_email_content(email_content, is_base64=False)
        return ParseResponse(
            success=True,
            data=parsed_data,
            message="Email file parsed successfully"
        )
    except Exception as e:
        return ParseResponse(
            success=False,
            data={},
            message=f"Error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)