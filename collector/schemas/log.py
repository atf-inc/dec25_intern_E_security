from pydantic import BaseModel, Field
from datetime import datetime

class Log(BaseModel):
    ts: datetime = Field(..., example="2025-12-09T14:30:00Z")
    user_id: str = Field(..., example="alice@company.com")
    domain: str = Field(..., example="chat.super-unknown-ai.io")
    url: str = Field(..., example="/api/v1/upload_context")
    method: str = Field(..., example="POST")
    upload_size_bytes: int = Field(..., example=5242880)