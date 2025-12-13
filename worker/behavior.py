import redis
import os

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
HISTORY_retention_SECONDS = 60 * 60 * 24 * 30  # Keep history for 30 days (optional)

class BehaviorEngine:
    def __init__(self, host=None, port=None):
        # Connect to the Redis service
        # Allow overriding for local testing
        _host = host if host else REDIS_HOST
        _port = port if port else REDIS_PORT
        self.r = redis.Redis(host=_host, port=_port, decode_responses=True)

    def analyze(self, user_id: str, domain: str) -> dict:
        try:
            user_key = f"history:{user_id}"

            # 1. Check if domain exists in the user's history set
            # sismember returns True if it exists, False if it doesn't.
            is_known_domain = self.r.sismember(user_key, domain)

            if is_known_domain:
                # Code Path: User has been here before.
                return {
                    "behavior_score": 0.0, # Safe / Normal
                    "is_first_visit": False,
                    "reason": "Domain found in user history"
                }
            
            else:
                # Code Path: First time visit!
                # 2. Add it to history so it isn't flagged next time
                self.r.sadd(user_key, domain)
                
                # (Optional) Set an expiry so Redis doesn't fill up forever
                self.r.expire(user_key, HISTORY_retention_SECONDS)

                return {
                    "behavior_score": 0.5, # Suspicious (Medium Risk)
                    "is_first_visit": True,
                    "reason": "First time user has visited this domain"
                }
        except Exception as e:
            # Fallback in case of Redis error
            return {
                "behavior_score": 0.0,
                "is_first_visit": False, 
                "reason": f"Analysis failed: {str(e)}"
            }