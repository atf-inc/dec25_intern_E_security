from fastapi import FastAPI, Query
from collector.schemas.log import Log
from collector.services.redis_service import RedisService
from typing import Annotated
from datetime import datetime

app = FastAPI(title="Log Collector Service")
redis_service = RedisService()

@app.post("/logs")
async def collect_log(log: Log):
    """
    Ingest logs via POST request.
    """
    redis_service.publish("events", log.dict())
    return {"status": "received", "method": "POST"}

@app.get("/logs")
async def collect_log_get(
    user_id: str,
    device_id: str,
    event: str,
    source: str,
    timestamp: Annotated[datetime | None, Query()] = None
):
    """
    Ingest logs via GET request (e.g. from proxy).
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    log = Log(
        user_id=user_id,
        device_id=device_id,
        event=event,
        source=source,
        timestamp=timestamp
    )
    
    redis_service.publish("events", log.dict())
    return {"status": "received", "method": "GET"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
