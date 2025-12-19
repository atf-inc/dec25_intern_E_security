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


@app.get("/api/stats")
async def get_stats(time_range: str = Query("all", regex="^(24h|7d|30d|all)$")):
    """Get dashboard statistics with optional time-range filter."""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        alerts = _get_all_alerts()
        
        # Apply time filter
        if time_range != "all":
            now = datetime.utcnow()
            if time_range == "24h":
                cutoff = now - timedelta(hours=24)
            elif time_range == "7d":
                cutoff = now - timedelta(days=7)
            elif time_range == "30d":
                cutoff = now - timedelta(days=30)
            else:
                cutoff = None
            
            if cutoff:
                filtered_alerts = []
                for alert in alerts:
                    try:
                        ts = datetime.fromisoformat(alert.get("timestamp", "").replace("Z", "+00:00"))
                        ts_naive = ts.replace(tzinfo=None)
                        if ts_naive >= cutoff:
                            filtered_alerts.append(alert)
                    except (ValueError, TypeError):
                        filtered_alerts.append(alert)
                alerts = filtered_alerts
        
        total = len(alerts)
        
        if total == 0:
            return {
                "total_alerts": 0, "high_risk": 0, "medium_risk": 0, "low_risk": 0,
                "unique_users": 0, "avg_risk_score": 0.0,
                "top_domains": [], "top_users": [], "time_range": time_range
            }
        
        # Risk level counts (score is 0-100)
        high_risk = sum(1 for a in alerts if a.get("risk_score", 0) > 70)
        medium_risk = sum(1 for a in alerts if 40 <= a.get("risk_score", 0) <= 70)
        low_risk = sum(1 for a in alerts if a.get("risk_score", 0) < 40)
        
        # Unique users and average score
        users = set(a.get("user", "") for a in alerts if a.get("user"))
        scores = [a.get("risk_score", 0) for a in alerts]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Top domains by frequency
        domain_counts = {}
        for a in alerts:
            domain = a.get("domain", "unknown")
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Top users by max risk score
        user_max_risk = {}
        for a in alerts:
            user = a.get("user", "unknown")
            risk = a.get("risk_score", 0)
            if user not in user_max_risk or risk > user_max_risk[user]:
                user_max_risk[user] = risk
        top_users = sorted(user_max_risk.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_alerts": total,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "unique_users": len(users),
            "avg_risk_score": round(avg_score, 2),
            "top_domains": [{"domain": d, "count": c} for d, c in top_domains],
            "top_users": [{"user": u, "max_risk": r} for u, r in top_users],
            "time_range": time_range
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")


@app.get("/api/alerts/search")
async def search_alerts(
    q: Optional[str] = None,
    risk_level: Optional[str] = Query(None, regex="^(high|medium|low)$"),
    category: Optional[str] = None,
    user: Optional[str] = None,
    domain: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Search and filter alerts by various criteria."""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        alerts = _get_all_alerts()
        
        # Apply filters
        if q:
            q_lower = q.lower()
            alerts = [a for a in alerts if (
                q_lower in a.get("user", "").lower() or
                q_lower in a.get("domain", "").lower() or
                q_lower in a.get("category", "").lower() or
                q_lower in a.get("ai_message", "").lower()
            )]
        
        if risk_level:
            if risk_level == "high":
                alerts = [a for a in alerts if a.get("risk_score", 0) > 70]
            elif risk_level == "medium":
                alerts = [a for a in alerts if 40 <= a.get("risk_score", 0) <= 70]
            elif risk_level == "low":
                alerts = [a for a in alerts if a.get("risk_score", 0) < 40]
        
        if category:
            alerts = [a for a in alerts if a.get("category", "").lower() == category.lower()]
        
        if user:
            alerts = [a for a in alerts if user.lower() in a.get("user", "").lower()]
        
        if domain:
            alerts = [a for a in alerts if domain.lower() in a.get("domain", "").lower()]
        
        # Pagination
        total = len(alerts)
        paginated = alerts[offset:offset + limit]
        
        return {
            "alerts": paginated,
            "total": total,
            "count": len(paginated),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching alerts: {str(e)}")


@app.get("/api/alerts/{alert_id}")
async def get_alert_by_id(alert_id: str):
    """Get a single alert by ID for investigation."""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        alerts = _get_all_alerts()
        
        for alert in alerts:
            if alert.get("id") == alert_id:
                return alert
        
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alert: {str(e)}")


@app.patch("/api/alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: str, 
    status: str = Query(..., regex="^(new|investigating|resolved|dismissed)$")
):
    """Update the status of an alert."""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        # Get all alerts
        raw_alerts = redis_client.lrange("alerts", 0, -1)
        
        for i, alert_str in enumerate(raw_alerts):
            try:
                alert = json.loads(alert_str)
                if alert.get("id") == alert_id:
                    # Update status
                    alert["status"] = status
                    # Update in Redis (replace at same position)
                    redis_client.lset("alerts", i, json.dumps(alert))
                    return {"message": f"Alert status updated to '{status}'", "alert": alert}
            except json.JSONDecodeError:
                continue
        
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating alert: {str(e)}")



