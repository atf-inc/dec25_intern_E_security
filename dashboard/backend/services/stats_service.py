"""Stats service for dashboard statistics calculations."""
from datetime import datetime, timedelta
from typing import List, Optional


class StatsService:
    """Handles statistics calculation for alerts."""
    
    @staticmethod
    def filter_by_time_range(alerts: List[dict], time_range: str) -> List[dict]:
        """Filter alerts by time range."""
        if time_range == "all":
            return alerts
        
        now = datetime.utcnow()
        if time_range == "24h":
            cutoff = now - timedelta(hours=24)
        elif time_range == "7d":
            cutoff = now - timedelta(days=7)
        elif time_range == "30d":
            cutoff = now - timedelta(days=30)
        else:
            return alerts
        
        filtered_alerts = []
        for alert in alerts:
            try:
                ts = datetime.fromisoformat(alert.get("timestamp", "").replace("Z", "+00:00"))
                ts_naive = ts.replace(tzinfo=None)
                if ts_naive >= cutoff:
                    filtered_alerts.append(alert)
            except (ValueError, TypeError):
                # Include alerts with invalid timestamps
                filtered_alerts.append(alert)
        
        return filtered_alerts
    
    @staticmethod
    def calculate_risk_counts(alerts: List[dict]) -> dict:
        """Calculate risk level counts (high, medium, low)."""
        high_risk = sum(1 for a in alerts if a.get("risk_score", 0) > 70)
        medium_risk = sum(1 for a in alerts if 40 <= a.get("risk_score", 0) <= 70)
        low_risk = sum(1 for a in alerts if a.get("risk_score", 0) < 40)
        
        return {
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk
        }
    
    @staticmethod
    def calculate_user_stats(alerts: List[dict]) -> dict:
        """Calculate unique users and top users by max risk."""
        users = set(a.get("user", "") for a in alerts if a.get("user"))
        
        user_max_risk = {}
        for a in alerts:
            user = a.get("user", "unknown")
            risk = a.get("risk_score", 0)
            if user not in user_max_risk or risk > user_max_risk[user]:
                user_max_risk[user] = risk
        
        top_users = sorted(user_max_risk.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "unique_users": len(users),
            "top_users": [{"user": u, "max_risk": r} for u, r in top_users]
        }
    
    @staticmethod
    def calculate_domain_stats(alerts: List[dict]) -> List[dict]:
        """Calculate top domains by frequency."""
        domain_counts = {}
        for a in alerts:
            domain = a.get("domain", "unknown")
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{"domain": d, "count": c} for d, c in top_domains]
    
    @staticmethod
    def calculate_average_risk(alerts: List[dict]) -> float:
        """Calculate average risk score."""
        scores = [a.get("risk_score", 0) for a in alerts]
        return round(sum(scores) / len(scores), 2) if scores else 0.0
    
    def get_stats(self, alerts: List[dict], time_range: str = "all") -> dict:
        """Get complete dashboard statistics."""
        # Apply time filter
        filtered_alerts = self.filter_by_time_range(alerts, time_range)
        total = len(filtered_alerts)
        
        if total == 0:
            return {
                "total_alerts": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "unique_users": 0,
                "avg_risk_score": 0.0,
                "top_domains": [],
                "top_users": [],
                "time_range": time_range
            }
        
        risk_counts = self.calculate_risk_counts(filtered_alerts)
        user_stats = self.calculate_user_stats(filtered_alerts)
        top_domains = self.calculate_domain_stats(filtered_alerts)
        avg_risk = self.calculate_average_risk(filtered_alerts)
        
        return {
            "total_alerts": total,
            **risk_counts,
            "unique_users": user_stats["unique_users"],
            "avg_risk_score": avg_risk,
            "top_domains": top_domains,
            "top_users": user_stats["top_users"],
            "time_range": time_range
        }


# Singleton instance
stats_service = StatsService()
