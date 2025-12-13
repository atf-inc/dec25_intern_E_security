# Collector Service

The Collector service is the data ingestion layer of ShadowGuard AI. It receives network traffic logs and events via a FastAPI-based REST API, validates incoming data, and pushes it to Redis for downstream processing.

**Files:**
- `main.py` - FastAPI application entry point and API endpoints
- `models.py` - Pydantic models for request/response validation

**Dependencies:**
- FastAPI
- Redis(Port: 6379)

**Environment Variables:**
- REDIS_HOST: Redis host (default: localhost)
- REDIS_PORT: Redis port (default: 6379)

**Usage:**
- Run the application using `uvicorn main:app --host 0.0.0.0 --port 8000`
- The API endpoint is `POST /collect`

**Example Request:**
```json
{
    "source": "source_ip",
    "event": "event_type",
    "timestamp": "timestamp"
}
```
