from fastapi import APIRouter, Query
from typing import Annotated
from datetime import datetime

from collector.schemas.log import Log
from collector.services.redis_service import RedisService

router = APIRouter()
redis_service = RedisService()

@router.post("/logs")
def collect_log(log: Log):
    """
    Ingest logs via POST request.
    """
    redis_service.publish("events", log.dict())
    return {"status": "received", "method": "POST"}

@router.get("/logs")
def collect_log_get(
    user_id: str,
    domain: str,
    url: str,
    method: str,
    upload_size_bytes: int,
    ts: Annotated[datetime | None, Query()] = None
):
    """
    Ingest logs via GET request (e.g. from proxy).
    """
    if ts is None:
        ts = datetime.utcnow()
    
    log = Log(
        ts=ts,
        user_id=user_id,
        domain=domain,
        url=url,
        method=method,
        upload_size_bytes=upload_size_bytes
    )
    
    redis_service.publish("events", log.dict())
    return {"status": "received", "method": "GET"}
