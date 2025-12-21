"""Alerts service for search and filtering operations."""
from typing import List, Optional


class AlertsService:
    """Handles alert search and filtering logic."""
    
    @staticmethod
    def filter_by_query(alerts: List[dict], query: str) -> List[dict]:
        """Filter alerts by text query across multiple fields."""
        q_lower = query.lower()
        return [
            a for a in alerts
            if (
                q_lower in a.get("user", "").lower() or
                q_lower in a.get("domain", "").lower() or
                q_lower in a.get("category", "").lower() or
                q_lower in a.get("ai_message", "").lower()
            )
        ]
    
    @staticmethod
    def filter_by_risk_level(alerts: List[dict], risk_level: str) -> List[dict]:
        """Filter alerts by risk level (high, medium, low)."""
        if risk_level == "high":
            return [a for a in alerts if a.get("risk_score", 0) > 70]
        elif risk_level == "medium":
            return [a for a in alerts if 40 <= a.get("risk_score", 0) <= 70]
        elif risk_level == "low":
            return [a for a in alerts if a.get("risk_score", 0) < 40]
        return alerts
    
    @staticmethod
    def filter_by_category(alerts: List[dict], category: str) -> List[dict]:
        """Filter alerts by category."""
        return [a for a in alerts if a.get("category", "").lower() == category.lower()]
    
    @staticmethod
    def filter_by_user(alerts: List[dict], user: str) -> List[dict]:
        """Filter alerts by user (partial match)."""
        return [a for a in alerts if user.lower() in a.get("user", "").lower()]
    
    @staticmethod
    def filter_by_domain(alerts: List[dict], domain: str) -> List[dict]:
        """Filter alerts by domain (partial match)."""
        return [a for a in alerts if domain.lower() in a.get("domain", "").lower()]
    
    def search_alerts(
        self,
        alerts: List[dict],
        q: Optional[str] = None,
        risk_level: Optional[str] = None,
        category: Optional[str] = None,
        user: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """Search and filter alerts with pagination."""
        filtered = alerts
        
        if q:
            filtered = self.filter_by_query(filtered, q)
        
        if risk_level:
            filtered = self.filter_by_risk_level(filtered, risk_level)
        
        if category:
            filtered = self.filter_by_category(filtered, category)
        
        if user:
            filtered = self.filter_by_user(filtered, user)
        
        if domain:
            filtered = self.filter_by_domain(filtered, domain)
        
        # Pagination
        total = len(filtered)
        paginated = filtered[offset:offset + limit]
        
        return {
            "alerts": paginated,
            "total": total,
            "count": len(paginated),
            "limit": limit,
            "offset": offset
        }


# Singleton instance
alerts_service = AlertsService()
