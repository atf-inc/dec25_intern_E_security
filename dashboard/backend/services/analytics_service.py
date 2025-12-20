"""Analytics service for chart data and visualizations."""
from datetime import datetime, timedelta
from typing import List
from services.stats_service import StatsService


class AnalyticsService:
    """Handles analytics data generation for charts and visualizations."""
    
    def __init__(self):
        self.stats_service = StatsService()
    
    def get_risk_trend(self, alerts: List[dict], time_range: str) -> List[dict]:
        """Calculate risk trend over time."""
        risk_trend = {}
        
        for alert in alerts:
            try:
                ts = datetime.fromisoformat(alert.get("timestamp", "").replace("Z", "+00:00"))
                # Group by hour for 24h, by day for other ranges
                if time_range == "24h":
                    key = ts.strftime("%Y-%m-%d %H:00")
                else:
                    key = ts.strftime("%Y-%m-%d")
                
                if key not in risk_trend:
                    risk_trend[key] = {"timestamp": key, "count": 0, "total_risk": 0}
                risk_trend[key]["count"] += 1
                risk_trend[key]["total_risk"] += alert.get("risk_score", 0)
            except (ValueError, TypeError):
                continue
        
        # Calculate average risk per period
        trend_data = []
        for key in sorted(risk_trend.keys()):
            entry = risk_trend[key]
            entry["avg_risk"] = round(entry["total_risk"] / entry["count"], 2) if entry["count"] > 0 else 0
            del entry["total_risk"]
            trend_data.append(entry)
        
        return trend_data
    
    def get_top_users_analytics(self, alerts: List[dict], limit: int = 10) -> List[dict]:
        """Get top risky users with detailed analytics."""
        user_stats = {}
        
        for alert in alerts:
            user = alert.get("user", "unknown")
            if user not in user_stats:
                user_stats[user] = {
                    "user": user,
                    "alert_count": 0,
                    "max_risk": 0,
                    "total_risk": 0
                }
            user_stats[user]["alert_count"] += 1
            user_stats[user]["max_risk"] = max(user_stats[user]["max_risk"], alert.get("risk_score", 0))
            user_stats[user]["total_risk"] += alert.get("risk_score", 0)
        
        for user in user_stats.values():
            user["avg_risk"] = round(user["total_risk"] / user["alert_count"], 2) if user["alert_count"] > 0 else 0
            del user["total_risk"]
        
        return sorted(user_stats.values(), key=lambda x: x["max_risk"], reverse=True)[:limit]
    
    def get_top_domains_analytics(self, alerts: List[dict], limit: int = 10) -> List[dict]:
        """Get top risky domains with detailed analytics."""
        domain_stats = {}
        
        for alert in alerts:
            domain = alert.get("domain", "unknown")
            if domain not in domain_stats:
                domain_stats[domain] = {
                    "domain": domain,
                    "alert_count": 0,
                    "max_risk": 0
                }
            domain_stats[domain]["alert_count"] += 1
            domain_stats[domain]["max_risk"] = max(domain_stats[domain]["max_risk"], alert.get("risk_score", 0))
        
        return sorted(domain_stats.values(), key=lambda x: x["alert_count"], reverse=True)[:limit]
    
    def get_category_breakdown(self, alerts: List[dict]) -> List[dict]:
        """Get alert count by category."""
        category_counts = {}
        
        for alert in alerts:
            category = alert.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        categories = [{"category": k, "count": v} for k, v in category_counts.items()]
        return sorted(categories, key=lambda x: x["count"], reverse=True)
    
    def get_analytics(self, alerts: List[dict], time_range: str = "7d") -> dict:
        """Get complete analytics data for visualizations."""
        # Apply time filter using stats service
        filtered_alerts = self.stats_service.filter_by_time_range(alerts, time_range)
        
        return {
            "risk_trend": self.get_risk_trend(filtered_alerts, time_range),
            "top_users": self.get_top_users_analytics(filtered_alerts),
            "top_domains": self.get_top_domains_analytics(filtered_alerts),
            "categories": self.get_category_breakdown(filtered_alerts),
            "time_range": time_range,
            "total_alerts": len(filtered_alerts)
        }


# Singleton instance
analytics_service = AnalyticsService()
