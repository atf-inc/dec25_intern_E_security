"""Redis service for connection and alert data operations."""
import redis
import json
from typing import List, Optional
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
    
    def get_alerts_paginated(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """Fetch paginated alerts from Redis list."""
        if not self._client:
            return []
        
        try:
            raw_alerts = self._client.lrange("alerts", offset, offset + limit - 1)
            alerts = []
            for alert_str in raw_alerts:
                try:
                    alerts.append(json.loads(alert_str))
                except json.JSONDecodeError:
                    alerts.append({"raw_content": alert_str, "error": "Invalid JSON"})
            return alerts
        except Exception:
            return []
    
    def get_all_alerts(self) -> List[dict]:
        """Fetch all alerts from Redis and parse them."""
        if not self._client:
            return []
        
        try:
            raw_alerts = self._client.lrange("alerts", 0, -1)
            alerts = []
            for alert_str in raw_alerts:
                try:
                    alerts.append(json.loads(alert_str))
                except json.JSONDecodeError:
                    continue
            return alerts
        except Exception:
            return []
    
    def get_alert_by_id(self, alert_id: str) -> Optional[dict]:
        """Get a single alert by ID."""
        alerts = self.get_all_alerts()
        for alert in alerts:
            if alert.get("id") == alert_id:
                return alert
        return None
    
    def update_alert(self, alert_id: str, updates: dict) -> Optional[dict]:
        """Update an alert by ID."""
        if not self._client:
            return None
        
        try:
            raw_alerts = self._client.lrange("alerts", 0, -1)
            for i, alert_str in enumerate(raw_alerts):
                try:
                    alert = json.loads(alert_str)
                    if alert.get("id") == alert_id:
                        alert.update(updates)
                        self._client.lset("alerts", i, json.dumps(alert))
                        return alert
                except json.JSONDecodeError:
                    continue
            return None
        except Exception:
            return None


# Singleton instance for dependency injection
redis_service = RedisService()
