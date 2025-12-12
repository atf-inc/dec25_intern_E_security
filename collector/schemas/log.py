from pydantic import BaseModel, Field
from datetime import datetime

class Log(BaseModel):
    user_id: str = Field(..., example="U123")
    device_id: str = Field(..., example="LAPTOP-001")
    event: str = Field(..., example="Opened Zoom")
    source: str = Field(..., example="windows_agent")
    timestamp: datetime = Field(default_factory=datetime.utcnow, example="2025-12-11T10:00:00Z")