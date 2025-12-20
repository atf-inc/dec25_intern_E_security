"""Analytics routes for chart data and visualizations."""
from fastapi import APIRouter, HTTPException, Query
from services.redis_service import redis_service
from services.analytics_service import analytics_service

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics")
async def get_analytics(time_range: str = Query("7d", regex="^(24h|7d|30d|all)$")):
    """Get analytics data for charts and visualizations."""
    if not redis_service.is_available:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        alerts = redis_service.get_all_alerts()
        return analytics_service.get_analytics(alerts, time_range)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")
