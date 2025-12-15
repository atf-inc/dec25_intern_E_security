"""
Real-time Behavior Analysis Monitor
Listens to Redis events and runs behavior analysis
"""

import redis
import json
import os
from behavior import BehaviorEngine

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
except ImportError:
    pass

# Use environment variable or fall back to localhost
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

print("\n" + "="*70)
print("BEHAVIOR ANALYSIS MONITOR")
print("="*70 + "\n")

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

# Initialize behavior engine
behavior_engine = BehaviorEngine(host=REDIS_HOST, port=REDIS_PORT)
print("✅ Behavior Engine initialized\n")

print("="*70)
print("🔄 Listening for events on 'events' channel...")
print("   Press Ctrl+C to stop\n")

# Subscribe to events
pubsub = redis_client.pubsub()
pubsub.subscribe("events")

event_count = 0
first_visit_count = 0
repeat_visit_count = 0