import redis
import json
import os
import app.core.config as settings

class RedisService:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.client = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)

    def publish(self, channel: str, message: dict):
        """Publish a message to a Redis channel."""
        self.client.publish(channel, json.dumps(message, default=str))

    def get_client(self):
        return self.client
