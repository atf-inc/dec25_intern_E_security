"""Stats routes for dashboard statistics."""
from fastapi import APIRouter, HTTPException, Query
from services.redis_service import redis_service
from services.stats_service import stats_service

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
async def get_stats(time_range: str = Query("all", regex="^(24h|7d|30d|all)$")):
    """Get dashboard statistics with optional time-range filter."""
    if not redis_service.is_available:
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    try:
        alerts = redis_service.get_all_alerts()
        return stats_service.get_stats(alerts, time_range)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")
