"""Health check routes."""
from fastapi import APIRouter
from services.redis_service import redis_service

router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ShadowGuard Dashboard API is running"}


@router.get("/api/health")
async def health_check():
    """Health check endpoint with Redis status."""
    if not redis_service.is_available:
        return {"status": "degraded", "redis": "not initialized"}
    
    if redis_service.ping():
        return {"status": "healthy", "redis": "connected"}
    else:
        return {"status": "unhealthy", "redis": "ping failed"}
