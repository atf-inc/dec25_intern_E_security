"""Redis service for connection management."""
import redis
from typing import Optional
from config import settings


class RedisService:
    """Handles Redis connection management."""
    
    _instance: Optional['RedisService'] = None
    _client: Optional[redis.Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_client()
        return cls._instance
    
    def _initialize_client(self):
        """Initialize Redis client connection."""
        try:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        except Exception as e:
            print(f"Warning: Redis connection failed: {e}")
            self._client = None
    
    @property
    def client(self) -> Optional[redis.Redis]:
        """Get Redis client instance."""
        return self._client
    
    @property
    def is_available(self) -> bool:
        """Check if Redis client is available."""
        return self._client is not None
    
    def ping(self) -> bool:
        """Check Redis connectivity."""
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            return False


# Singleton instance for dependency injection
redis_service = RedisService()
