import redis
import json
import os
import collector.core.config as settings

class RedisService:
    def __init__(self):
        self.redis_host = settings.settings.REDIS_HOST
        self.redis_port = settings.settings.REDIS_PORT
        self.client = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)

    def publish(self, channel: str, message: dict):
        """Publish a message to a Redis channel."""
        self.client.publish(channel, json.dumps(message, default=str))

    def get_client(self):
        return self.client
