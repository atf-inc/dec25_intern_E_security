from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
import redis
import json
from config import settings

app = FastAPI(title="ShadowGuard Dashboard API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis Client Setup
# We use a global client for simplicity in this MVP. 
# In production, consider dependency injection.
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )
    # Quick connectivity check (optional, can remove if it blocks startup)
    # redis_client.ping() 
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    redis_client = None

@app.get("/")
async def root():
    return {"message": "ShadowGuard Dashboard API is running"}

@app.get("/api/health")
async def health_check():
    if not redis_client:
        return {"status": "degraded", "redis": "not initialized"}
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": str(e)}

@app.get("/api/alerts")
async def get_alerts(limit: int = 50, offset: int = 0):
    """
    Fetch alerts from the 'alerts' Redis list.
    Returns the most recent alerts (assuming LPUSH was used).
    """
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        # Get raw strings from Redis list
        # lrange is inclusive for start and stop
        raw_alerts = redis_client.lrange("alerts", offset, offset + limit - 1)
        
        # Parse JSON
        alerts = []
        for alert_str in raw_alerts:
            try:
                alerts.append(json.loads(alert_str))
            except json.JSONDecodeError:
                alerts.append({"raw_content": alert_str, "error": "Invalid JSON"})
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")


# Helper function to get all alerts from Redis
def _get_all_alerts() -> List[dict]:
    """Fetch all alerts from Redis and parse them."""
    if not redis_client:
        return []
    try:
        raw_alerts = redis_client.lrange("alerts", 0, -1)
        alerts = []
        for alert_str in raw_alerts:
            try:
                alerts.append(json.loads(alert_str))
            except json.JSONDecodeError:
                continue
        return alerts
    except Exception:
        return []
