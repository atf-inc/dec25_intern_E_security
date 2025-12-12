import redis
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BehaviorEngine:
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 2):
       
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_client = None
        
        # Behavior analysis parameters
        self.history_days = 7  # How many days of history to maintain
        self.min_visits_for_familiarity = 3  # Minimum visits to consider domain familiar
        self.time_window_hours = 24  # Time window for frequency analysis
        
        self._connect_redis()
    
    def _connect_redis(self):
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}/{self.redis_db}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            self.redis_client = None
    
    def _get_user_key(self, user_id: str) -> str:
        """Generate Redis key for user data."""
        return f"behavior:user:{user_id}"
    
    def _get_domain_key(self, user_id: str, domain: str) -> str:
        """Generate Redis key for user-domain data."""
        return f"behavior:user:{user_id}:domain:{domain}"
    
    def _store_user_activity(self, user_id: str, domain: str, timestamp: str, upload_size: int = 0):
        """Store user activity in Redis."""
        if not self.redis_client:
            return
        
        try:
            # Store in user's activity list
            user_key = self._get_user_key(user_id)
            activity_data = {
                'domain': domain,
                'timestamp': timestamp,
                'upload_size': upload_size
            }
            
            # Add to user's activity stream (as JSON string)
            self.redis_client.lpush(user_key, json.dumps(activity_data))
            
            # Keep only recent activities (limit to prevent memory bloat)
            self.redis_client.ltrim(user_key, 0, 999)  # Keep last 1000 activities
            
            # Set expiration for user data (cleanup old users)
            self.redis_client.expire(user_key, self.history_days * 24 * 3600)
            
            # Store domain-specific data
            domain_key = self._get_domain_key(user_id, domain)
            domain_data = {
                'first_visit': timestamp,
                'last_visit': timestamp,
                'visit_count': 1,
                'total_upload_size': upload_size
            }
            
            # Check if domain data already exists
            existing_data = self.redis_client.get(domain_key)
            if existing_data:
                existing = json.loads(existing_data)
                domain_data = {
                    'first_visit': existing['first_visit'],  # Keep original first visit
                    'last_visit': timestamp,
                    'visit_count': existing['visit_count'] + 1,
                    'total_upload_size': existing['total_upload_size'] + upload_size
                }
            
            self.redis_client.set(domain_key, json.dumps(domain_data))
            self.redis_client.expire(domain_key, self.history_days * 24 * 3600)
            
        except Exception as e:
            logger.error(f"Failed to store user activity: {e}")
    
    def _get_user_domain_history(self, user_id: str, domain: str) -> Optional[Dict[str, Any]]:
        """Get user's history for a specific domain."""
        if not self.redis_client:
            return None
        
        try:
            domain_key = self._get_domain_key(user_id, domain)
            data = self.redis_client.get(domain_key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user domain history: {e}")
            return None
    
    def _get_user_recent_activity(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get user's recent activity within specified hours."""
        if not self.redis_client:
            return []
        
        try:
            user_key = self._get_user_key(user_id)
            activities = self.redis_client.lrange(user_key, 0, -1)
            
            # Filter by time window
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_activities = []
            
            for activity_json in activities:
                try:
                    activity = json.loads(activity_json)
                    activity_time = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
                    
                    if activity_time.replace(tzinfo=None) > cutoff_time:
                        recent_activities.append(activity)
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse activity: {e}")
                    continue
            
            return recent_activities
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []
    
    def _analyze_first_time_visit(self, user_id: str, domain: str) -> Tuple[bool, str]:
        """Check if this is user's first time visiting the domain."""
        domain_history = self._get_user_domain_history(user_id, domain)
        
        if not domain_history or domain_history.get('visit_count', 0) <= 1:
            return True, f"First time visit to {domain}"
        
        return False, f"Familiar domain (visited {domain_history.get('visit_count', 0)} times)"
    
    def _analyze_frequency_anomaly(self, user_id: str, domain: str) -> Tuple[bool, str]:
        """Check for unusual frequency patterns."""
        recent_activities = self._get_user_recent_activity(user_id, self.time_window_hours)
        
        if not recent_activities:
            return False, "No recent activity"
        
        # Count visits to this domain in recent window
        domain_visits = [a for a in recent_activities if a['domain'] == domain]
        visit_count = len(domain_visits)
        
        # Check for unusual frequency (more than 10 visits in 24 hours might be suspicious)
        if visit_count > 10:
            return True, f"High frequency access: {visit_count} visits in {self.time_window_hours}h"
        
        # Check for burst activity (multiple visits in short time)
        if len(domain_visits) >= 3:
            timestamps = [datetime.fromisoformat(v['timestamp'].replace('Z', '+00:00')) 
                         for v in domain_visits[:3]]
            timestamps.sort()
            
            # If 3 visits within 1 hour
            if (timestamps[-1] - timestamps[0]).total_seconds() < 3600:
                return True, "Burst activity detected: 3+ visits within 1 hour"
        
        return False, f"Normal frequency: {visit_count} visits"
    
    def _analyze_unusual_timing(self, timestamp: str) -> Tuple[bool, str]:
        """Check for unusual access timing (e.g., outside business hours)."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            
            # Consider 10 PM - 6 AM as unusual hours (adjust as needed)
            if hour >= 22 or hour <= 6:
                return True, f"Unusual timing: {hour:02d}:xx (outside business hours)"
            
            return False, f"Normal timing: {hour:02d}:xx"
            
        except ValueError:
            return False, "Invalid timestamp"
    
    def analyze(self, log_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user behavior for the log event.
        
        Args:
            log_event: Dictionary containing 'user_id', 'domain', 'ts', etc.
            
        Returns:
            Dictionary with behavior analysis results
        """
        user_id = log_event.get('user_id', 'unknown')
        domain = log_event.get('domain', '')
        timestamp = log_event.get('ts', '')
        upload_size = log_event.get('upload_size_bytes', 0)
        
        # Store this activity for future analysis
        self._store_user_activity(user_id, domain, timestamp, upload_size)
        
        alerts = []
        explanations = []
        score = 0.0
        
        # Analysis 1: First time visit
        is_first_visit, explanation = self._analyze_first_time_visit(user_id, domain)
        if is_first_visit:
            alerts.append('first_time_visit')
            explanations.append(explanation)
            score += 0.4  # Medium risk for first time visits
        else:
            explanations.append(explanation)
        
        # Analysis 2: Frequency anomaly
        is_frequent, explanation = self._analyze_frequency_anomaly(user_id, domain)
        if is_frequent:
            alerts.append('frequency_anomaly')
            explanations.append(explanation)
            score += 0.5  # Medium-high risk for suspicious frequency
        else:
            explanations.append(explanation)
        
        # Analysis 3: Unusual timing
        is_unusual_time, explanation = self._analyze_unusual_timing(timestamp)
        if is_unusual_time:
            alerts.append('unusual_timing')
            explanations.append(explanation)
            score += 0.3  # Low-medium risk for unusual timing
        else:
            explanations.append(explanation)
        
        # Get domain history for additional context
        domain_history = self._get_user_domain_history(user_id, domain)
        
        # Cap score at 1.0
        final_score = min(score, 1.0)
        
        return {
            'behavior_score': final_score,
            'behavior_alerts': alerts,
            'behavior_explanations': explanations,
            'domain_history': domain_history,
            'is_first_visit': is_first_visit
        }

# Test function
def test_behavior_engine():
    """Test the behavior engine with sample data."""
    try:
        engine = BehaviorEngine()
        
        # Simulate some user activity
        test_logs = [
            {
                'user_id': 'alice@company.com',
                'domain': 'github.com',
                'ts': '2025-12-12T10:30:00Z',
                'upload_size_bytes': 1024
            },
            {
                'user_id': 'alice@company.com',
                'domain': 'stealth-ai-writer.io',
                'ts': '2025-12-12T23:45:00Z',  # Late night
                'upload_size_bytes': 5242880
            },
            {
                'user_id': 'bob@company.com',
                'domain': 'github.com',
                'ts': '2025-12-12T14:20:00Z',
                'upload_size_bytes': 2048
            }
        ]
        
        for i, log in enumerate(test_logs, 1):
            print(f"\nTest {i}: {log['user_id']} -> {log['domain']}")
            result = engine.analyze(log)
            print(f"Score: {result['behavior_score']}")
            print(f"Alerts: {result['behavior_alerts']}")
            print(f"Explanations: {result['behavior_explanations']}")
            print(f"First visit: {result['is_first_visit']}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_behavior_engine()