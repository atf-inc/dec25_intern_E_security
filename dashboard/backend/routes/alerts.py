"""Alert routes for CRUD operations."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.redis_service import redis_service
from services.alerts_service import alerts_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
async def get_alerts(limit: int = 50, offset: int = 0):
    """Fetch paginated alerts from Redis."""
    if not redis_service.is_available:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        alerts = redis_service.get_alerts_paginated(limit, offset)
        return {
            "alerts": alerts,
            "count": len(alerts),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")


@router.get("/search")
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
    if not redis_service.is_available:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        all_alerts = redis_service.get_all_alerts()
        result = alerts_service.search_alerts(
            alerts=all_alerts,
            q=q,
            risk_level=risk_level,
            category=category,
            user=user,
            domain=domain,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching alerts: {str(e)}")


@router.get("/{alert_id}")
async def get_alert_by_id(alert_id: str):
    """Get a single alert by ID for investigation."""
    if not redis_service.is_available:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        alert = redis_service.get_alert_by_id(alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return alert
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alert: {str(e)}")


@router.patch("/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status: str = Query(..., regex="^(new|investigating|resolved|dismissed)$")
):
    """Update the status of an alert."""
    if not redis_service.is_available:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        updated_alert = redis_service.update_alert(alert_id, {"status": status})
        if updated_alert is None:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return {"message": f"Alert status updated to '{status}'", "alert": updated_alert}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating alert: {str(e)}")


@router.post("/reset")
async def reset_alerts():
    """
    Clear all alerts from Redis to start fresh simulations.
    This is called automatically when starting a new simulation.
    """
    if not redis_service.is_available:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        deleted_count = redis_service.clear_all_alerts()
        return {
            "message": "All alerts cleared successfully",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing alerts: {str(e)}")
