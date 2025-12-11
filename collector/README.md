# Collector Service

The Collector service is the data ingestion layer of ShadowGuard AI. It receives network traffic logs and events via a FastAPI-based REST API, validates incoming data, and pushes it to Redis for downstream processing.

**Files:**
- `main.py` - FastAPI application entry point and API endpoints
- `models.py` - Pydantic models for request/response validation
